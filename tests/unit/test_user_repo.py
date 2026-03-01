# User Repository Tests

import pytest
from unittest.mock import MagicMock, patch
from decimal import Decimal
from datetime import date, datetime


# Mock database connections
@pytest.fixture
def mock_mysql():
    """Create mock MySQL connection."""
    mock = MagicMock()
    mock.execute.return_value = 1
    mock.insert.return_value = 1
    mock.query_one.return_value = None
    mock.query_all.return_value = []
    return mock


@pytest.fixture
def user_repo(mock_mysql):
    """Create UserRepository with mock database."""
    with patch('src.repositories.user_repo.get_mysql', return_value=mock_mysql):
        from src.repositories.user_repo import UserRepository
        return UserRepository()


# ==================== User Management Tests ====================

class TestInsertUser:
    """Test insert user"""

    def test_insert_user_normal(self, user_repo, mock_mysql):
        """Normal case: Create user successfully"""
        mock_mysql.query_one.return_value = None  # No existing user

        result = user_repo.insert_user(
            username="testuser",
            password="password123",
            email="test@example.com",
            phone="13800138000"
        )
        assert result == 1

    def test_insert_user_duplicate_username(self, user_repo, mock_mysql):
        """Error case: Username already exists"""
        mock_mysql.query_one.return_value = {
            'id': 1,
            'username': 'testuser',
            'password': 'hash',
            'email': 'test@example.com',
            'phone': '13800138000',
            'created_at': datetime.now()
        }

        with pytest.raises(Exception):
            user_repo.insert_user(
                username="testuser",
                password="password123"
            )

    def test_insert_user_empty_username(self, user_repo, mock_mysql):
        """Boundary case: Empty username"""
        with pytest.raises(Exception):
            user_repo.insert_user(
                username="",
                password="password123"
            )

    def test_insert_user_empty_password(self, user_repo, mock_mysql):
        """Boundary case: Empty password"""
        with pytest.raises(Exception):
            user_repo.insert_user(
                username="testuser",
                password=""
            )


class TestGetUserByUsername:
    """Test get user by username"""

    def test_get_user_normal(self, user_repo, mock_mysql):
        """Normal case: Get user successfully"""
        mock_mysql.query_one.return_value = {
            'id': 1,
            'username': 'testuser',
            'password': 'hashed_password',
            'email': 'test@example.com',
            'phone': '13800138000',
            'created_at': datetime.now()
        }

        user = user_repo.get_user_by_username("testuser")
        assert user is not None
        assert user.username == "testuser"

    def test_get_user_not_found(self, user_repo, mock_mysql):
        """Error case: User not found"""
        mock_mysql.query_one.return_value = None

        user = user_repo.get_user_by_username("nonexistent")
        assert user is None


class TestVerifyPassword:
    """Test password verification"""

    def test_verify_password_correct(self, user_repo, mock_mysql):
        """Normal case: Password is correct"""
        mock_mysql.query_one.return_value = {
            'id': 1,
            'username': 'testuser',
            'password': '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8',  # hash of 'password'
            'email': 'test@example.com',
            'phone': None,
            'created_at': datetime.now()
        }

        # SHA256 hash of 'password123'
        mock_mysql.query_one.return_value['password'] = 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f'

        result = user_repo.verify_password("testuser", "password123")
        assert result is not None

    def test_verify_password_incorrect(self, user_repo, mock_mysql):
        """Error case: Password is incorrect"""
        mock_mysql.query_one.return_value = {
            'id': 1,
            'username': 'testuser',
            'password': 'hashed_password',
            'email': 'test@example.com',
            'phone': None,
            'created_at': datetime.now()
        }

        with pytest.raises(Exception):
            user_repo.verify_password("testuser", "wrongpassword")

    def test_verify_password_nonexistent_user(self, user_repo, mock_mysql):
        """Error case: User does not exist"""
        mock_mysql.query_one.return_value = None

        with pytest.raises(Exception):
            user_repo.verify_password("nonexistent", "password123")


# ==================== User Holdings Tests ====================

class TestInsertUserHolding:
    """Test insert user holding"""

    def test_insert_holding_normal(self, user_repo, mock_mysql):
        """Normal case: Insert holding successfully"""
        result = user_repo.insert_user_holding(
            user_id=1,
            symbol="600519",
            shares=100,
            cost_price=Decimal("1600.00"),
            purchase_date=date(2021, 1, 15)
        )
        assert result == 1

    def test_insert_holding_negative_shares(self, user_repo, mock_mysql):
        """Error case: Negative shares"""
        with pytest.raises(Exception):
            user_repo.insert_user_holding(
                user_id=1,
                symbol="600519",
                shares=-100,
                cost_price=Decimal("1600.00"),
                purchase_date=date(2021, 1, 15)
            )

    def test_insert_holding_zero_cost(self, user_repo, mock_mysql):
        """Boundary case: Cost price is zero"""
        with pytest.raises(Exception):
            user_repo.insert_user_holding(
                user_id=1,
                symbol="600519",
                shares=100,
                cost_price=Decimal("0"),
                purchase_date=date(2021, 1, 15)
            )

    def test_insert_holding_future_date(self, user_repo, mock_mysql):
        """Error case: Purchase date is in future"""
        with pytest.raises(Exception):
            user_repo.insert_user_holding(
                user_id=1,
                symbol="600519",
                shares=100,
                cost_price=Decimal("1600.00"),
                purchase_date=date(2030, 1, 1)
            )


class TestGetUserHoldings:
    """Test get user holdings"""

    def test_get_holdings_normal(self, user_repo, mock_mysql):
        """Normal case: Get user holdings"""
        mock_mysql.query_all.return_value = [
            {
                'id': 1,
                'user_id': 1,
                'symbol': '600519',
                'shares': 100,
                'cost_price': Decimal('1600.00'),
                'purchase_date': date(2021, 1, 15),
                'created_at': datetime.now()
            }
        ]

        holdings = user_repo.get_user_holdings(1)
        assert isinstance(holdings, list)
        assert len(holdings) == 1

    def test_get_holdings_empty(self, user_repo, mock_mysql):
        """Boundary case: User has no holdings"""
        mock_mysql.query_all.return_value = []

        holdings = user_repo.get_user_holdings(999)
        assert len(holdings) == 0


class TestUpdateUserHolding:
    """Test update user holding"""

    def test_update_holding_normal(self, user_repo, mock_mysql):
        """Normal case: Update holding successfully"""
        mock_mysql.execute.return_value = 1

        result = user_repo.update_user_holding(
            user_id=1,
            symbol="600519",
            shares=200,
            cost_price=Decimal("1700.00")
        )
        assert result == 1


class TestDeleteUserHolding:
    """Test delete user holding"""

    def test_delete_holding_normal(self, user_repo, mock_mysql):
        """Normal case: Delete holding successfully"""
        mock_mysql.execute.return_value = 1

        result = user_repo.delete_user_holding(1, "600519")
        assert result == 1
