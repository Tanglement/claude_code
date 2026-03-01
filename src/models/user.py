"""User data models."""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional
from decimal import Decimal


@dataclass
class User:
    """User model."""
    id: Optional[int] = None
    username: str = ''
    password: str = ''  # Hashed password
    email: Optional[str] = None
    phone: Optional[str] = None
    created_at: Optional[datetime] = None

    def to_dict(self, include_password: bool = False) -> dict:
        """Convert to dictionary."""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'phone': self.phone,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if include_password:
            data['password'] = self.password
        return data


@dataclass
class UserHolding:
    """User stock holding model."""
    id: Optional[int] = None
    user_id: int = 0
    symbol: str = ''
    shares: int = 0  # 持股数量
    cost_price: Decimal = field(default_factory=lambda: Decimal('0'))  # 成本价
    purchase_date: Optional[date] = None
    created_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'symbol': self.symbol,
            'shares': self.shares,
            'cost_price': float(self.cost_price),
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


@dataclass
class UserSession:
    """User session model."""
    session_id: str
    user_id: int
    username: str
    token: str
    expires_at: datetime

    def is_expired(self) -> bool:
        """Check if session is expired."""
        return datetime.now() > self.expires_at


@dataclass
class UserWatchlist:
    """User watchlist (自选股) model."""
    id: Optional[int] = None
    user_id: int = 0
    symbol: str = ''
    stock_name: str = ''  # 股票名称
    notes: str = ''  # 备注
    alert_price: Optional[float] = None  # 预警价格
    alert_pct: Optional[float] = None  # 预警涨跌幅
    created_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'symbol': self.symbol,
            'stock_name': self.stock_name,
            'notes': self.notes,
            'alert_price': self.alert_price,
            'alert_pct': self.alert_pct,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


@dataclass
class UserPreference:
    """User notification preferences."""
    id: Optional[int] = None
    user_id: int = 0
    push_enabled: bool = True  # 是否启用推送
    push_time: str = '09:30'  # 推送时间 (HH:MM)
    push_days: str = '1,2,3,4,5'  # 推送日期 (1-7, 逗号分隔)
    price_alert: bool = True  # 价格预警
    news_alert: bool = True  # 新闻预警
    announcement_alert: bool = True  # 公告预警
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'push_enabled': self.push_enabled,
            'push_time': self.push_time,
            'push_days': self.push_days,
            'price_alert': self.price_alert,
            'news_alert': self.news_alert,
            'announcement_alert': self.announcement_alert,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
