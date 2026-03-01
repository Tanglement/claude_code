"""Stock repository for data access layer."""

from typing import Optional, List, Tuple
from datetime import datetime, date
from decimal import Decimal

from src.db.mysql_db import get_mysql
from src.models.exceptions import DatabaseError, StockNotFoundError
from src.models.stock import StockBasic, StockRealtime, StockHistory, StockQuote


class StockRepository:
    """Stock data repository."""

    def __init__(self):
        """Initialize stock repository."""
        self.db = get_mysql()

    # ==================== Stock Basic Operations ====================

    def insert_stock_basic(self, symbol: str, name: str, market: str,
                          industry: Optional[str] = None,
                          listing_date: Optional[date] = None) -> int:
        """Insert or update stock basic information.

        Args:
            symbol: Stock code
            name: Stock name
            market: Market type (A股、港股、美股等)
            industry: Industry
            listing_date: Listing date

        Returns:
            Number of affected rows
        """
        sql = """
            INSERT INTO stock_basic (symbol, name, market, industry, listing_date)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                name = VALUES(name),
                market = VALUES(market),
                industry = VALUES(industry),
                listing_date = VALUES(listing_date)
        """
        params = (symbol, name, market, industry, listing_date)
        return self.db.execute(sql, params)

    def get_stock_basic(self, symbol: str) -> Optional[StockBasic]:
        """Get stock basic information by symbol.

        Args:
            symbol: Stock code

        Returns:
            StockBasic instance or None
        """
        sql = """
            SELECT symbol, name, market, full_name, industry,
                   listing_date, delisting_date, status,
                   created_at, updated_at
            FROM stock_basic
            WHERE symbol = %s
        """
        result = self.db.query_one(sql, (symbol,))
        if not result:
            return None

        return StockBasic(
            symbol=result['symbol'],
            name=result['name'],
            market=result['market'],
            full_name=result.get('full_name'),
            industry=result.get('industry'),
            listing_date=result.get('listing_date'),
            delisting_date=result.get('delisting_date'),
            status=result.get('status', '正常'),
            created_at=result.get('created_at'),
            updated_at=result.get('updated_at')
        )

    def get_all_stocks(self, market: Optional[str] = None,
                       limit: int = 1000) -> List[StockBasic]:
        """Get all stocks.

        Args:
            market: Filter by market type
            limit: Maximum number of records

        Returns:
            List of StockBasic instances
        """
        if market:
            sql = """
                SELECT symbol, name, market, full_name, industry,
                       listing_date, delisting_date, status,
                       created_at, updated_at
                FROM stock_basic
                WHERE market = %s
                ORDER BY symbol
                LIMIT %s
            """
            params = (market, limit)
        else:
            sql = """
                SELECT symbol, name, market, full_name, industry,
                       listing_date, delisting_date, status,
                       created_at, updated_at
                FROM stock_basic
                ORDER BY symbol
                LIMIT %s
            """
            params = (limit,)

        results = self.db.query_all(sql, params)
        stocks = []
        for result in results:
            stocks.append(StockBasic(
                symbol=result['symbol'],
                name=result['name'],
                market=result['market'],
                full_name=result.get('full_name'),
                industry=result.get('industry'),
                listing_date=result.get('listing_date'),
                delisting_date=result.get('delisting_date'),
                status=result.get('status', '正常'),
                created_at=result.get('created_at'),
                updated_at=result.get('updated_at')
            ))
        return stocks

    # ==================== Stock Realtime Operations ====================

    def insert_stock_realtime(self, symbol: str, price: Decimal, change: Decimal,
                              change_pct: Decimal, open_price: Decimal,
                              high: Decimal, low: Decimal, close_yest: Decimal,
                              volume: int, amount: Decimal,
                              turnover: Decimal = Decimal('0'),
                              pe: Optional[Decimal] = None,
                              pb: Optional[Decimal] = None,
                              datetime: Optional[datetime] = None) -> int:
        """Insert stock realtime quote.

        Args:
            symbol: Stock code
            price: Current price
            change: Change amount
            change_pct: Change percentage
            open_price: Open price
            high: High price
            low: Low price
            close_yest: Yesterday close price
            volume: Volume
            amount: Amount
            turnover: Turnover rate
            pe: P/E ratio
            pb: P/B ratio
            datetime: Quote timestamp

        Returns:
            Number of affected rows
        """
        sql = """
            INSERT INTO stock_realtime (
                symbol, price, change, change_pct, open, high, low,
                close_yest, volume, amount, turnover, pe, pb, datetime
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            symbol, price, change, change_pct, open_price, high, low,
            close_yest, volume, amount, turnover, pe, pb, datetime
        )
        return self.db.execute(sql, params)

    def get_stock_realtime(self, symbol: str) -> Optional[StockRealtime]:
        """Get stock realtime quote by symbol.

        Args:
            symbol: Stock code

        Returns:
            StockRealtime instance or None
        """
        sql = """
            SELECT symbol, price, change, change_pct, open, high, low,
                   close_yest, volume, amount, turnover, pe, pb, datetime,
                   created_at
            FROM stock_realtime
            WHERE symbol = %s
            ORDER BY datetime DESC
            LIMIT 1
        """
        result = self.db.query_one(sql, (symbol,))
        if not result:
            return None

        return StockRealtime(
            symbol=result['symbol'],
            price=result['price'],
            change=result['change'],
            change_pct=result['change_pct'],
            open=result['open'],
            high=result['high'],
            low=result['low'],
            close_yest=result['close_yest'],
            volume=result['volume'],
            amount=result['amount'],
            turnover=result.get('turnover', 0),
            pe=result.get('pe'),
            pb=result.get('pb'),
            datetime=result.get('datetime'),
            created_at=result.get('created_at')
        )

    # ==================== Stock History Operations ====================

    def insert_stock_history(self, symbol: str, trade_date: date,
                             open_price: Decimal, high: Decimal, low: Decimal,
                             close: Decimal, volume: int, amount: Decimal,
                             adj_close: Optional[Decimal] = None,
                             change_pct: Optional[Decimal] = None) -> int:
        """Insert stock history data.

        Args:
            symbol: Stock code
            trade_date: Trade date
            open_price: Open price
            high: High price
            low: Low price
            close: Close price
            volume: Volume
            amount: Amount
            adj_close: Adjusted close price
            change_pct: Change percentage

        Returns:
            Number of affected rows
        """
        sql = """
            INSERT INTO stock_history (
                symbol, trade_date, open, high, low, close,
                volume, amount, adj_close, change_pct
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                open = VALUES(open),
                high = VALUES(high),
                low = VALUES(low),
                close = VALUES(close),
                volume = VALUES(volume),
                amount = VALUES(amount),
                adj_close = VALUES(adj_close),
                change_pct = VALUES(change_pct)
        """
        params = (
            symbol, trade_date, open_price, high, low, close,
            volume, amount, adj_close, change_pct
        )
        return self.db.execute(sql, params)

    def get_stock_history(self, symbol: str,
                          start_date: Optional[date] = None,
                          end_date: Optional[date] = None,
                          limit: int = 100) -> List[StockHistory]:
        """Get stock history data.

        Args:
            symbol: Stock code
            start_date: Start date
            end_date: End date
            limit: Maximum number of records

        Returns:
            List of StockHistory instances
        """
        if start_date and end_date:
            sql = """
                SELECT symbol, trade_date, open, high, low, close,
                       volume, amount, adj_close, change_pct, created_at
                FROM stock_history
                WHERE symbol = %s AND trade_date BETWEEN %s AND %s
                ORDER BY trade_date DESC
                LIMIT %s
            """
            params = (symbol, start_date, end_date, limit)
        elif start_date:
            sql = """
                SELECT symbol, trade_date, open, high, low, close,
                       volume, amount, adj_close, change_pct, created_at
                FROM stock_history
                WHERE symbol = %s AND trade_date >= %s
                ORDER BY trade_date DESC
                LIMIT %s
            """
            params = (symbol, start_date, limit)
        elif end_date:
            sql = """
                SELECT symbol, trade_date, open, high, low, close,
                       volume, amount, adj_close, change_pct, created_at
                FROM stock_history
                WHERE symbol = %s AND trade_date <= %s
                ORDER BY trade_date DESC
                LIMIT %s
            """
            params = (symbol, end_date, limit)
        else:
            sql = """
                SELECT symbol, trade_date, open, high, low, close,
                       volume, amount, adj_close, change_pct, created_at
                FROM stock_history
                WHERE symbol = %s
                ORDER BY trade_date DESC
                LIMIT %s
            """
            params = (symbol, limit)

        results = self.db.query_all(sql, params)
        history = []
        for result in results:
            history.append(StockHistory(
                symbol=result['symbol'],
                trade_date=result['trade_date'],
                open=result['open'],
                high=result['high'],
                low=result['low'],
                close=result['close'],
                volume=result['volume'],
                amount=result['amount'],
                adj_close=result.get('adj_close'),
                change_pct=result.get('change_pct'),
                created_at=result.get('created_at')
            ))
        return history

    # ==================== Utility Methods ====================

    def get_stock_with_realtime(self, symbol: str) -> Optional[StockQuote]:
        """Get stock with realtime quote.

        Args:
            symbol: Stock code

        Returns:
            StockQuote instance or None
        """
        basic = self.get_stock_basic(symbol)
        if not basic:
            return None

        realtime = self.get_stock_realtime(symbol)

        quote = StockQuote(
            symbol=basic.symbol,
            name=basic.name
        )

        if realtime:
            quote.price = realtime.price
            quote.change = realtime.change
            quote.change_pct = realtime.change_pct
            quote.open = realtime.open
            quote.high = realtime.high
            quote.low = realtime.low
            quote.close_yest = realtime.close_yest
            quote.volume = realtime.volume
            quote.amount = realtime.amount
            quote.turnover = realtime.turnover
            quote.pe = realtime.pe
            quote.pb = realtime.pb
            quote.datetime = realtime.datetime

        return quote
