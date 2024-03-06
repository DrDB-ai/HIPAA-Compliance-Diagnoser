import psycopg2
from .db_connector import DBConnector 


class PostgreSQLConnector(DBConnector):
    def connect(self, host, port, database, username, password):
        return psycopg2.connect(
            dbname=database,
            user=username,
            password=password,
            host=host,
            port=port
        )

    def scan_for_sensitive_data(self, cursor):
        cursor.execute(
            "SELECT table_name, column_name FROM information_schema.columns WHERE column_name ILIKE '%patient%' AND TABLE_NAME != 'pg_hba_file_rules'")
        sensitive_data = cursor.fetchall()

        additional_terms = ["medical condition", "ssn", "dob", "address", "phone number", "email address",
                            "medical procedure", "healthcare provider", "medication name", "insurance information",
                            "lab result", "genetic information", "payment information"]
        for term in additional_terms:
            cursor.execute(
                f"SELECT table_name, column_name FROM information_schema.columns WHERE column_name ILIKE '%{term}%' AND TABLE_NAME != 'pg_hba_file_rules'")
            sensitive_data.extend(cursor.fetchall())

        return sensitive_data

    def check_access_controls(self, cursor):
        cursor.execute(
            "SELECT grantee, privilege_type FROM information_schema.role_table_grants WHERE grantee='PUBLIC'")
        return cursor.fetchall()

    def check_audit_trail(self, cursor):
        cursor.execute(
            "SELECT setting FROM pg_settings WHERE name = 'log_statement'")
        log_statement_setting = cursor.fetchone()[0]
        return log_statement_setting == 'all'

    def check_encryption(self, cursor):
        cursor.execute("SELECT * FROM pg_extension WHERE extname = 'pgcrypto'")
        return cursor.fetchone() is not None

    def check_activity_monitoring(self, cursor):
        cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM information_schema.views WHERE table_name = 'pg_stat_activity')")
        return cursor.fetchone()[0]

    def get_description(self):
        return {
            "Sensitive Data Scan": {
                "description": "This check scans the database for columns containing sensitive data related to patients, such as names, addresses, or medical history.",
                "details": "The scan is performed by querying the 'information_schema.columns' system view."
            },
            "Access Control Check": {
                "description": "This check examines the database's access controls to ensure that only authorized users have access to patient data.",
                "details": "The access control check queries the 'information_schema.role_table_grants' system view to verify the privileges granted to roles."
            },
            "Audit Trail Check": {
                "description": "This check verifies the existence of an audit trail mechanism in the database to track access and modifications to patient data.",
                "details": "The audit trail check queries the 'pg_settings' system view to ensure that logging mechanisms are in place."
            },
            "Encryption Check": {
                "description": "This check verifies if encryption is enabled in the PostgreSQL database.",
                "details": "The encryption check queries the 'pg_extension' system view to determine the presence of the 'pgcrypto' extension, indicating encryption functionality."
            },
            "Database Activity Monitoring Check": {
                "description": "This check verifies if database activity monitoring is enabled in the PostgreSQL database.",
                "details": "The database activity monitoring check queries the 'information_schema.views' system view to determine if the 'pg_stat_activity' view exists, indicating the presence of activity monitoring functionality."
            }
        }