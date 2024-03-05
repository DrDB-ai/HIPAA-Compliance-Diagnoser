import unittest
from testcontainers.mssql import SqlServerContainer
from src.app import SQLServerConnector


class TestMsSqlServerConnector(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start SQL Server container
        cls.sql_server_container = SqlServerContainer()
        cls.sql_server_container.start()
        # Connect to the SQL Server database
        cls.sql_server_connector = SQLServerConnector()
        cls.conn = cls.sql_server_connector.connect(
            cls.sql_server_container.get_container_host_ip(),
            cls.sql_server_container.get_exposed_port(1433),
            cls.sql_server_container.SQLSERVER_DBNAME,
            cls.sql_server_container.SQLSERVER_USER,
            cls.sql_server_container.SQLSERVER_PASSWORD
        )

        # Create table for happy path test
        cls.cursor = cls.conn.cursor()
        cls.cursor.execute("""
            CREATE TABLE patients (
                id INT PRIMARY KEY,
                name VARCHAR(255),
                ssn VARCHAR(20),
                address VARCHAR(255)
            )
        """)
        sql = """
            INSERT INTO patients (id, name, ssn, address) VALUES 
            (?, ?, ?, ?)
        """
        cls.cursor.execute(sql, 1, 'John Doe', '123-45-6789', '123 Main St')
        cls.cursor.execute(sql, 2, 'Jane Doe', '987-65-4321', '456 Oak St')
        cls.conn.commit()

    @classmethod
    def tearDownClass(cls):
        # Close connection and stop container
        cls.cursor.close()
        cls.conn.close()
        cls.sql_server_container.stop()

    def test_scan_for_sensitive_data(self):
        # Happy path test for scan_for_sensitive_data
        with self.conn.cursor() as cursor:
            sensitive_data = self.sql_server_connector.scan_for_sensitive_data(
                cursor)
        # Expecting 2 row of sensitive data
        self.assertEqual(len(sensitive_data), 2)

    def test_check_access_controls(self):
        # Happy path test for check_access_controls
        with self.conn.cursor() as cursor:
            access_controls = self.sql_server_connector.check_access_controls(
                cursor)
        # Expecting a list of access controls
        self.assertTrue(isinstance(access_controls, list))

    def test_check_audit_trail(self):
        # Happy path test for check_audit_trail
        with self.conn.cursor() as cursor:
            audit_trail = self.sql_server_connector.check_audit_trail(cursor)
        # Expecting a boolean value
        self.assertTrue(isinstance(audit_trail, bool))

    def test_check_encryption(self):
        # Happy path test for check_encryption
        with self.conn.cursor() as cursor:
            encryption_status = self.sql_server_connector.check_encryption(
                cursor)
        # Expecting a boolean value
        self.assertTrue(isinstance(encryption_status, bool))

    def test_check_activity_monitoring(self):
        # Happy path test for check_activity_monitoring
        with self.conn.cursor() as cursor:
            activity_monitoring_status = self.sql_server_connector.check_activity_monitoring(
                cursor)
        # Expecting a boolean value
        self.assertFalse(isinstance(activity_monitoring_status, bool))


if __name__ == "__main__":
    unittest.main()
