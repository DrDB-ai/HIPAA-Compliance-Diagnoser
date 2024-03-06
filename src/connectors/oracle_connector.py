import cx_Oracle
from .db_connector import DBConnector


class OracleConnector(DBConnector):
    def connect(self, host, port, database, username, password):
        return cx_Oracle.connect(
            f"{username}/{password}@{host}:{port}/{database}"
        )

    def scan_for_sensitive_data(self, cursor):
        cursor.execute("""
            SELECT TABLE_NAME, COLUMN_NAME 
            FROM ALL_TAB_COLUMNS 
            WHERE COLUMN_NAME LIKE '%PATIENT%'
            AND OWNER NOT IN ('SYS', 'SYSTEM', 'XDB', 'DBSNMP', 'APEX_040000', 'OUTLN', 'CTXSYS', 'WMSYS', 'ORDSYS', 'ORDPLUGINS', 'MDSYS', 'FLOWS_030000', 'ORACLE_OCM', 'APEX_PUBLIC_USER', 'ANONYMOUS', 'DIP', 'ORDDATA', 'XDBEXT', 'APEX_030200')
            AND TABLE_NAME NOT LIKE 'BIN$%'
            AND TABLE_NAME NOT LIKE 'SYS_%'
            AND TABLE_NAME NOT LIKE 'APEX%'
            AND TABLE_NAME NOT LIKE 'DR$%'
            AND TABLE_NAME NOT LIKE 'AQ$%'
            AND TABLE_NAME NOT IN ('CONTAINER_DATABASE', 'DATABASE', 'CHANGE_LOG_QUEUE_TABLE')
        """)
        sensitive_data = cursor.fetchall()

        additional_terms = ["MEDICAL CONDITION", "SSN", "DOB", "ADDRESS", "PHONE NUMBER", "EMAIL ADDRESS",
                            "MEDICAL PROCEDURE", "HEALTHCARE PROVIDER", "MEDICATION NAME", "INSURANCE INFORMATION",
                            "LAB RESULT", "GENETIC INFORMATION", "PAYMENT INFORMATION"]
        for term in additional_terms:
            cursor.execute(
                f"""
                SELECT TABLE_NAME, COLUMN_NAME 
                FROM ALL_TAB_COLUMNS 
                WHERE COLUMN_NAME LIKE '%{term}%'
                AND OWNER NOT IN ('SYS', 'SYSTEM', 'XDB', 'DBSNMP', 'APEX_040000', 'OUTLN', 'CTXSYS', 'WMSYS', 'ORDSYS', 'ORDPLUGINS', 'MDSYS', 'FLOWS_030000', 'ORACLE_OCM', 'APEX_PUBLIC_USER', 'ANONYMOUS', 'DIP', 'ORDDATA', 'XDBEXT', 'APEX_030200')
                AND TABLE_NAME NOT LIKE 'BIN$%'
                AND TABLE_NAME NOT LIKE 'SYS_%'
                AND TABLE_NAME NOT LIKE 'APEX%'
                AND TABLE_NAME NOT LIKE 'DR$%'
                AND TABLE_NAME NOT LIKE 'AQ$%'
                AND TABLE_NAME NOT IN ('CONTAINER_DATABASE', 'DATABASE', 'CHANGE_LOG_QUEUE_TABLE')
                """
            )
            sensitive_data.extend(cursor.fetchall())

        return sensitive_data

    def check_access_controls(self, cursor):
        cursor.execute("""
            SELECT table_name, grantee, privilege 
            FROM dba_tab_privs 
            WHERE grantee = 'PUBLIC' 
            AND owner NOT IN ('OLAPSYS', 'DVSYS', 'DVF', 'LBACSYS', 'GSMADMIN_INTERNAL', 'SYS', 'SYSTEM', 'XDB', 'DBSNMP', 'APEX_040000', 'OUTLN', 'CTXSYS', 'WMSYS', 'ORDSYS', 'ORDPLUGINS', 'MDSYS', 'FLOWS_030000', 'ORACLE_OCM', 'APEX_PUBLIC_USER', 'ANONYMOUS', 'DIP', 'ORDDATA', 'XDBEXT', 'APEX_030200')
        """)
        return cursor.fetchall()

    def check_audit_trail(self, cursor):
        cursor.execute(
            "SELECT CASE WHEN value IS NOT NULL THEN 'true' ELSE 'false' END AS audit_enabled FROM v$parameter WHERE name = 'audit_trail'")
        return cursor.fetchone()[0]

    def check_encryption(self, cursor):
        cursor.execute("SELECT value FROM v$parameter WHERE name = 'encrypt_new_tablespaces'")
        result = cursor.fetchone()
        if result:
            return result[0] in ['CLOUD_ONLY', 'ALWAYS', 'DDL']
        else:
            return False

    def check_activity_monitoring(self, cursor):
        cursor.execute("SELECT CASE WHEN (SELECT value FROM v$parameter WHERE name = 'statistics_level') IN ('TYPICAL', 'ALL') AND (SELECT value FROM v$parameter WHERE name = 'control_management_pack_access') = 'DIAGNOSTIC+TUNING' THEN 1 ELSE 0 END AS activity_monitoring_enabled FROM dual")
        return cursor.fetchone()[0]

    def get_description(self):
        return {
            "Sensitive Data Scan": {
                "description": "This check scans the database for columns containing sensitive data related to patients, such as names, addresses, or medical history.",
                "details": "The scan is performed by querying the 'ALL_TAB_COLUMNS' system view."
            },
            "Access Control Check": {
                "description": "This check examines the database's access controls to ensure that only authorized users have access to patient data.",
                "details": "The access control check queries the 'DBA_TAB_PRIVS' view to verify the privileges granted to users or roles on specific tables. This view provides information about table-level privileges granted to users and roles in the database. By examining the privileges granted to public users or roles ('PUBLIC' grantee), this check ensures that any overly permissive access controls are identified and remediated."
            },
            "Audit Trail Check": {
                "description": "This check verifies the existence of an audit trail mechanism in the Oracle database to track access and modifications to patient data.",
                "details": "The audit trail check queries the 'v$parameter' system view to determine if the 'audit_trail' parameter is set, indicating the presence of audit trail functionality."
            },
            "Encryption Check": {
                "description": "This check verifies if encryption is enabled in the Oracle database.",
                "details": "The encryption check queries the 'SELECT value FROM v$parameter WHERE name = 'encrypt_new_tablespaces'' statement to determine if tablespace encryption is enabled."
            },
            "Database Activity Monitoring Check": {
                "description": "This check verifies if activity monitoring is enabled in the Oracle database.",
                "details": "The activity monitoring check queries system views such as 'v$parameter' to determine if the necessary parameters related to activity monitoring, such as 'statistics_level' and 'control_management_pack_access', are set to appropriate values, indicating the presence of activity monitoring functionality."
            }
        }