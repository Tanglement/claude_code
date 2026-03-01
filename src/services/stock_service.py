"""Stock business logic service."""

from typing import Optional, List, Dict
from datetime import date, datetime
from decimal import Decimal

from src.repositories.stock_repo import StockRepository
from src.models.stock import StockBasic, StockRealtime, StockHistory, StockQuote
from src.models.exceptions import StockNotFoundError, DatabaseError
from src.utils.logger import get_logger

logger = get_logger(__name__)


class StockService:
    """Stock business logic service."""

    def __init__(self):
        """Initialize stock service."""
        self.repo = StockRepository()

    def get_stock_quote(self, symbol: str) -> Dict:
        """Get stock quote with basic info and realtime data.

        Args:
            symbol: Stock code

        Returns:
            Dictionary with stock quote data

        Raises:
            StockNotFoundError: If stock not found
        """
        quote = self.repo.get_stock_with_realtime(symbol)
        if not quote:
            raise StockNotFoundError(symbol)

        return quote.to_dict()

    def get_stock_basic(self, symbol: str) -> Dict:
        """Get stock basic information.

        Args:
            symbol: Stock code

        Returns:
            Dictionary with basic info

        Raises:
            StockNotFoundError: If stock not found
        """
        stock = self.repo.get_stock_basic(symbol)
        if not stock:
            raise StockNotFoundError(symbol)

        return {
            'symbol': stock.symbol,
            'name': stock.name,
            'market': stock.market,
            'industry': stock.industry,
            'listing_date': stock.listing_date.isoformat() if stock.listing_date else None,
            'status': stock.status
        }

    def get_all_stocks(self, market: Optional[str] = None, limit: int = 1000) -> List[Dict]:
        """Get all stocks.

        Args:
            market: Filter by market type
            limit: Maximum number of records

        Returns:
            List of stock dictionaries
        """
        stocks = self.repo.get_all_stocks(market=market, limit=limit)
        return [
            {
                'symbol': s.symbol,
                'name': s.name,
                'market': s.market,
                'industry': s.industry,
                'status': s.status
            }
            for s in stocks
        ]

    def get_realtime_quote(self, symbol: str) -> Dict:
        """Get stock realtime quote.

        Args:
            symbol: Stock code

        Returns:
            Dictionary with realtime data

        Raises:
            StockNotFoundError: If quote not found
        """
        realtime = self.repo.get_stock_realtime(symbol)
        if not realtime:
            raise StockNotFoundError(f"No realtime data for {symbol}")

        return {
            'symbol': realtime.symbol,
            'price': float(realtime.price),
            'change': float(realtime.change),
            'change_pct': float(realtime.change_pct),
            'open': float(realtime.open),
            'high': float(realtime.high),
            'low': float(realtime.low),
            'close_yest': float(realtime.close_yest),
            'volume': realtime.volume,
            'amount': float(realtime.amount),
            'turnover': float(realtime.turnover),
            'pe': float(realtime.pe) if realtime.pe else None,
            'pb': float(realtime.pb) if realtime.pb else None,
            'datetime': realtime.datetime.isoformat() if realtime.datetime else None
        }

    def get_history(self, symbol: str,
                   start_date: Optional[date] = None,
                   end_date: Optional[date] = None,
                   limit: int = 100) -> List[Dict]:
        """Get stock history data.

        Args:
            symbol: Stock code
            start_date: Start date
            end_date: End date
            limit: Maximum number of records

        Returns:
            List of history data dictionaries
        """
        history = self.repo.get_stock_history(symbol, start_date, end_date, limit)
        return [
            {
                'symbol': h.symbol,
                'trade_date': h.trade_date.isoformat(),
                'open': float(h.open),
                'high': float(h.high),
                'low': float(h.low),
                'close': float(h.close),
                'volume': h.volume,
                'amount': float(h.amount),
                'change_pct': float(h.change_pct) if h.change_pct else None
            }
            for h in history
        ]

    def save_realtime_data(self, quote_data: Dict) -> bool:
        """Save realtime quote data.

        Args:
            quote_data: Quote data dictionary

        Returns:
            True if saved successfully
        """
        try:
            self.repo.insert_stock_realtime(
                symbol=quote_data['symbol'],
                price=Decimal(str(quote_data['price'])),
                change=Decimal(str(quote_data.get('change', 0))),
                change_pct=Decimal(str(quote_data.get('change_pct', 0))),
                open_price=Decimal(str(quote_data['open'])),
                high=Decimal(str(quote_data['high'])),
                low=Decimal(str(quote_data['low'])),
                close_yest=Decimal(str(quote_data.get('close_yest', 0))),
                volume=int(quote_data['volume']),
                amount=Decimal(str(quote_data.get('amount', 0))),
                turnover=Decimal(str(quote_data.get('turnover', 0))),
                pe=Decimal(str(quote_data['pe'])) if quote_data.get('pe') else None,
                pb=Decimal(str(quote_data['pb'])) if quote_data.get('pb') else None,
                datetime=datetime.now()
            )
            return True
        except Exception as e:
            logger.error(f"Failed to save realtime data: {e}")
            return False

    def save_history_data(self, history_data: Dict) -> bool:
        """Save history data.

        Args:
            history_data: History data dictionary

        Returns:
            True if saved successfully
        """
        try:
            self.repo.insert_stock_history(
                symbol=history_data['symbol'],
                trade_date=history_data['trade_date'],
                open_price=Decimal(str(history_data['open'])),
                high=Decimal(str(history_data['high'])),
                low=Decimal(str(history_data['low'])),
                close=Decimal(str(history_data['close'])),
                volume=int(history_data['volume']),
                amount=Decimal(str(history_data.get('amount', 0))),
                adj_close=Decimal(str(history_data['adj_close'])) if history_data.get('adj_close') else None,
                change_pct=Decimal(str(history_data['change_pct'])) if history_data.get('change_pct') else None
            )
            return True
        except Exception as e:
            logger.error(f"Failed to save history data: {e}")
            return False


# Service singleton
_stock_service: Optional[StockService] = None


def get_stock_service() -> StockService:
    """Get stock service instance."""
    global _stock_service
    if _stock_service is None:
        _stock_service = StockService()
    return _stock_service
