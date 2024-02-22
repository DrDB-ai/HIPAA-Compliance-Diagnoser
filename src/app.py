import streamlit as st
import psycopg2
import mysql.connector
import pyodbc
import ibm_db
import cx_Oracle

st.set_page_config(page_title="Dr DB HIPAA Compliance Check", layout="wide")

st.markdown("""
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
""", unsafe_allow_html=True)


# Define base class for database connectors
class DBConnector:

    def connect(self, host, port, database, username, password):
        raise NotImplementedError("connect method must be implemented by subclasses")

    def scan_for_sensitive_data(self, cursor):
        raise NotImplementedError("scan_for_sensitive_data method must be implemented by subclasses")

    def check_access_controls(self, cursor):
        raise NotImplementedError("check_access_controls method must be implemented by subclasses")

    def check_audit_trail(self, cursor):
        raise NotImplementedError("check_audit_trail method must be implemented by subclasses")

    def check_encryption(self, cursor):
        raise NotImplementedError("check_encryption method must be implemented by subclasses")

    def check_activity_monitoring(self, cursor):
        raise NotImplementedError("check_activity_monitoring method must be implemented by subclasses")

    def get_description(self):
        raise NotImplementedError("get_description method must be implemented by subclasses")


# Define PostgreSQL connector
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
        cursor.execute("SELECT table_name, column_name FROM information_schema.columns WHERE column_name ILIKE '%patient%' AND TABLE_NAME != 'pg_hba_file_rules'")
        sensitive_data = cursor.fetchall()

        additional_terms = ["medical condition", "ssn", "dob", "address", "phone number", "email address",
                            "medical procedure", "healthcare provider", "medication name", "insurance information",
                            "lab result", "genetic information", "payment information"]
        for term in additional_terms:
            cursor.execute(f"SELECT table_name, column_name FROM information_schema.columns WHERE column_name ILIKE '%{term}%' AND TABLE_NAME != 'pg_hba_file_rules'")
            sensitive_data.extend(cursor.fetchall())

        return sensitive_data

    def check_access_controls(self, cursor):
        cursor.execute("SELECT grantee, privilege_type FROM information_schema.role_table_grants WHERE grantee='PUBLIC'")
        return cursor.fetchall()

    def check_audit_trail(self, cursor):
        cursor.execute("SELECT setting FROM pg_settings WHERE name = 'log_statement'")
        log_statement_setting = cursor.fetchone()[0]
        return log_statement_setting == 'all'

    def check_encryption(self, cursor):
        cursor.execute("SELECT * FROM pg_extension WHERE extname = 'pgcrypto'")
        return cursor.fetchone() is not None

    def check_activity_monitoring(self, cursor):
        cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.views WHERE table_name = 'pg_stat_activity')")
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


# Define MySQL connector
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
        cursor.execute("SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE COLUMN_NAME LIKE '%patient%'")
        sensitive_data = cursor.fetchall()

        additional_terms = ["medical condition", "ssn", "dob", "address", "phone number", "email address",
                            "medical procedure", "healthcare provider", "medication name", "insurance information",
                            "lab result", "genetic information", "payment information"]
        for term in additional_terms:
            cursor.execute(f"SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE COLUMN_NAME LIKE '%{term}%'")
            sensitive_data.extend(cursor.fetchall())

        return sensitive_data

    def check_access_controls(self, cursor):
        cursor.execute("SHOW GRANTS FOR CURRENT_USER()")
        return cursor.fetchall()

    def check_audit_trail(self, cursor):
        cursor.execute("SELECT IF(VERSION() LIKE '%Enterprise%', IF((SELECT COUNT(*) FROM information_schema.plugins WHERE plugin_name = 'audit_log' AND plugin_status = 'ACTIVE') > 0, 'true', 'false'), 'false') AS audit_log_enabled")
        return bool(cursor.fetchone()[0])

    def check_encryption(self, cursor):
        cursor.execute("SHOW VARIABLES LIKE 'have_ssl'")
        ssl_status = cursor.fetchone()[1]
        return ssl_status == "YES"

    def check_activity_monitoring(self, cursor):
        cursor.execute("SELECT @@general_log = 1 AND @@slow_query_log = 1 AND @@performance_schema = 1 AS result")
        return bool(cursor.fetchone()[0])

    def get_description(self):
        return {
            "Sensitive Data Scan": {
                "description": "This check scans the database for columns containing sensitive data related to patients, such as names, addresses, or medical history.",
                "details": "The scan is performed by querying the 'information_schema.columns' system view."
            },
            "Access Control Check": {
                "description": "This check examines the database's access controls to ensure that only authorized users have access to patient data.",
                "details": "The access control check queries the 'SHOW GRANTS' statement to retrieve the permissions granted to the current user."
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


# Define SQL Server connector
class SQLServerConnector(DBConnector):
    def connect(self, host, port, database, username, password):
        return pyodbc.connect(
            f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={host},{port};DATABASE={database};UID={username};PWD={password}'
        )

    def scan_for_sensitive_data(self, cursor):
        cursor.execute("SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE COLUMN_NAME LIKE '%patient%'")
        sensitive_data = cursor.fetchall()

        additional_terms = ["medical condition", "ssn", "dob", "address", "phone number", "email address",
                            "medical procedure", "healthcare provider", "medication name", "insurance information",
                            "lab result", "genetic information", "payment information"]
        for term in additional_terms:
            cursor.execute(f"SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE COLUMN_NAME LIKE '%{term}%'")
            sensitive_data.extend(cursor.fetchall())

        return sensitive_data

    def check_access_controls(self, cursor):
        cursor.execute("SELECT permission_name, state_desc FROM sys.database_permissions WHERE grantee_principal_id = USER_ID()")
        return cursor.fetchall()

    def check_audit_trail(self, cursor):
        cursor.execute("SELECT is_trustworthy_on FROM sys.databases WHERE name = DB_NAME()")
        return cursor.fetchone()[0]

    def check_encryption(self, cursor):
        cursor.execute("SELECT name FROM sys.databases WHERE is_encrypted = 1")
        encrypted_databases = cursor.fetchall()
        return len(encrypted_databases) > 0

    def check_activity_monitoring(self, cursor):
        cursor.execute("SELECT OBJECT_ID('sys.dm_exec_requests')")
        return cursor.fetchone() is not None

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
                "details": "The audit trail check queries the 'sys.databases' system view to check the 'is_trustworthy_on' property."
            },
            "Encryption Check": {
                "description": "This check verifies if encryption is enabled in the SQL Server database.",
                "details": "The encryption check queries the 'sys.dm_database_encryption_keys' system view to determine if any database encryption keys are present, indicating encryption functionality."
            },
            "Database Activity Monitoring Check": {
                "description": "This check verifies if database activity monitoring is enabled in the SQL Server database.",
                "details": "The database activity monitoring check queries the 'sys.dm_exec_sessions' system view to determine if session information is accessible, indicating the presence of activity monitoring functionality."
            }
        }


# Define DB2 connector
class DB2Connector(DBConnector):
    def connect(self, host, port, database, username, password):
        return ibm_db.connect(
            f"DATABASE={database};HOSTNAME={host};PORT={port};PROTOCOL=TCPIP;UID={username};PWD={password};",
            "", ""
        )

    def scan_for_sensitive_data(self, cursor):
        cursor.execute("SELECT TABSCHEMA, TABNAME, COLNAME FROM SYSCAT.COLUMNS WHERE COLNAME LIKE '%PATIENT%'")
        sensitive_data = cursor.fetchall()

        additional_terms = ["MEDICAL CONDITION", "SSN", "DOB", "ADDRESS", "PHONE NUMBER", "EMAIL ADDRESS",
                            "MEDICAL PROCEDURE", "HEALTHCARE PROVIDER", "MEDICATION NAME", "INSURANCE INFORMATION",
                            "LAB RESULT", "GENETIC INFORMATION", "PAYMENT INFORMATION"]
        for term in additional_terms:
            cursor.execute(f"SELECT TABSCHEMA, TABNAME, COLNAME FROM SYSCAT.COLUMNS WHERE COLNAME LIKE '%{term}%'")
            sensitive_data.extend(cursor.fetchall())

        return sensitive_data

    def check_access_controls(self, cursor):
        cursor.execute("SELECT authid, objectname FROM syscat.tabauth WHERE authid=CURRENT_USER")
        return cursor.fetchall()

    def check_audit_trail(self, cursor):
        return False  # DB2 does not have a built-in audit trail feature

    def check_encryption(self, cursor):
        cursor.execute("SELECT DBMS_INFO.TBSPACE_ENCRYPT FROM SYSIBMADM.ENV_INST_INFO")
        return cursor.fetchone()[0] == "YES"

    def check_activity_monitoring(self, cursor):
        cursor.execute("SELECT EXISTS (SELECT 1 FROM SYSIBMADM.SNAPAPPL)")
        return cursor.fetchone()[0]

    def get_description(self):
        return {
            "Sensitive Data Scan": {
                "description": "This check scans the database for columns containing sensitive data related to patients, such as names, addresses, or medical history.",
                "details": "The scan is performed by querying the 'SYSCAT.COLUMNS' system view."
            },
            "Access Control Check": {
                "description": "This check examines the database's access controls to ensure that only authorized users have access to patient data.",
                "details": "The access control check queries the 'SYSIBM.SYSTABAUTH' system view to verify the permissions granted to the current user."
            },
            "Audit Trail Check": {
                "description": "DB2 does not have a built-in audit trail feature. Consider implementing a custom solution or using third-party tools/plugins."
            },
            "Encryption Check": {
                "description": "This check verifies if encryption is enabled in the DB2 database.",
                "details": "The encryption check queries the 'SELECT DBMS_INFO.TBSPACE_ENCRYPT FROM SYSIBMADM.ENV_INST_INFO' statement to determine if tablespace encryption is enabled."
            },
            "Database Activity Monitoring Check": {
                "description": "DB2 does not have a built-in database activity monitoring feature. Consider implementing a custom solution or using third-party tools/plugins."
            }
        }


# Define Oracle connector
class OracleConnector(DBConnector):
    def connect(self, host, port, database, username, password):
        return cx_Oracle.connect(
            f"{username}/{password}@{host}:{port}/{database}"
        )

    def scan_for_sensitive_data(self, cursor):
        cursor.execute("SELECT TABLE_NAME, COLUMN_NAME FROM ALL_TAB_COLUMNS WHERE COLUMN_NAME LIKE '%PATIENT%'")
        sensitive_data = cursor.fetchall()

        additional_terms = ["MEDICAL CONDITION", "SSN", "DOB", "ADDRESS", "PHONE NUMBER", "EMAIL ADDRESS",
                            "MEDICAL PROCEDURE", "HEALTHCARE PROVIDER", "MEDICATION NAME", "INSURANCE INFORMATION",
                            "LAB RESULT", "GENETIC INFORMATION", "PAYMENT INFORMATION"]
        for term in additional_terms:
            cursor.execute(f"SELECT TABLE_NAME, COLUMN_NAME FROM ALL_TAB_COLUMNS WHERE COLUMN_NAME LIKE '%{term}%'")
            sensitive_data.extend(cursor.fetchall())

        return sensitive_data

    def check_access_controls(self, cursor):
        cursor.execute("SELECT grantee, privilege FROM USER_SYS_PRIVS WHERE grantee=CURRENT_USER")
        return cursor.fetchall()

    def check_audit_trail(self, cursor):
        return False  # Oracle does not have a built-in audit trail feature

    def check_encryption(self, cursor):
        cursor.execute("SELECT value FROM v$parameter WHERE name = 'encrypt_new_tablespaces'")
        return cursor.fetchone()[0] == "TRUE"

    def check_activity_monitoring(self, cursor):
        cursor.execute("SELECT EXISTS (SELECT 1 FROM V$SESSION)")
        return cursor.fetchone()[0]

    def get_description(self):
        return {
            "Sensitive Data Scan": {
                "description": "This check scans the database for columns containing sensitive data related to patients, such as names, addresses, or medical history.",
                "details": "The scan is performed by querying the 'ALL_TAB_COLUMNS' system view."
            },
            "Access Control Check": {
                "description": "This check examines the database's access controls to ensure that only authorized users have access to patient data.",
                "details": "The access control check queries the 'USER_SYS_PRIVS' system view to verify the privileges granted to the current user."
            },
            "Audit Trail Check": {
                "description": "Oracle does not have a built-in audit trail feature. Consider implementing a custom solution or using third-party tools/plugins."
            },
            "Encryption Check": {
                "description": "This check verifies if encryption is enabled in the Oracle database.",
                "details": "The encryption check queries the 'SELECT value FROM v$parameter WHERE name = 'encrypt_new_tablespaces'' statement to determine if tablespace encryption is enabled."
            },
            "Database Activity Monitoring Check": {
                "description": "Oracle does not have a built-in database activity monitoring feature. Consider implementing a custom solution or using third-party tools/plugins."
            }
        }


# Function to connect to the database
def get_database(db_type):
    if db_type == "PostgreSQL":
        return PostgreSQLConnector()
    elif db_type == "MySQL":
        return MySQLConnector()
    elif db_type == "SQL Server":
        return SQLServerConnector()
    elif db_type == "DB2":
        return DB2Connector()
    elif db_type == "Oracle":
        return OracleConnector()
    else:
        raise RuntimeError("Unsupported database type.")

# Main function
def main():
    st.title("HIPAA Compliance Checker")

    db_type = st.selectbox("Select database type", ["PostgreSQL", "MySQL", "SQL Server", "DB2", "Oracle"])

    # Display all the compliance checks for the selected database type
    st.markdown(f"## Compliance Checks")
    st.write("The following checks are going to be performed.")

    db = get_database(db_type)
    descriptions = db.get_description()
    for check, description in descriptions.items():
        st.markdown(f"#### {check}")
        st.write(description["description"])
        if "details" in description:
            st.write(description["details"])

    st.markdown(f"---")

    st.markdown(f"## Enter your DB credentials")
    host = st.text_input("Host:")
    port = st.text_input("Port:")
    database = st.text_input("Database name:")
    username = st.text_input("Username:")
    password = st.text_input("Password:", type="password")

    if st.button("Check Compliance"):
        try:
            conn = None
            with st.spinner("Connecting to the database..."):
                conn = db.connect(host, port, database, username, password)
                st.success("Connection successful! Generating report....")
            if conn:
                cursor = conn.cursor()

                # Perform compliance checks
                sensitive_data = None
                try:
                    sensitive_data = db.scan_for_sensitive_data(cursor)
                except Exception as e:
                    st.error(str(e))

                access_controls = None
                try:
                    access_controls = db.check_access_controls(cursor)
                except Exception as e:
                    st.error(str(e))

                audit_trail = None
                try:
                    audit_trail = db.check_audit_trail(cursor)
                except Exception as e:
                    st.error(str(e))

                encryption = None
                try:
                    encryption = db.check_encryption(cursor)
                except Exception as e:
                    st.error(str(e))

                activity_monitoring = None
                try:
                    activity_monitoring = db.check_activity_monitoring(cursor)
                except Exception as e:
                    st.error(str(e))

                st.markdown(f"---")
                # Generate compliance report
                st.header("HIPAA Compliance Report")
                sensitive_data_status = len(sensitive_data) == 0
                access_controls_status = len(access_controls) == 0

                if sensitive_data_status:
                    st.markdown("✅ Sensitive Data Scan - Passed")
                else:
                    st.markdown("❌ Sensitive Data Scan - Failed")
                if len(sensitive_data) > 0:
                    for row in sensitive_data:
                        st.write(f"Table: {row[0]}, Column: {row[1]}")

                if access_controls_status:
                    st.markdown("✅ Access Controls Check - Passed")
                else:
                    st.markdown("❌ Access Controls Check - Failed")
                if len(access_controls) > 0:
                    for row in access_controls:
                        if db_type == "PostgreSQL":
                            st.write(f"Grantee: {row[0]}, Privilege: {row[1]}")
                        else:
                            st.write(row)

                if audit_trail:
                    st.markdown("✅ Audit Trail Check - Passed")
                else:
                    st.markdown("❌ Audit Trail Check - Failed")

                encryption_status_icon = "✅" if encryption else "❌"
                st.markdown(f"{encryption_status_icon} Encryption Check - {'Passed' if encryption else 'Failed'}")

                activity_monitoring_status_icon = "✅" if activity_monitoring else "❌"
                st.markdown(f"{activity_monitoring_status_icon} Database Activity Monitoring Check - {'Passed' if activity_monitoring else 'Failed'}")

                # If all checks pass, display success message
                if sensitive_data_status and access_controls_status and audit_trail and encryption and activity_monitoring:
                    st.success("The database meets HIPAA compliance requirements.")
                else:
                    st.error("The database does not meet HIPAA compliance requirements.")

                conn.close()
        except Exception as e:
            st.error(str(e))

if __name__ == "__main__":
    main()
