"""Pytest configuration and fixtures."""

import pytest
from unittest.mock import MagicMock, patch


# Mock database connections before importing modules
@pytest.fixture(scope='session', autouse=True)
def mock_database_connections():
    """Mock database connections for testing."""
    # Mock MySQL
    mock_mysql = MagicMock()
    mock_mysql.execute.return_value = 1
    mock_mysql.insert.return_value = 1
    mock_mysql.query_one.return_value = None
    mock_mysql.query_all.return_value = []

    # Mock MongoDB
    mock_mongodb = MagicMock()
    mock_mongodb.insert_one.return_value = 'test_id'
    mock_mongodb.find_one.return_value = None
    mock_mongodb.find_many.return_value = []

    # Mock Redis
    mock_redis = MagicMock()
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True

    with patch('src.db.mysql_db.get_mysql', return_value=mock_mysql):
        with patch('src.db.mongodb.get_mongodb', return_value=mock_mongodb):
            with patch('src.db.redis_db.get_redis', return_value=mock_redis):
                yield {
                    'mysql': mock_mysql,
                    'mongodb': mock_mongodb,
                    'redis': mock_redis
                }


@pytest.fixture
def sample_stock_basic():
    """Sample stock basic data."""
    return {
        'symbol': '600519',
        'name': '贵州茅台',
        'market': 'A股',
        'industry': '白酒',
        'listing_date': '2001-08-27'
    }


@pytest.fixture
def sample_stock_realtime():
    """Sample stock realtime data."""
    return {
        'symbol': '600519',
        'price': 1686.00,
        'change': 10.00,
        'change_pct': 0.59,
        'open': 1676.00,
        'high': 1688.00,
        'low': 1675.00,
        'close_yest': 1676.00,
        'volume': 1234567,
        'amount': 2089000000,
        'turnover': 0.23,
        'pe': 58.52,
        'pb': 12.35
    }


@pytest.fixture
def sample_user():
    """Sample user data."""
    return {
        'username': 'testuser',
        'password': 'testpass123',
        'email': 'test@example.com'
    }
