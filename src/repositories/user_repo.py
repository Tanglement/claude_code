"""User repository for data access layer."""

from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
import hashlib

from src.db.mysql_db import get_mysql
from src.models.exceptions import (
    DatabaseError, UserNotFoundError,
    AuthenticationError, DuplicateError
)
from src.models.user import User, UserHolding, UserWatchlist, UserPreference


class UserRepository:
    """User data repository."""

    def __init__(self):
        """Initialize user repository."""
        self.db = get_mysql()

    # ==================== User Operations ====================

    def _hash_password(self, password: str) -> str:
        """Hash password using SHA256.

        Args:
            password: Plain text password

        Returns:
            Hashed password
        """
        return hashlib.sha256(password.encode()).hexdigest()

    def insert_user(self, username: str, password: str,
                    email: Optional[str] = None,
                    phone: Optional[str] = None) -> int:
        """Insert a new user.

        Args:
            username: Username
            password: Password (will be hashed)
            email: Email address
            phone: Phone number

        Returns:
            User ID

        Raises:
            DuplicateError: If username already exists
        """
        # Check if username exists
        existing = self.get_user_by_username(username)
        if existing:
            raise DuplicateError('User', f'username: {username}')

        hashed_password = self._hash_password(password)
        sql = """
            INSERT INTO user_info (username, password, email, phone)
            VALUES (%s, %s, %s, %s)
        """
        params = (username, hashed_password, email, phone)
        return self.db.insert(sql, params)

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username.

        Args:
            username: Username

        Returns:
            User instance or None
        """
        sql = """
            SELECT id, username, password, email, phone, created_at
            FROM user_info
            WHERE username = %s
        """
        result = self.db.query_one(sql, (username,))
        if not result:
            return None

        return User(
            id=result['id'],
            username=result['username'],
            password=result['password'],
            email=result.get('email'),
            phone=result.get('phone'),
            created_at=result.get('created_at')
        )

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User instance or None
        """
        sql = """
            SELECT id, username, password, email, phone, created_at
            FROM user_info
            WHERE id = %s
        """
        result = self.db.query_one(sql, (user_id,))
        if not result:
            return None

        return User(
            id=result['id'],
            username=result['username'],
            password=result['password'],
            email=result.get('email'),
            phone=result.get('phone'),
            created_at=result.get('created_at')
        )

    def verify_password(self, username: str, password: str) -> Optional[User]:
        """Verify user credentials.

        Args:
            username: Username
            password: Plain text password

        Returns:
            User instance if credentials are valid

        Raises:
            AuthenticationError: If credentials are invalid
        """
        user = self.get_user_by_username(username)
        if not user:
            raise AuthenticationError("Invalid username or password")

        hashed_password = self._hash_password(password)
        if user.password != hashed_password:
            raise AuthenticationError("Invalid username or password")

        return user

    def update_user(self, user_id: int, email: Optional[str] = None,
                    phone: Optional[str] = None) -> int:
        """Update user information.

        Args:
            user_id: User ID
            email: New email
            phone: New phone

        Returns:
            Number of affected rows
        """
        updates = []
        params = []

        if email is not None:
            updates.append("email = %s")
            params.append(email)
        if phone is not None:
            updates.append("phone = %s")
            params.append(phone)

        if not updates:
            return 0

        params.append(user_id)
        sql = f"UPDATE user_info SET {', '.join(updates)} WHERE id = %s"
        return self.db.execute(sql, tuple(params))

    def change_password(self, user_id: int, old_password: str,
                        new_password: str) -> bool:
        """Change user password.

        Args:
            user_id: User ID
            old_password: Old password
            new_password: New password

        Returns:
            True if password was changed

        Raises:
            AuthenticationError: If old password is incorrect
        """
        user = self.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"user_id: {user_id}")

        old_hash = self._hash_password(old_password)
        if user.password != old_hash:
            raise AuthenticationError("Old password is incorrect")

        new_hash = self._hash_password(new_password)
        sql = "UPDATE user_info SET password = %s WHERE id = %s"
        self.db.execute(sql, (new_hash, user_id))
        return True

    # ==================== User Holdings Operations ====================

    def insert_user_holding(self, user_id: int, symbol: str, shares: int,
                            cost_price: Decimal,
                            purchase_date: date) -> int:
        """Insert user stock holding.

        Args:
            user_id: User ID
            symbol: Stock code
            shares: Number of shares
            cost_price: Cost price per share
            purchase_date: Purchase date

        Returns:
            Holding ID
        """
        sql = """
            INSERT INTO user_holdings (user_id, symbol, shares, cost_price, purchase_date)
            VALUES (%s, %s, %s, %s, %s)
        """
        params = (user_id, symbol, shares, cost_price, purchase_date)
        return self.db.insert(sql, params)

    def get_user_holdings(self, user_id: int) -> List[UserHolding]:
        """Get user stock holdings.

        Args:
            user_id: User ID

        Returns:
            List of UserHolding instances
        """
        sql = """
            SELECT id, user_id, symbol, shares, cost_price, purchase_date, created_at
            FROM user_holdings
            WHERE user_id = %s
            ORDER BY created_at DESC
        """
        results = self.db.query_all(sql, (user_id,))
        holdings = []
        for result in results:
            holdings.append(UserHolding(
                id=result['id'],
                user_id=result['user_id'],
                symbol=result['symbol'],
                shares=result['shares'],
                cost_price=result['cost_price'],
                purchase_date=result['purchase_date'],
                created_at=result.get('created_at')
            ))
        return holdings

    def get_user_holding(self, user_id: int, symbol: str) -> Optional[UserHolding]:
        """Get user holding for specific stock.

        Args:
            user_id: User ID
            symbol: Stock code

        Returns:
            UserHolding instance or None
        """
        sql = """
            SELECT id, user_id, symbol, shares, cost_price, purchase_date, created_at
            FROM user_holdings
            WHERE user_id = %s AND symbol = %s
        """
        result = self.db.query_one(sql, (user_id, symbol))
        if not result:
            return None

        return UserHolding(
            id=result['id'],
            user_id=result['user_id'],
            symbol=result['symbol'],
            shares=result['shares'],
            cost_price=result['cost_price'],
            purchase_date=result['purchase_date'],
            created_at=result.get('created_at')
        )

    def update_user_holding(self, user_id: int, symbol: str,
                            shares: int, cost_price: Decimal) -> int:
        """Update user holding.

        Args:
            user_id: User ID
            symbol: Stock code
            shares: New number of shares
            cost_price: New cost price

        Returns:
            Number of affected rows
        """
        sql = """
            UPDATE user_holdings
            SET shares = %s, cost_price = %s
            WHERE user_id = %s AND symbol = %s
        """
        return self.db.execute(sql, (shares, cost_price, user_id, symbol))

    def delete_user_holding(self, user_id: int, symbol: str) -> int:
        """Delete user holding.

        Args:
            user_id: User ID
            symbol: Stock code

        Returns:
            Number of affected rows
        """
        sql = """
            DELETE FROM user_holdings
            WHERE user_id = %s AND symbol = %s
        """
        return self.db.execute(sql, (user_id, symbol))

    # ==================== Utility Methods ====================

    def calculate_portfolio_value(self, user_id: int,
                                   stock_prices: dict) -> dict:
        """Calculate portfolio value.

        Args:
            user_id: User ID
            stock_prices: Dictionary of symbol -> current price

        Returns:
            Portfolio summary
        """
        holdings = self.get_user_holdings(user_id)

        total_cost = Decimal('0')
        total_value = Decimal('0')
        positions = []

        for holding in holdings:
            current_price = stock_prices.get(holding.symbol, holding.cost_price)
            cost = holding.cost_price * holding.shares
            value = current_price * holding.shares
            profit = value - cost
            profit_pct = (profit / cost * 100) if cost > 0 else Decimal('0')

            total_cost += cost
            total_value += value

            positions.append({
                'symbol': holding.symbol,
                'shares': holding.shares,
                'cost_price': float(holding.cost_price),
                'current_price': float(current_price),
                'cost': float(cost),
                'value': float(value),
                'profit': float(profit),
                'profit_pct': float(profit_pct)
            })

        total_profit = total_value - total_cost
        total_profit_pct = (total_profit / total_cost * 100) if total_cost > 0 else Decimal('0')

        return {
            'total_cost': float(total_cost),
            'total_value': float(total_value),
            'total_profit': float(total_profit),
            'total_profit_pct': float(total_profit_pct),
            'positions': positions
        }

    # ==================== Watchlist Operations (自选股) ====================

    def add_watchlist(self, user_id: int, symbol: str,
                      stock_name: str = '', notes: str = '',
                      alert_price: float = None,
                      alert_pct: float = None) -> int:
        """Add stock to user watchlist.

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
        # Check if already exists
        existing = self.get_watchlist_item(user_id, symbol)
        if existing:
            # Update instead
            return self.update_watchlist(user_id, symbol, stock_name, notes, alert_price, alert_pct)

        sql = """
            INSERT INTO user_watchlist (user_id, symbol, stock_name, notes, alert_price, alert_pct)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (user_id, symbol, stock_name, notes, alert_price, alert_pct)
        return self.db.insert(sql, params)

    def get_watchlist(self, user_id: int) -> List[UserWatchlist]:
        """Get user watchlist.

        Args:
            user_id: User ID

        Returns:
            List of UserWatchlist instances
        """
        sql = """
            SELECT id, user_id, symbol, stock_name, notes, alert_price, alert_pct, created_at
            FROM user_watchlist
            WHERE user_id = %s
            ORDER BY created_at DESC
        """
        results = self.db.query_all(sql, (user_id,))
        watchlist = []
        for result in results:
            watchlist.append(UserWatchlist(
                id=result['id'],
                user_id=result['user_id'],
                symbol=result['symbol'],
                stock_name=result.get('stock_name', ''),
                notes=result.get('notes', ''),
                alert_price=result.get('alert_price'),
                alert_pct=result.get('alert_pct'),
                created_at=result.get('created_at')
            ))
        return watchlist

    def get_watchlist_item(self, user_id: int, symbol: str) -> Optional[UserWatchlist]:
        """Get watchlist item for specific stock.

        Args:
            user_id: User ID
            symbol: Stock code

        Returns:
            UserWatchlist instance or None
        """
        sql = """
            SELECT id, user_id, symbol, stock_name, notes, alert_price, alert_pct, created_at
            FROM user_watchlist
            WHERE user_id = %s AND symbol = %s
        """
        result = self.db.query_one(sql, (user_id, symbol))
        if not result:
            return None

        return UserWatchlist(
            id=result['id'],
            user_id=result['user_id'],
            symbol=result['symbol'],
            stock_name=result.get('stock_name', ''),
            notes=result.get('notes', ''),
            alert_price=result.get('alert_price'),
            alert_pct=result.get('alert_pct'),
            created_at=result.get('created_at')
        )

    def update_watchlist(self, user_id: int, symbol: str,
                        stock_name: str = None, notes: str = None,
                        alert_price: float = None,
                        alert_pct: float = None) -> int:
        """Update watchlist item.

        Args:
            user_id: User ID
            symbol: Stock code
            stock_name: Stock name
            notes: Notes
            alert_price: Alert price
            alert_pct: Alert percentage

        Returns:
            Number of affected rows
        """
        updates = []
        params = []

        if stock_name is not None:
            updates.append("stock_name = %s")
            params.append(stock_name)
        if notes is not None:
            updates.append("notes = %s")
            params.append(notes)
        if alert_price is not None:
            updates.append("alert_price = %s")
            params.append(alert_price)
        if alert_pct is not None:
            updates.append("alert_pct = %s")
            params.append(alert_pct)

        if not updates:
            return 0

        params.extend([user_id, symbol])
        sql = f"UPDATE user_watchlist SET {', '.join(updates)} WHERE user_id = %s AND symbol = %s"
        return self.db.execute(sql, tuple(params))

    def delete_watchlist(self, user_id: int, symbol: str) -> int:
        """Delete watchlist item.

        Args:
            user_id: User ID
            symbol: Stock code

        Returns:
            Number of affected rows
        """
        sql = """
            DELETE FROM user_watchlist
            WHERE user_id = %s AND symbol = %s
        """
        return self.db.execute(sql, (user_id, symbol))

    # ==================== User Preference Operations ====================

    def get_user_preference(self, user_id: int) -> Optional[UserPreference]:
        """Get user notification preferences.

        Args:
            user_id: User ID

        Returns:
            UserPreference instance or None
        """
        sql = """
            SELECT id, user_id, push_enabled, push_time, push_days,
                   price_alert, news_alert, announcement_alert,
                   created_at, updated_at
            FROM user_preference
            WHERE user_id = %s
        """
        result = self.db.query_one(sql, (user_id,))
        if not result:
            return None

        return UserPreference(
            id=result['id'],
            user_id=result['user_id'],
            push_enabled=result.get('push_enabled', True),
            push_time=result.get('push_time', '09:30'),
            push_days=result.get('push_days', '1,2,3,4,5'),
            price_alert=result.get('price_alert', True),
            news_alert=result.get('news_alert', True),
            announcement_alert=result.get('announcement_alert', True),
            created_at=result.get('created_at'),
            updated_at=result.get('updated_at')
        )

    def save_user_preference(self, user_id: int,
                             push_enabled: bool = True,
                             push_time: str = '09:30',
                             push_days: str = '1,2,3,4,5',
                             price_alert: bool = True,
                             news_alert: bool = True,
                             announcement_alert: bool = True) -> int:
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
            Preference ID
        """
        existing = self.get_user_preference(user_id)

        if existing:
            sql = """
                UPDATE user_preference SET
                    push_enabled = %s, push_time = %s, push_days = %s,
                    price_alert = %s, news_alert = %s, announcement_alert = %s,
                    updated_at = NOW()
                WHERE user_id = %s
            """
            params = (push_enabled, push_time, push_days,
                     price_alert, news_alert, announcement_alert, user_id)
            self.db.execute(sql, params)
            return existing.id
        else:
            sql = """
                INSERT INTO user_preference
                    (user_id, push_enabled, push_time, push_days,
                     price_alert, news_alert, announcement_alert)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            params = (user_id, push_enabled, push_time, push_days,
                     price_alert, news_alert, announcement_alert)
            return self.db.insert(sql, params)
