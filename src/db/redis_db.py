"""Redis database connection module."""

import redis
from redis import Redis
from typing import Optional, Any
import json
import logging

logger = logging.getLogger(__name__)


class RedisConnection:
    """Redis database connection manager."""

    def __init__(self, host: str, port: int, password: Optional[str] = None,
                 db: int = 0, decode_responses: bool = True):
        """Initialize Redis connection.

        Args:
            host: Redis server host
            port: Redis server port
            password: Redis password (optional)
            db: Redis database number
            decode_responses: Decode responses to strings
        """
        self.config = {
            'host': host,
            'port': port,
            'password': password,
            'db': db,
            'decode_responses': decode_responses
        }
        self.client: Optional[Redis] = None

    def connect(self) -> 'RedisConnection':
        """Connect to Redis server."""
        try:
            self.client = redis.Redis(**self.config)
            self.client.ping()
            logger.info(f"Redis connected to {self.config['host']}:{self.config['port']}")
            return self
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    def get(self, key: str) -> Optional[str]:
        """Get a value by key.

        Args:
            key: Redis key

        Returns:
            Value or None
        """
        if not self.client:
            raise RuntimeError("Redis not connected. Call connect() first.")
        return self.client.get(key)

    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """Set a key-value pair.

        Args:
            key: Redis key
            value: Value to store
            ex: Expiration time in seconds

        Returns:
            True if successful
        """
        if not self.client:
            raise RuntimeError("Redis not connected. Call connect() first.")

        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)

        return self.client.set(key, value, ex=ex)

    def delete(self, *keys: str) -> int:
        """Delete keys.

        Args:
            keys: Redis keys to delete

        Returns:
            Number of keys deleted
        """
        if not self.client:
            raise RuntimeError("Redis not connected. Call connect() first.")
        return self.client.delete(*keys)

    def exists(self, key: str) -> bool:
        """Check if a key exists.

        Args:
            key: Redis key

        Returns:
            True if key exists
        """
        if not self.client:
            raise RuntimeError("Redis not connected. Call connect() first.")
        return bool(self.client.exists(key))

    def expire(self, key: str, seconds: int) -> bool:
        """Set expiration time for a key.

        Args:
            key: Redis key
            seconds: Expiration time in seconds

        Returns:
            True if timeout was set
        """
        if not self.client:
            raise RuntimeError("Redis not connected. Call connect() first.")
        return self.client.expire(key, seconds)

    def ttl(self, key: str) -> int:
        """Get time to live for a key.

        Args:
            key: Redis key

        Returns:
            Time to live in seconds (-1 if no expiration, -2 if key doesn't exist)
        """
        if not self.client:
            raise RuntimeError("Redis not connected. Call connect() first.")
        return self.client.ttl(key)

    # Hash operations
    def hset(self, name: str, key: str = None, value: Any = None, mapping: dict = None) -> int:
        """Set hash field(s).

        Args:
            name: Hash name
            key: Field key
            value: Field value
            mapping: Dictionary of field-value pairs

        Returns:
            Number of fields set
        """
        if not self.client:
            raise RuntimeError("Redis not connected. Call connect() first.")

        if mapping:
            return self.client.hset(name, mapping=mapping)
        return self.client.hset(name, key, value)

    def hget(self, name: str, key: str) -> Optional[str]:
        """Get hash field value.

        Args:
            name: Hash name
            key: Field key

        Returns:
            Field value or None
        """
        if not self.client:
            raise RuntimeError("Redis not connected. Call connect() first.")
        return self.client.hget(name, key)

    def hgetall(self, name: str) -> dict:
        """Get all hash fields.

        Args:
            name: Hash name

        Returns:
            Dictionary of all fields
        """
        if not self.client:
            raise RuntimeError("Redis not connected. Call connect() first.")
        return self.client.hgetall(name)

    def hdel(self, name: str, *keys: str) -> int:
        """Delete hash fields.

        Args:
            name: Hash name
            keys: Field keys to delete

        Returns:
            Number of fields deleted
        """
        if not self.client:
            raise RuntimeError("Redis not connected. Call connect() first.")
        return self.client.hdel(name, *keys)

    # List operations
    def lpush(self, key: str, *values: Any) -> int:
        """Push values to the left of list.

        Args:
            key: List key
            values: Values to push

        Returns:
            Length of list after push
        """
        if not self.client:
            raise RuntimeError("Redis not connected. Call connect() first.")
        return self.client.lpush(key, *values)

    def rpush(self, key: str, *values: Any) -> int:
        """Push values to the right of list.

        Args:
            key: List key
            values: Values to push

        Returns:
            Length of list after push
        """
        if not self.client:
            raise RuntimeError("Redis not connected. Call connect() first.")
        return self.client.rpush(key, *values)

    def lrange(self, key: str, start: int, end: int) -> list:
        """Get list range.

        Args:
            key: List key
            start: Start index
            end: End index

        Returns:
            List of values
        """
        if not self.client:
            raise RuntimeError("Redis not connected. Call connect() first.")
        return self.client.lrange(key, start, end)

    # Sorted set operations
    def zadd(self, name: str, mapping: dict) -> int:
        """Add members to sorted set.

        Args:
            name: Sorted set name
            mapping: Dictionary of member-score pairs

        Returns:
            Number of members added
        """
        if not self.client:
            raise RuntimeError("Redis not connected. Call connect() first.")
        return self.client.zadd(name, mapping)

    def zrevrange(self, name: str, start: int, end: int, withscores: bool = False) -> list:
        """Get members from sorted set in reverse order.

        Args:
            name: Sorted set name
            start: Start index
            end: End index
            withscores: Include scores

        Returns:
            List of members (and scores if withscores=True)
        """
        if not self.client:
            raise RuntimeError("Redis not connected. Call connect() first.")
        return self.client.zrevrange(name, start, end, withscores=withscores)

    def close(self):
        """Close Redis connection."""
        if self.client:
            self.client.close()
            logger.info("Redis connection closed")


# Global Redis connection instance
redis_conn: Optional[RedisConnection] = None


def init_redis(host: str = 'localhost', port: int = 6379, password: Optional[str] = None,
               db: int = 0) -> RedisConnection:
    """Initialize Redis connection.

    Args:
        host: Redis server host
        port: Redis server port
        password: Redis password (optional)
        db: Redis database number

    Returns:
        RedisConnection instance
    """
    global redis_conn
    redis_conn = RedisConnection(host, port, password, db)
    redis_conn.connect()
    return redis_conn


def get_redis() -> RedisConnection:
    """Get the global Redis connection instance.

    Returns:
        RedisConnection instance

    Raises:
        RuntimeError: If Redis not initialized
    """
    if redis_conn is None:
        raise RuntimeError("Redis not initialized. Call init_redis() first.")
    return redis_conn
