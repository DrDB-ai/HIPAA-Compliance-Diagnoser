import unittest
from testcontainers.mysql import MySqlContainer
from src.app import MySQLConnector


class TestMySQLConnector(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start MySQL container
        cls.mysql_container = MySqlContainer("mysql:latest")
        cls.mysql_container.start()
        # Connect to the database
        cls.mysql_connector = MySQLConnector()
        cls.conn = cls.mysql_connector.connect(
            cls.mysql_container.get_container_host_ip(),
            cls.mysql_container.get_exposed_port(3306),
            cls.mysql_container.MYSQL_DATABASE,
            "root",
            "test"
        )
        # Create table for happy path test
        cls.cursor = cls.conn.cursor()
        cls.cursor.execute("""
            CREATE TABLE patients (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255),
                ssn VARCHAR(20),
                address VARCHAR(255)
            )
        """)
        cls.cursor.execute("""
            INSERT INTO patients (name, ssn, address) VALUES 
            ('John Doe', '123-45-6789', '123 Main St'),
            ('Jane Doe', '987-65-4321', '456 Oak St')
        """)
        cls.cursor.execute("""
            SET GLOBAL general_log = 'ON', slow_query_log = 'ON'
        """)
        cls.conn.commit()

    @classmethod
    def tearDownClass(cls):
        # Close connection and stop container
        cls.cursor.close()
        cls.conn.close()
        cls.mysql_container.stop()

    def test_scan_for_sensitive_data(self):
        # Happy path test for scan_for_sensitive_data
        with self.conn.cursor() as cursor:
            sensitive_data = self.mysql_connector.scan_for_sensitive_data(
                cursor)
        # Expecting 2 rows of sensitive data
        self.assertEqual(len(sensitive_data), 2)

    def test_check_access_controls(self):
        # Happy path test for check_access_controls
        with self.conn.cursor() as cursor:
            access_controls = self.mysql_connector.check_access_controls(
                cursor)
        # Expecting a list of access controls
        self.assertTrue(isinstance(access_controls, list))

    def test_check_audit_trail(self):
        # Happy path test for check_audit_trail
        with self.conn.cursor() as cursor:
            audit_trail = self.mysql_connector.check_audit_trail(cursor)
        # Expecting a boolean value
        self.assertTrue(isinstance(audit_trail, bool))

    def test_check_encryption(self):
        # Happy path test for check_encryption
        with self.conn.cursor() as cursor:
            encryption_status = self.mysql_connector.check_encryption(cursor)
        # Expecting a boolean value
        self.assertTrue(isinstance(encryption_status, bool))

    def test_check_activity_monitoring(self):
        # Happy path test for check_activity_monitoring
        with self.conn.cursor() as cursor:
            activity_monitoring_status = self.mysql_connector.check_activity_monitoring(
                cursor)
        # Expecting a boolean value
        self.assertTrue(isinstance(activity_monitoring_status, bool))


if __name__ == "__main__":
    unittest.main()
