from .postgresql_connector import PostgreSQLConnector
from .mysql_connector import MySQLConnector
from .sqlserver_connector import SQLServerConnector
from .db2_connector import DB2Connector
from .oracle_connector import OracleConnector


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


def get_database_list():
    return ["PostgreSQL", "MySQL", "SQL Server", "DB2", "Oracle"]
