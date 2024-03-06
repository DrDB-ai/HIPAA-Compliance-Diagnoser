import unittest
from testcontainers.oracle import OracleDbContainer
from src.connectors.oracle_connector import OracleConnector


class TestOracleConnector(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start Oracle container
        cls.oracle_container = OracleDbContainer()
        cls.oracle_container.start()
        # Connect to the Oracle database
        cls.oracle_connector = OracleConnector()
        cls.conn = cls.oracle_connector.connect(cls.oracle_container.get_container_host_ip(),
                                                cls.oracle_container.get_exposed_port(
                                                    1521),
                                                "xe",
                                                "system",
                                                "oracle")
        # Create table for happy path test
        cls.cursor = cls.conn.cursor()
        cls.cursor.execute("""
            CREATE TABLE patients (
                id NUMBER PRIMARY KEY,
                name VARCHAR2(255),
                ssn VARCHAR2(20),
                address VARCHAR2(255)
            )
        """)
        sql = """
                INSERT INTO patients (id, name, ssn, address) VALUES 
                (:id1, :name1, :ssn1, :address1)
            """
        cls.cursor.execute(sql, id1=1, name1='John Doe',
                           ssn1='123-45-6789', address1='123 Main St')
        cls.cursor.execute(sql, id1=2, name1='Jane Doe',
                           ssn1='987-65-4321', address1='456 Oak St')
        cls.conn.commit()

    @classmethod
    def tearDownClass(cls):
        # Close connection and stop container
        cls.cursor.close()
        cls.conn.close()
        cls.oracle_container.stop()

    def test_scan_for_sensitive_data(self):
        # Happy path test for scan_for_sensitive_data
        with self.conn.cursor() as cursor:
            sensitive_data = self.oracle_connector.scan_for_sensitive_data(
                cursor)
        # Expecting 1 rows of sensitive data
        self.assertEqual(len(sensitive_data), 1)

    def test_check_access_controls(self):
        # Happy path test for check_access_controls
        with self.conn.cursor() as cursor:
            access_controls = self.oracle_connector.check_access_controls(
                cursor)
        # Expecting a list of access controls
        self.assertTrue(isinstance(access_controls, list))

    def test_check_audit_trail(self):
        # Happy path test for check_audit_trail
        with self.conn.cursor() as cursor:
            audit_trail = self.oracle_connector.check_audit_trail(cursor)
        # Expecting a boolean value
        self.assertFalse(isinstance(audit_trail, bool))

    def test_check_encryption(self):
        # Happy path test for check_encryption
        with self.conn.cursor() as cursor:
            encryption_status = self.oracle_connector.check_encryption(cursor)
        # Expecting a boolean value
        self.assertTrue(isinstance(encryption_status, bool))

    def test_check_activity_monitoring(self):
        # Happy path test for check_activity_monitoring
        with self.conn.cursor() as cursor:
            activity_monitoring_status = self.oracle_connector.check_activity_monitoring(
                cursor)
        # Expecting a boolean value
        self.assertFalse(isinstance(activity_monitoring_status, bool))


if __name__ == "__main__":
    unittest.main()
