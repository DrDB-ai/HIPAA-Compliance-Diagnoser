import ibm_db
import ibm_db_dbi
from .db_connector import DBConnector


class DB2Connector(DBConnector):
    def connect(self, host, port, database, username, password):
        return ibm_db_dbi.Connection(ibm_db.connect(
            f"DATABASE={database};HOSTNAME={host};PORT={port};PROTOCOL=TCPIP;UID={username};PWD={password};",
            "", ""
        ))

    def scan_for_sensitive_data(self, cursor):
        cursor.execute(
            "SELECT TABSCHEMA, TABNAME, COLNAME FROM SYSCAT.COLUMNS WHERE COLNAME LIKE '%PATIENT%' AND TABSCHEMA NOT LIKE 'SYS%' AND TABNAME NOT LIKE 'SYS%'")
        sensitive_data = cursor.fetchall()

        additional_terms = ["MEDICAL CONDITION", "SSN", "DOB", "ADDRESS", "PHONE NUMBER", "EMAIL ADDRESS",
                            "MEDICAL PROCEDURE", "HEALTHCARE PROVIDER", "MEDICATION NAME", "INSURANCE INFORMATION",
                            "LAB RESULT", "GENETIC INFORMATION", "PAYMENT INFORMATION"]
        for term in additional_terms:
            cursor.execute(
                f"SELECT TABSCHEMA, TABNAME, COLNAME FROM SYSCAT.COLUMNS WHERE COLNAME LIKE '%{term}%' AND TABSCHEMA NOT LIKE 'SYS%' AND TABNAME NOT LIKE 'SYS%'")
            sensitive_data.extend(cursor.fetchall())

        return sensitive_data

    def check_access_controls(self, cursor):
        cursor.execute(
            "SELECT GRANTEETYPE, TABNAME  FROM SYSCAT.TABAUTH WHERE TABSCHEMA NOT LIKE 'SYS%' AND TABNAME NOT LIKE 'SYS%'")
        return cursor.fetchall()

    def check_audit_trail(self, cursor):
        cursor.execute("SELECT CASE WHEN COUNT(*) > 0 THEN 1 ELSE 0 END AS has_audit_policy FROM SYSCAT.AUDITPOLICIES")
        result = cursor.fetchone()
        return bool(result[0])

    def check_encryption(self, cursor):
        cursor.execute("""
            SELECT CASE WHEN COUNT(*) > 0 THEN 1 ELSE 0 END AS encryption_enabled
            FROM TABLE (SYSPROC.ADMIN_GET_ENCRYPTION_INFO()) AS ENCRYPTION_INFO
            WHERE ALGORITHM IS NOT NULL
        """)
        result = cursor.fetchone()
        return bool(result[0])

    def check_activity_monitoring(self, cursor):
        cursor.execute("SELECT CASE WHEN COUNT(*) > 0 THEN 1 ELSE 0 END AS activity_monitoring_enabled FROM SYSIBM.SYSTABLES WHERE NAME LIKE 'ACTIVITYSTMT_%'")
        return cursor.fetchone()[0]

    def get_description(self):
        return {
            "Sensitive Data Scan": {
                "description": "This check scans the database for columns containing sensitive data related to patients, such as names, addresses, or medical history.",
                "details": "The scan is performed by querying the 'SYSCAT.COLUMNS' system view."
            },
            "Access Control Check": {
                "description": "This check examines the database's access controls to ensure that only authorized users have access to patient data.",
                "details": "The access control check queries the SYSCAT.TABAUTH system catalog to retrieve information about table-level privileges granted to various users or roles. It excludes tables with schema names starting with 'SYS' and tables with names starting with 'SYS' to filter out system tables. This ensures that only user-defined tables are considered for access control verification."
            },
            "Audit Policy Check": {
                "description": "This check verifies whether any audit policies are configured in the DB2 database.",
                "details": "The check executes a SQL query against the SYSCAT.AUDITPOLICIES system catalog table to determine the presence of audit policies. If any audit policies are found, the function returns True; otherwise, it returns False."
            },
            "Encryption Check": {
                "description": "This check verifies if encryption is enabled in the DB2 database.",
                "details": "The encryption check queries the 'SELECT CASE WHEN COUNT(*) > 0 THEN 1 ELSE 0 END AS encryption_enabled FROM TABLE (SYSPROC.ADMIN_GET_ENCRYPTION_INFO()) AS ENCRYPTION_INFO WHERE ALGORITHM IS NOT NULL' statement to determine if encryption is enabled at the database level. It counts the number of rows returned where the ALGORITHM column is not null, indicating that encryption is enabled. If any such rows are found, the function returns True; otherwise, it returns False."
            },
            "Database Activity Monitoring Check": {
                "description": "This check verifies if activity monitoring is enabled in the DB2 database.",
                "details": "The activity monitoring check queries the 'SYSIBM.SYSTABLES' system catalog to determine if tables with names starting with 'ACTIVITYSTMT_' exist, which indicates that activity monitoring is enabled."
            }
        }