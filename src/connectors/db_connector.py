class DBConnector:

    def connect(self, host, port, database, username, password):
        raise NotImplementedError(
            "connect method must be implemented by subclasses")

    def scan_for_sensitive_data(self, cursor):
        raise NotImplementedError(
            "scan_for_sensitive_data method must be implemented by subclasses")

    def check_access_controls(self, cursor):
        raise NotImplementedError(
            "check_access_controls method must be implemented by subclasses")

    def check_audit_trail(self, cursor):
        raise NotImplementedError(
            "check_audit_trail method must be implemented by subclasses")

    def check_encryption(self, cursor):
        raise NotImplementedError(
            "check_encryption method must be implemented by subclasses")

    def check_activity_monitoring(self, cursor):
        raise NotImplementedError(
            "check_activity_monitoring method must be implemented by subclasses")

    def get_description(self):
        raise NotImplementedError(
            "get_description method must be implemented by subclasses")