import mysql.connector
from .db_connector import DBConnector


class MySQLConnector(DBConnector):
    def connect(self, host, port, database, username, password):
        return mysql.connector.connect(
            host=host,
            user=username,
            password=password,
            database=database,
            port=port
        )

    def scan_for_sensitive_data(self, cursor):
        cursor.execute(
            "SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE COLUMN_NAME LIKE '%patient%'")
        sensitive_data = cursor.fetchall()

        additional_terms = ["medical condition", "ssn", "dob", "address", "phone number", "email address",
                            "medical procedure", "healthcare provider", "medication name", "insurance information",
                            "lab result", "genetic information", "payment information"]
        for term in additional_terms:
            cursor.execute(
                f"SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE COLUMN_NAME LIKE '%{term}%'")
            sensitive_data.extend(cursor.fetchall())

        return sensitive_data

    def check_access_controls(self, cursor):
        cursor.execute(
            "SELECT grantee, privilege_type FROM information_schema.USER_PRIVILEGES WHERE grantee='PUBLIC'")
        return cursor.fetchall()

    def check_audit_trail(self, cursor):
        cursor.execute("SELECT IF(VERSION() LIKE '%Enterprise%', IF((SELECT COUNT(*) FROM information_schema.plugins WHERE plugin_name = 'audit_log' AND plugin_status = 'ACTIVE') > 0, 'true', 'false'), 'false') AS audit_log_enabled")
        return bool(cursor.fetchone()[0])

    def check_encryption(self, cursor):
        cursor.execute("SHOW VARIABLES LIKE 'have_ssl'")
        ssl_status = cursor.fetchone()[1]
        return ssl_status == "YES"

    def check_activity_monitoring(self, cursor):
        cursor.execute(
            "SELECT @@general_log = 1 AND @@slow_query_log = 1 AND @@performance_schema = 1 AS result")
        return bool(cursor.fetchone()[0])

    def get_description(self):
        return {
            "Sensitive Data Scan": {
                "description": "This check scans the database for columns containing sensitive data related to patients, such as names, addresses, or medical history.",
                "details": "The scan is performed by querying the 'information_schema.columns' system view."
            },
            "Access Control Check": {
                "description": "This check examines the database's access controls to ensure that only authorized users have access to patient data.",
                "details": "The access control check queries the 'information_schema.role_table_grants' table to retrieve the permissions granted to the 'PUBLIC' role."
            },
            "Audit Trail Check": {
                "description": "This check verifies the existence of an audit trail mechanism in the database to track access and modifications to patient data.",
                "details": "The audit trail checks if the audit_log plugin is enabled. This check is only enabled for MySQL Enterprise."
            },
            "Encryption Check": {
                "description": "This check verifies if encryption is enabled in the MySQL database.",
                "details": "The encryption check queries the 'SHOW VARIABLES LIKE 'have_ssl'' statement to determine if SSL is enabled, indicating encryption functionality."
            },
            "Database Activity Monitoring Check": {
                "description": "This check verifies if database activity monitoring is enabled in the MySQL database.",
                "details": "The database activity monitoring checks that 'general_log', 'slow_query_log', and 'performance_schema' are enabled, indicating the presence of activity monitoring functionality."
            }
        }
