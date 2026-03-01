"""Configuration management module."""

import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class DatabaseConfig:
    """Database configuration."""
    mysql_host: str = 'localhost'
    mysql_port: int = 3306
    mysql_user: str = 'root'
    mysql_password: str = 'csw19961226'
    mysql_database: str = 'stock_db'

    mongodb_host: str = 'localhost'
    mongodb_port: int = 27017
    mongodb_database: str = 'stock_db'
    mongodb_username: Optional[str] = None
    mongodb_password: Optional[str] = None

    redis_host: str = 'localhost'
    redis_port: int = 6379
    redis_password: Optional[str] = None
    redis_db: int = 0


@dataclass
class AppConfig:
    """Application configuration."""
    debug: bool = False
    secret_key: str = 'your-secret-key-here'
    host: str = '0.0.0.0'
    port: int = 5000

    # JWT configuration
    jwt_secret: str = 'your-jwt-secret-key'
    jwt_expiration_hours: int = 24

    # API configuration
    api_prefix: str = '/api/v1'

    # Data source configuration
    realtime_update_interval: int = 3  # seconds
    news_update_interval: int = 3600  # seconds (1 hour)

    # Cache configuration
    cache_ttl: int = 60  # seconds


class Config:
    """Global configuration class."""

    def __init__(self):
        self.database = DatabaseConfig()
        self.app = AppConfig()

    def load_from_env(self):
        """Load configuration from environment variables."""
        # MySQL
        self.database.mysql_host = os.getenv('MYSQL_HOST', 'localhost')
        self.database.mysql_port = int(os.getenv('MYSQL_PORT', 3306))
        self.database.mysql_user = os.getenv('MYSQL_USER', 'root')
        self.database.mysql_password = os.getenv('MYSQL_PASSWORD', '')
        self.database.mysql_database = os.getenv('MYSQL_DATABASE', 'stock_db')

        # MongoDB
        self.database.mongodb_host = os.getenv('MONGODB_HOST', 'localhost')
        self.database.mongodb_port = int(os.getenv('MONGODB_PORT', 27017))
        self.database.mongodb_database = os.getenv('MONGODB_DATABASE', 'stock_db')
        self.database.mongodb_username = os.getenv('MONGODB_USERNAME')
        self.database.mongodb_password = os.getenv('MONGODB_PASSWORD')

        # Redis
        self.database.redis_host = os.getenv('REDIS_HOST', 'localhost')
        self.database.redis_port = int(os.getenv('REDIS_PORT', 6379))
        self.database.redis_password = os.getenv('REDIS_PASSWORD')
        self.database.redis_db = int(os.getenv('REDIS_DB', 0))

        # App
        self.app.debug = os.getenv('DEBUG', 'false').lower() == 'true'
        self.app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')
        self.app.host = os.getenv('HOST', '0.0.0.0')
        self.app.port = int(os.getenv('PORT', 5000))

        # JWT
        self.app.jwt_secret = os.getenv('JWT_SECRET', 'your-jwt-secret-key')

    def get_mysql_config(self) -> dict:
        """Get MySQL configuration dict."""
        return {
            'host': self.database.mysql_host,
            'port': self.database.mysql_port,
            'user': self.database.mysql_user,
            'password': self.database.mysql_password,
            'database': self.database.mysql_database
        }

    def get_mongodb_config(self) -> dict:
        """Get MongoDB configuration dict."""
        config = {
            'host': self.database.mongodb_host,
            'port': self.database.mongodb_port,
            'database': self.database.mongodb_database
        }
        if self.database.mongodb_username:
            config['username'] = self.database.mongodb_username
        if self.database.mongodb_password:
            config['password'] = self.database.mongodb_password
        return config

    def get_redis_config(self) -> dict:
        """Get Redis configuration dict."""
        config = {
            'host': self.database.redis_host,
            'port': self.database.redis_port,
            'db': self.database.redis_db
        }
        if self.database.redis_password:
            config['password'] = self.database.redis_password
        return config


# Global configuration instance
config = Config()


def get_config() -> Config:
    """Get global configuration instance."""
    return config
