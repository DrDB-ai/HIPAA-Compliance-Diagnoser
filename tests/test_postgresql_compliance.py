import unittest
import psycopg2
from testcontainers.postgres import PostgresContainer
from src.app import PostgreSQLConnector

class TestPostgreSQLConnector(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start Postgres container
        cls.postgres_container = PostgresContainer("postgres:latest")
        cls.postgres_container.start()
        # Connect to the database
        cls.conn = psycopg2.connect(
            dbname=cls.postgres_container.POSTGRES_DB,
            user=cls.postgres_container.POSTGRES_USER,
            password=cls.postgres_container.POSTGRES_PASSWORD,
            host=cls.postgres_container.get_container_host_ip(),
            port=cls.postgres_container.get_exposed_port(5432),
        )
        # Create table for happy path test
        cls.cursor = cls.conn.cursor()
        cls.cursor.execute("""
            CREATE TABLE patients (
                id SERIAL PRIMARY KEY,
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
        cls.conn.commit()

    @classmethod
    def tearDownClass(cls):
        # Close connection and stop container
        cls.cursor.close()
        cls.conn.close()
        cls.postgres_container.stop()

    def setUp(self):
        # Initialize the PostgreSQLConnector instance
        self.postgres_connector = PostgreSQLConnector()

    def test_scan_for_sensitive_data(self):
        # Happy path test for scan_for_sensitive_data
        with self.conn.cursor() as cursor:
            sensitive_data = self.postgres_connector.scan_for_sensitive_data(cursor)
        self.assertEqual(len(sensitive_data), 2)  # Expecting 2 rows of sensitive data

    def test_check_access_controls(self):
        # Happy path test for check_access_controls
        with self.conn.cursor() as cursor:
            access_controls = self.postgres_connector.check_access_controls(cursor)
        self.assertTrue(isinstance(access_controls, list))  # Expecting a list of access controls

    def test_check_audit_trail(self):
        # Happy path test for check_audit_trail
        with self.conn.cursor() as cursor:
            audit_trail = self.postgres_connector.check_audit_trail(cursor)
        self.assertTrue(isinstance(audit_trail, bool))  # Expecting a boolean value

    def test_check_encryption(self):
        # Happy path test for check_encryption
        with self.conn.cursor() as cursor:
            encryption_status = self.postgres_connector.check_encryption(cursor)
        self.assertTrue(isinstance(encryption_status, bool))  # Expecting a boolean value

    def test_check_activity_monitoring(self):
        # Happy path test for check_activity_monitoring
        with self.conn.cursor() as cursor:
            activity_monitoring_status = self.postgres_connector.check_activity_monitoring(cursor)
        self.assertTrue(isinstance(activity_monitoring_status, bool))  # Expecting a boolean value

if __name__ == "__main__":
    unittest.main()
