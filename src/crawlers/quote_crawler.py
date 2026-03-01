"""Stock quote crawler."""

import re
from typing import Optional, Dict, List
from datetime import datetime
from decimal import Decimal

from .base import BaseCrawler
from src.utils.logger import get_logger

logger = get_logger(__name__)


class QuoteCrawler(BaseCrawler):
    """Crawler for stock realtime quotes."""

    def __init__(self):
        """Initialize quote crawler."""
        super().__init__(timeout=10)

    def get_quote_sina(self, symbol: str) -> Optional[Dict]:
        """Get quote from Sina Finance.

        Args:
            symbol: Stock code (e.g., sh600519, sz000001)

        Returns:
            Quote dictionary or None
        """
        # Determine exchange prefix
        if symbol.startswith('6') or symbol.startswith('9'):
            prefix = 'sh'
        elif symbol.startswith('0') or symbol.startswith('3'):
            prefix = 'sz'
        elif symbol.startswith('5'):
            prefix = 'sh'  # 基金
        elif symbol.startswith('8') or symbol.startswith('4'):
            prefix = 'bj'  # 北京
        else:
            prefix = 'sh'

        url = f"https://hq.sinajs.cn/list={prefix}{symbol}"

        response = self.get(url, delay=0.5)
        if not response:
            return None

        try:
            # Parse response
            text = response.text
            match = re.search(r'="(.+)"', text)

            if not match:
                return None

            data = match.group(1).split(',')

            if len(data) < 10:
                logger.warning(f"Incomplete data for {symbol}")
                return None

            # Parse quote data
            quote = {
                'symbol': symbol,
                'name': data[0],
                'open': self._parse_number(data[1]),
                'close_yest': self._parse_number(data[2]),
                'price': self._parse_number(data[3]),
                'high': self._parse_number(data[4]),
                'low': self._parse_number(data[5]),
                'volume': self._parse_number(data[8]),
                'amount': self._parse_number(data[9]),
                'datetime': datetime.now()
            }

            # Calculate change and change_pct
            if quote['close_yest'] and quote['close_yest'] > 0:
                quote['change'] = quote['price'] - quote['close_yest']
                quote['change_pct'] = (quote['change'] / quote['close_yest']) * 100
            else:
                quote['change'] = Decimal('0')
                quote['change_pct'] = Decimal('0')

            return quote

        except Exception as e:
            logger.error(f"Failed to parse quote for {symbol}: {e}")
            return None

    def get_quote_eastmoney(self, symbol: str) -> Optional[Dict]:
        """Get quote from East Money.

        Args:
            symbol: Stock code

        Returns:
            Quote dictionary or None
        """
        # Convert to East Money format
        if symbol.startswith('6'):
            market = '1'
        elif symbol.startswith('0'):
            market = '0'
        elif symbol.startswith('3'):
            market = '0'
        else:
            market = '1'

        url = f"https://push2.eastmoney.com/api/qt/stock/get"
        params = {
            'ut': 'fa5fd1943c7b386f172d6893dbfba10b',
            'invt': '2',
            'fltt': '2',
            'fields': 'f43,f44,f45,f46,f47,f48,f50,f51,f52,f55,f57,f58,f59,f60,f116,f117,f162,f167,f168,f169,f170,f171,f173,f177',
            'secid': f"{market}.{symbol}"
        }

        response = self.get(url, params=params, delay=0.5)
        if not response:
            return None

        try:
            data = response.json()
            if data.get('data') is None:
                return None

            d = data['data']

            quote = {
                'symbol': symbol,
                'name': d.get('f58', ''),
                'price': Decimal(str(d.get('f43', 0))) / 100 if d.get('f43') else Decimal('0'),
                'change': Decimal(str(d.get('f44', 0))) / 100 if d.get('f44') else Decimal('0'),
                'change_pct': Decimal(str(d.get('f45', 0))) / 100 if d.get('f45') else Decimal('0'),
                'open': Decimal(str(d.get('f46', 0))) / 100 if d.get('f46') else Decimal('0'),
                'high': Decimal(str(d.get('f47', 0))) / 100 if d.get('f47') else Decimal('0'),
                'low': Decimal(str(d.get('f48', 0))) / 100 if d.get('f48') else Decimal('0'),
                'close_yest': Decimal(str(d.get('f50', 0))) / 100 if d.get('f50') else Decimal('0'),
                'volume': d.get('f52', 0),
                'amount': Decimal(str(d.get('f51', 0))) / 10000 if d.get('f51') else Decimal('0'),
                'datetime': datetime.now()
            }

            return quote

        except Exception as e:
            logger.error(f"Failed to parse East Money quote for {symbol}: {e}")
            return None

    def get_quotes_batch(self, symbols: List[str]) -> Dict[str, Dict]:
        """Get quotes for multiple symbols.

        Args:
            symbols: List of stock codes

        Returns:
            Dictionary of symbol -> quote
        """
        results = {}

        for symbol in symbols:
            quote = self.get_quote_sina(symbol)
            if quote:
                results[symbol] = quote

        return results

    def _parse_number(self, value: str) -> Optional[Decimal]:
        """Parse number from string."""
        if not value or value == '-':
            return None
        try:
            return Decimal(value)
        except:
            return None
