"""Database package initialization and configuration."""

from .mysql_db import init_mysql, get_mysql, MySQLConnection
from .mongodb import init_mongodb, get_mongodb, MongoDBConnection
from .redis_db import init_redis, get_redis, RedisConnection


__all__ = [
    'init_mysql',
    'get_mysql',
    'MySQLConnection',
    'init_mongodb',
    'get_mongodb',
    'MongoDBConnection',
    'init_redis',
    'get_redis',
    'RedisConnection'
]


def init_all_databases(mysql_config: dict = None, mongodb_config: dict = None,
                       redis_config: dict = None):
    """Initialize all database connections.

    Args:
        mysql_config: MySQL configuration dict
        mongodb_config: MongoDB configuration dict
        redis_config: Redis configuration dict
    """
    if mysql_config:
        init_mysql(**mysql_config)

    if mongodb_config:
        init_mongodb(**mongodb_config)

    if redis_config:
        init_redis(**redis_config)


def close_all_databases():
    """Close all database connections."""
    global mysql_conn, mongodb_conn, redis_conn

    if mysql_conn:
        mysql_conn.close()

    if mongodb_conn:
        mongodb_conn.close()

    if redis_conn:
        redis_conn.close()


# Import global connection instances for cleanup
from . import mysql_db
from . import mongodb
from . import redis_db
