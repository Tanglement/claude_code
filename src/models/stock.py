"""Stock data models."""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal


@dataclass
class StockBasic:
    """Stock basic information model."""
    symbol: str
    name: str
    market: str  # A股、港股、美股等
    full_name: Optional[str] = None
    industry: Optional[str] = None
    listing_date: Optional[date] = None
    delisting_date: Optional[date] = None
    status: str = '正常'  # 正常、ST、*ST、退市
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class StockRealtime:
    """Stock realtime quote model."""
    symbol: str
    price: Decimal
    change: Decimal  # 涨跌额
    change_pct: Decimal  # 涨跌幅(%)
    open: Decimal  # 开盘价
    high: Decimal  # 最高价
    low: Decimal  # 最低价
    close_yest: Decimal  # 昨收价
    volume: int  # 成交量(股)
    amount: Decimal  # 成交额(万元)
    turnover: Decimal = field(default_factory=lambda: Decimal('0'))  # 换手率(%)
    pe: Optional[Decimal] = None  # 市盈率
    pb: Optional[Decimal] = None  # 市净率
    datetime: Optional[datetime] = None
    created_at: Optional[datetime] = None


@dataclass
class StockHistory:
    """Stock history data model."""
    symbol: str
    trade_date: date
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int
    amount: Decimal
    adj_close: Optional[Decimal] = None  # 复权收盘价
    change_pct: Optional[Decimal] = None  # 涨跌幅(%)
    created_at: Optional[datetime] = None


@dataclass
class StockQuote:
    """Unified stock quote model (internal format)."""
    symbol: str
    name: str
    price: Decimal = field(default_factory=lambda: Decimal('0'))
    change: Decimal = field(default_factory=lambda: Decimal('0'))
    change_pct: Decimal = field(default_factory=lambda: Decimal('0'))
    open: Decimal = field(default_factory=lambda: Decimal('0'))
    high: Decimal = field(default_factory=lambda: Decimal('0'))
    low: Decimal = field(default_factory=lambda: Decimal('0'))
    close_yest: Decimal = field(default_factory=lambda: Decimal('0'))
    volume: int = 0
    amount: Decimal = field(default_factory=lambda: Decimal('0'))
    turnover: Decimal = field(default_factory=lambda: Decimal('0'))
    pe: Optional[Decimal] = None
    pb: Optional[Decimal] = None
    datetime: Optional[datetime] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'symbol': self.symbol,
            'name': self.name,
            'price': float(self.price),
            'change': float(self.change),
            'change_pct': float(self.change_pct),
            'open': float(self.open),
            'high': float(self.high),
            'low': float(self.low),
            'close_yest': float(self.close_yest),
            'volume': self.volume,
            'amount': float(self.amount),
            'turnover': float(self.turnover),
            'pe': float(self.pe) if self.pe else None,
            'pb': float(self.pb) if self.pb else None,
            'datetime': self.datetime.isoformat() if self.datetime else None
        }
