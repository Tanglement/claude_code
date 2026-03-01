"""User business logic service."""

from typing import Optional, List, Dict
from datetime import datetime, timedelta
from decimal import Decimal
import hashlib
import secrets

from src.repositories.user_repo import UserRepository
from src.models.user import User, UserHolding, UserWatchlist, UserPreference
from src.models.exceptions import UserNotFoundError, AuthenticationError, DuplicateError
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AuthService:
    """Authentication service for JWT token management."""

    def __init__(self, secret_key: str = 'default-secret-key', expiration_hours: int = 24):
        """Initialize auth service.

        Args:
            secret_key: Secret key for token generation
            expiration_hours: Token expiration time in hours
        """
        self.secret_key = secret_key
        self.expiration_hours = expiration_hours
        self.token_length = 32

    def generate_token(self, user_id: int, username: str) -> Dict[str, str]:
        """Generate JWT token for user.

        Args:
            user_id: User ID
            username: Username

        Returns:
            Dictionary with token and expiration
        """
        # Generate random token
        token = secrets.token_urlsafe(self.token_length)
        expires_at = datetime.now() + timedelta(hours=self.expiration_hours)

        # In production, use proper JWT library
        # Here we use a simple token format for demonstration
        token_data = f"{user_id}:{username}:{expires_at.timestamp()}:{self._hash(token)}"

        return {
            'token': token,
            'expires_at': expires_at.isoformat(),
            'token_data': token_data
        }

    def verify_token(self, token: str, token_data: str) -> Optional[Dict]:
        """Verify token validity.

        Args:
            token: Token string
            token_data: Stored token data

        Returns:
            User info if valid, None otherwise
        """
        try:
            parts = token_data.split(':')
            if len(parts) != 4:
                return None

            user_id = int(parts[0])
            username = parts[1]
            timestamp = float(parts[2])
            stored_hash = parts[3]

            # Verify token hash
            if self._hash(token) != stored_hash:
                return None

            # Check expiration
            if datetime.now().timestamp() > timestamp:
                return None

            return {
                'user_id': user_id,
                'username': username
            }
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return None

    def _hash(self, data: str) -> str:
        """Generate hash for token."""
        return hashlib.sha256(f"{data}{self.secret_key}".encode()).hexdigest()


class UserService:
    """User business logic service."""

    def __init__(self):
        """Initialize user service."""
        self.repo = UserRepository()
        self.auth_service = AuthService()

    def register(self, username: str, password: str,
                 email: Optional[str] = None,
                 phone: Optional[str] = None) -> Dict:
        """Register a new user.

        Args:
            username: Username
            password: Password
            email: Email address
            phone: Phone number

        Returns:
            User info dictionary

        Raises:
            DuplicateError: If username already exists
            ValidationError: If validation fails
        """
        # Validate input
        if not username or len(username) < 3:
            raise ValueError("Username must be at least 3 characters")
        if not password or len(password) < 6:
            raise ValueError("Password must be at least 6 characters")

        # Create user
        user_id = self.repo.insert_user(username, password, email, phone)
        logger.info(f"User registered: {username}")

        return {
            'id': user_id,
            'username': username,
            'email': email
        }

    def login(self, username: str, password: str) -> Dict:
        """User login.

        Args:
            username: Username
            password: Password

        Returns:
            Login result with token

        Raises:
            AuthenticationError: If credentials are invalid
        """
        user = self.repo.verify_password(username, password)

        # Generate token
        token_info = self.auth_service.generate_token(user.id, user.username)

        logger.info(f"User logged in: {username}")

        return {
            'token': token_info['token'],
            'expires_at': token_info['expires_at'],
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }

    def get_user_info(self, user_id: int) -> Dict:
        """Get user information.

        Args:
            user_id: User ID

        Returns:
            User info dictionary

        Raises:
            UserNotFoundError: If user not found
        """
        user = self.repo.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"user_id: {user_id}")

        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'phone': user.phone,
            'created_at': user.created_at.isoformat() if user.created_at else None
        }

    def update_user(self, user_id: int, email: Optional[str] = None,
                   phone: Optional[str] = None) -> bool:
        """Update user information.

        Args:
            user_id: User ID
            email: New email
            phone: New phone

        Returns:
            True if updated successfully
        """
        result = self.repo.update_user(user_id, email, phone)
        return result > 0

    def change_password(self, user_id: int, old_password: str,
                       new_password: str) -> bool:
        """Change user password.

        Args:
            user_id: User ID
            old_password: Old password
            new_password: New password

        Returns:
            True if password changed successfully

        Raises:
            AuthenticationError: If old password is incorrect
        """
        if len(new_password) < 6:
            raise ValueError("New password must be at least 6 characters")

        return self.repo.change_password(user_id, old_password, new_password)

    # ==================== Holdings Management ====================

    def get_holdings(self, user_id: int) -> List[Dict]:
        """Get user holdings.

        Args:
            user_id: User ID

        Returns:
            List of holding dictionaries
        """
        holdings = self.repo.get_user_holdings(user_id)
        return [h.to_dict() for h in holdings]

    def add_holding(self, user_id: int, symbol: str, shares: int,
                   cost_price: float, purchase_date: datetime) -> int:
        """Add a new holding.

        Args:
            user_id: User ID
            symbol: Stock code
            shares: Number of shares
            cost_price: Cost price per share
            purchase_date: Purchase date

        Returns:
            Holding ID
        """
        holding_id = self.repo.insert_user_holding(
            user_id=user_id,
            symbol=symbol,
            shares=shares,
            cost_price=Decimal(str(cost_price)),
            purchase_date=purchase_date.date()
        )
        logger.info(f"Holding added: user={user_id}, symbol={symbol}, shares={shares}")
        return holding_id

    def update_holding(self, user_id: int, symbol: str,
                      shares: int, cost_price: float) -> bool:
        """Update a holding.

        Args:
            user_id: User ID
            symbol: Stock code
            shares: New number of shares
            cost_price: New cost price

        Returns:
            True if updated successfully
        """
        result = self.repo.update_user_holding(
            user_id=user_id,
            symbol=symbol,
            shares=shares,
            cost_price=Decimal(str(cost_price))
        )
        return result > 0

    def delete_holding(self, user_id: int, symbol: str) -> bool:
        """Delete a holding.

        Args:
            user_id: User ID
            symbol: Stock code

        Returns:
            True if deleted successfully
        """
        result = self.repo.delete_user_holding(user_id, symbol)
        logger.info(f"Holding deleted: user={user_id}, symbol={symbol}")
        return result > 0

    # ==================== Watchlist Management (自选股) ====================

    def get_watchlist(self, user_id: int) -> List[Dict]:
        """Get user watchlist.

        Args:
            user_id: User ID

        Returns:
            List of watchlist dictionaries
        """
        watchlist = self.repo.get_watchlist(user_id)
        return [w.to_dict() for w in watchlist]

    def add_watchlist(self, user_id: int, symbol: str,
                      stock_name: str = '', notes: str = '',
                      alert_price: float = None,
                      alert_pct: float = None) -> int:
        """Add stock to watchlist.

        Args:
            user_id: User ID
            symbol: Stock code
            stock_name: Stock name
            notes: Notes
            alert_price: Alert price
            alert_pct: Alert percentage

        Returns:
            Watchlist ID
        """
        watchlist_id = self.repo.add_watchlist(
            user_id=user_id,
            symbol=symbol,
            stock_name=stock_name,
            notes=notes,
            alert_price=alert_price,
            alert_pct=alert_pct
        )
        logger.info(f"Watchlist added: user={user_id}, symbol={symbol}")
        return watchlist_id

    def update_watchlist(self, user_id: int, symbol: str,
                        stock_name: str = None, notes: str = None,
                        alert_price: float = None,
                        alert_pct: float = None) -> bool:
        """Update watchlist item.

        Args:
            user_id: User ID
            symbol: Stock code
            stock_name: Stock name
            notes: Notes
            alert_price: Alert price
            alert_pct: Alert percentage

        Returns:
            True if updated successfully
        """
        result = self.repo.update_watchlist(
            user_id=user_id,
            symbol=symbol,
            stock_name=stock_name,
            notes=notes,
            alert_price=alert_price,
            alert_pct=alert_pct
        )
        return result > 0

    def delete_watchlist(self, user_id: int, symbol: str) -> bool:
        """Delete watchlist item.

        Args:
            user_id: User ID
            symbol: Stock code

        Returns:
            True if deleted successfully
        """
        result = self.repo.delete_watchlist(user_id, symbol)
        logger.info(f"Watchlist deleted: user={user_id}, symbol={symbol}")
        return result > 0

    # ==================== User Preference ====================

    def get_preference(self, user_id: int) -> Dict:
        """Get user notification preferences.

        Args:
            user_id: User ID

        Returns:
            Preference dictionary
        """
        pref = self.repo.get_user_preference(user_id)
        if not pref:
            # Return default preference
            return UserPreference(user_id=user_id).to_dict()
        return pref.to_dict()

    def save_preference(self, user_id: int,
                       push_enabled: bool = True,
                       push_time: str = '09:30',
                       push_days: str = '1,2,3,4,5',
                       price_alert: bool = True,
                       news_alert: bool = True,
                       announcement_alert: bool = True) -> bool:
        """Save user notification preferences.

        Args:
            user_id: User ID
            push_enabled: Enable push
            push_time: Push time
            push_days: Push days
            price_alert: Enable price alert
            news_alert: Enable news alert
            announcement_alert: Enable announcement alert

        Returns:
            True if saved successfully
        """
        pref_id = self.repo.save_user_preference(
            user_id=user_id,
            push_enabled=push_enabled,
            push_time=push_time,
            push_days=push_days,
            price_alert=price_alert,
            news_alert=news_alert,
            announcement_alert=announcement_alert
        )
        logger.info(f"Preference saved: user={user_id}")
        return pref_id > 0


# Service singletons
_user_service: Optional[UserService] = None
_auth_service: Optional[AuthService] = None


def get_user_service() -> UserService:
    """Get user service instance."""
    global _user_service
    if _user_service is None:
        _user_service = UserService()
    return _user_service


def get_auth_service() -> AuthService:
    """Get auth service instance."""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service
