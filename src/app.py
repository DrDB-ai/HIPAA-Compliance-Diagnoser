import streamlit as st
from connectors.connector_factory import get_database, get_database_list

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


def main():
    st.image("logo.png", width=200)
    st.title("HIPAA Compliance Diagnoser")

    db_type = st.selectbox("Select database type", get_database_list())

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
                st.markdown(
                    f"{encryption_status_icon} Encryption Check - {'Passed' if encryption else 'Failed'}")

                activity_monitoring_status_icon = "✅" if activity_monitoring else "❌"
                st.markdown(
                    f"{activity_monitoring_status_icon} Database Activity Monitoring Check - {'Passed' if activity_monitoring else 'Failed'}")

                # If all checks pass, display success message
                if sensitive_data_status and access_controls_status and audit_trail and encryption and activity_monitoring:
                    st.success(
                        "The database meets HIPAA compliance requirements.")
                else:
                    st.error(
                        "The database does not meet HIPAA compliance requirements.")

                conn.close()
        except Exception as e:
            st.error(str(e))


if __name__ == "__main__":
    main()
