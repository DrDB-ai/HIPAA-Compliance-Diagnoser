import pyodbc
from .db_connector import DBConnector


class SQLServerConnector(DBConnector):
    def connect(self, host, port, database, username, password):
        return pyodbc.connect(
            f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={host},{port};DATABASE={database};UID={username};PWD={password};TrustServerCertificate=yes;'
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
        cursor.execute("""
            SELECT 
                OBJECT_NAME(major_id) AS object_name,
                permission_name,
                state_desc
            FROM 
                sys.database_permissions 
            WHERE 
                grantee_principal_id = USER_ID('PUBLIC')
                AND OBJECT_SCHEMA_NAME(major_id) NOT IN ('sys', 'information_schema') -- Exclude system schemas
                AND OBJECT_NAME(major_id) NOT LIKE 'spt!_%%' ESCAPE '!' -- Exclude objects starting with 'spt_'
        """)
        return cursor.fetchall()

    def check_audit_trail(self, cursor):
        cursor.execute(
            "SELECT COUNT(*) FROM sys.server_audits WHERE is_state_enabled = 1")
        return cursor.fetchone()[0] > 0

    def check_encryption(self, cursor):
        cursor.execute("SELECT name FROM sys.databases WHERE is_encrypted = 1")
        encrypted_databases = cursor.fetchall()
        return len(encrypted_databases) > 0

    def check_activity_monitoring(self, cursor):
        cursor.execute("SELECT CASE WHEN OBJECT_ID('sys.dm_exec_requests') IS NOT NULL AND (SELECT value_in_use FROM sys.configurations WHERE name = 'default trace enabled') = 1 THEN 1 ELSE 0 END AS activity_monitoring_enabled")
        return cursor.fetchone()[0]

    def get_description(self):
        return {
            "Sensitive Data Scan": {
                "description": "This check scans the database for columns containing sensitive data related to patients, such as names, addresses, or medical history.",
                "details": "The scan is performed by querying the 'INFORMATION_SCHEMA.COLUMNS' system view."
            },
            "Access Control Check": {
                "description": "This check examines the database's access controls to ensure that only authorized users have access to patient data.",
                "details": "The access control check queries the 'sys.database_permissions' system view to verify the permissions granted to the current user."
            },
            "Audit Trail Check": {
                "description": "This check verifies the existence of an audit trail mechanism in the database to track access and modifications to patient data.",
                "details": "The audit trail check queries the 'sys.server_audits' system view to count the number of active audit trails where the state is enabled."
            },
            "Encryption Check": {
                "description": "This check verifies if encryption is enabled in the SQL Server database.",
                "details": "The encryption check queries the 'sys.databases' system view to identify databases where encryption is enabled."
            },
            "Database Activity Monitoring Check": {
                "description": "This check verifies if database activity monitoring is enabled in the SQL Server database.",
                "details": "The activity monitoring check queries system views like 'sys.dm_exec_requests' and 'sys.configurations' to determine if the required components for activity monitoring are enabled."
            }
        }