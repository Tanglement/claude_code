"""MySQL database connection module."""

import pymysql
from pymysql.cursors import DictCursor
from contextlib import contextmanager
from typing import Optional, Any, List, Tuple
import logging

logger = logging.getLogger(__name__)


class MySQLConnection:
    """MySQL database connection manager."""

    def __init__(self, host: str, port: int, user: str, password: str, database: str):
        """Initialize MySQL connection.

        Args:
            host: MySQL server host
            port: MySQL server port
            user: MySQL username
            password: MySQL password
            database: Database name
        """
        self.config = {
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'database': database,
            'charset': 'utf8mb4',
            'cursorclass': DictCursor,
            'autocommit': True
        }
        self._pool = []
        self._pool_size = 10

    def get_connection(self) -> pymysql.Connection:
        """Get a database connection from pool or create new one."""
        try:
            conn = pymysql.connect(**self.config)
            return conn
        except Exception as e:
            logger.error(f"Failed to connect to MySQL: {e}")
            raise

    @contextmanager
    def get_cursor(self):
        """Context manager for database cursor."""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            yield cursor
            cursor.close()
        except Exception as e:
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()

    def execute(self, sql: str, params: Optional[Tuple] = None) -> int:
        """Execute a SQL statement.

        Args:
            sql: SQL statement
            params: Query parameters

        Returns:
            Number of affected rows
        """
        with self.get_cursor() as cursor:
            result = cursor.execute(sql, params)
            return result

    def query_one(self, sql: str, params: Optional[Tuple] = None) -> Optional[dict]:
        """Query a single row.

        Args:
            sql: SQL statement
            params: Query parameters

        Returns:
            Single row as dictionary or None
        """
        with self.get_cursor() as cursor:
            cursor.execute(sql, params)
            result = cursor.fetchone()
            return result

    def query_all(self, sql: str, params: Optional[Tuple] = None) -> List[dict]:
        """Query all rows.

        Args:
            sql: SQL statement
            params: Query parameters

        Returns:
            List of rows as dictionaries
        """
        with self.get_cursor() as cursor:
            cursor.execute(sql, params)
            result = cursor.fetchall()
            return result

    def insert(self, sql: str, params: Optional[Tuple] = None) -> int:
        """Insert a row and return the last insert id.

        Args:
            sql: INSERT statement
            params: Insert parameters

        Returns:
            Last insert id
        """
        with self.get_cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.lastrowid

    def close(self):
        """Close all connections in pool."""
        for conn in self._pool:
            try:
                conn.close()
            except Exception:
                pass
        self._pool.clear()


# Global MySQL connection instance
mysql_conn: Optional[MySQLConnection] = None


def init_mysql(host: str = 'localhost', port: int = 3306, user: str = 'root',
               password: str = '', database: str = 'stock_db') -> MySQLConnection:
    """Initialize MySQL connection.

    Args:
        host: MySQL server host
        port: My        user: MySQL server port
SQL username
        password: MySQL password
        database: Database name

    Returns:
        MySQLConnection instance
    """
    global mysql_conn
    mysql_conn = MySQLConnection(host, port, user, password, database)
    logger.info(f"MySQL connected to {host}:{port}/{database}")
    return mysql_conn


def get_mysql() -> MySQLConnection:
    """Get the global MySQL connection instance.

    Returns:
        MySQLConnection instance

    Raises:
        RuntimeError: If MySQL not initialized
    """
    if mysql_conn is None:
        raise RuntimeError("MySQL not initialized. Call init_mysql() first.")
    return mysql_conn
