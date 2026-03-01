# Stock Repository Tests

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
def stock_repo(mock_mysql):
    """Create StockRepository with mock database."""
    with patch('src.repositories.stock_repo.get_mysql', return_value=mock_mysql):
        from src.repositories.stock_repo import StockRepository
        return StockRepository()


# ==================== Stock Basic Tests ====================

class TestInsertStockBasic:
    """Test insert stock basic information"""

    def test_insert_stock_normal(self, stock_repo, mock_mysql):
        """Normal case: Insert stock basic info successfully"""
        result = stock_repo.insert_stock_basic(
            symbol="600519",
            name="贵州茅台",
            market="A股",
            industry="白酒",
            listing_date=date(2001, 8, 27)
        )
        assert result == 1
        assert mock_mysql.execute.called

    def test_insert_stock_with_minimal_params(self, stock_repo, mock_mysql):
        """Normal case: Insert stock with minimal parameters"""
        result = stock_repo.insert_stock_basic(
            symbol="000001",
            name="平安银行",
            market="A股"
        )
        assert result == 1

    def test_insert_stock_empty_symbol(self, stock_repo, mock_mysql):
        """Boundary case: Stock symbol is empty"""
        with pytest.raises(Exception):
            stock_repo.insert_stock_basic(
                symbol="",
                name="贵州茅台",
                market="A股"
            )

    def test_insert_stock_empty_name(self, stock_repo, mock_mysql):
        """Boundary case: Stock name is empty"""
        with pytest.raises(Exception):
            stock_repo.insert_stock_basic(
                symbol="600519",
                name="",
                market="A股"
            )


class TestGetStockBasic:
    """Test get stock basic information"""

    def test_get_stock_normal(self, stock_repo, mock_mysql):
        """Normal case: Get existing stock"""
        mock_mysql.query_one.return_value = {
            'symbol': '600519',
            'name': '贵州茅台',
            'market': 'A股',
            'full_name': None,
            'industry': '白酒',
            'listing_date': date(2001, 8, 27),
            'delisting_date': None,
            'status': '正常',
            'created_at': None,
            'updated_at': None
        }

        stock = stock_repo.get_stock_basic("600519")
        assert stock is not None
        assert stock.symbol == "600519"
        assert stock.name == "贵州茅台"

    def test_get_stock_not_found(self, stock_repo, mock_mysql):
        """Error case: Stock not found"""
        mock_mysql.query_one.return_value = None

        stock = stock_repo.get_stock_basic("999999")
        assert stock is None


class TestGetAllStocks:
    """Test get all stocks"""

    def test_get_all_stocks_normal(self, stock_repo, mock_mysql):
        """Normal case: Get all stocks"""
        mock_mysql.query_all.return_value = [
            {'symbol': '600519', 'name': '贵州茅台', 'market': 'A股', 'full_name': None,
             'industry': '白酒', 'listing_date': None, 'delisting_date': None,
             'status': '正常', 'created_at': None, 'updated_at': None},
            {'symbol': '000001', 'name': '平安银行', 'market': 'A股', 'full_name': None,
             'industry': '银行', 'listing_date': None, 'delisting_date': None,
             'status': '正常', 'created_at': None, 'updated_at': None}
        ]

        stocks = stock_repo.get_all_stocks()
        assert len(stocks) == 2

    def test_get_all_stocks_with_market_filter(self, stock_repo, mock_mysql):
        """Normal case: Filter stocks by market"""
        mock_mysql.query_all.return_value = []

        stocks = stock_repo.get_all_stocks(market="港股")
        assert isinstance(stocks, list)


# ==================== Realtime Quote Tests ====================

class TestInsertStockRealtime:
    """Test insert stock realtime quote"""

    def test_insert_realtime_normal(self, stock_repo, mock_mysql):
        """Normal case: Insert realtime quote successfully"""
        result = stock_repo.insert_stock_realtime(
            symbol="600519",
            price=Decimal("1686.00"),
            change=Decimal("10.00"),
            change_pct=Decimal("0.59"),
            open_price=Decimal("1676.00"),
            high=Decimal("1688.00"),
            low=Decimal("1675.00"),
            close_yest=Decimal("1676.00"),
            volume=1234567,
            amount=Decimal("2089000000"),
            turnover=Decimal("0.23"),
            pe=Decimal("58.52"),
            pb=Decimal("12.35"),
            datetime=datetime(2021, 6, 25, 15, 0, 0)
        )
        assert result == 1

    def test_insert_realtime_invalid_price(self, stock_repo, mock_mysql):
        """Error case: Invalid price (negative)"""
        with pytest.raises(Exception):
            stock_repo.insert_stock_realtime(
                symbol="600519",
                price=Decimal("-100.00"),
                change=Decimal("0"),
                change_pct=Decimal("0"),
                open_price=Decimal("0"),
                high=Decimal("0"),
                low=Decimal("0"),
                close_yest=Decimal("0"),
                volume=0,
                amount=Decimal("0"),
                turnover=Decimal("0"),
                pe=Decimal("0"),
                pb=Decimal("0"),
                datetime=datetime(2021, 6, 25, 15, 0, 0)
            )


class TestGetStockRealtime:
    """Test get stock realtime quote"""

    def test_get_realtime_normal(self, stock_repo, mock_mysql):
        """Normal case: Get realtime quote"""
        mock_mysql.query_one.return_value = {
            'symbol': '600519',
            'price': Decimal("1686.00"),
            'change': Decimal("10.00"),
            'change_pct': Decimal("0.59"),
            'open': Decimal("1676.00"),
            'high': Decimal("1688.00"),
            'low': Decimal("1675.00"),
            'close_yest': Decimal("1676.00"),
            'volume': 1234567,
            'amount': Decimal("2089000000"),
            'turnover': Decimal("0.23"),
            'pe': Decimal("58.52"),
            'pb': Decimal("12.35"),
            'datetime': datetime(2021, 6, 25, 15, 0, 0),
            'created_at': None
        }

        realtime = stock_repo.get_stock_realtime("600519")
        assert realtime is not None
        assert realtime.symbol == "600519"
        assert realtime.price == Decimal("1686.00")

    def test_get_realtime_not_found(self, stock_repo, mock_mysql):
        """Error case: Quote not found"""
        mock_mysql.query_one.return_value = None

        realtime = stock_repo.get_stock_realtime("999999")
        assert realtime is None


# ==================== History Data Tests ====================

class TestInsertStockHistory:
    """Test insert stock history data"""

    def test_insert_history_normal(self, stock_repo, mock_mysql):
        """Normal case: Insert history data successfully"""
        result = stock_repo.insert_stock_history(
            symbol="600519",
            trade_date=date(2021, 6, 25),
            open_price=Decimal("1676.00"),
            high=Decimal("1688.00"),
            low=Decimal("1675.00"),
            close=Decimal("1686.00"),
            volume=1234567,
            amount=Decimal("2089000000"),
            adj_close=Decimal("1686.00"),
            change_pct=Decimal("0.59")
        )
        assert result == 1

    def test_insert_history_future_date(self, stock_repo, mock_mysql):
        """Boundary case: Insert future date"""
        with pytest.raises(Exception):
            stock_repo.insert_stock_history(
                symbol="600519",
                trade_date=date(2030, 12, 31),
                open_price=Decimal("1676.00"),
                high=Decimal("1688.00"),
                low=Decimal("1675.00"),
                close=Decimal("1686.00"),
                volume=1234567,
                amount=Decimal("2089000000")
            )


class TestGetStockHistory:
    """Test get stock history data"""

    def test_get_history_normal(self, stock_repo, mock_mysql):
        """Normal case: Get history data"""
        mock_mysql.query_all.return_value = [
            {
                'symbol': '600519',
                'trade_date': date(2021, 6, 25),
                'open': Decimal("1676.00"),
                'high': Decimal("1688.00"),
                'low': Decimal("1675.00"),
                'close': Decimal("1686.00"),
                'volume': 1234567,
                'amount': Decimal("2089000000"),
                'adj_close': Decimal("1686.00"),
                'change_pct': Decimal("0.59"),
                'created_at': None
            }
        ]

        history = stock_repo.get_stock_history("600519")
        assert len(history) == 1
        assert history[0].symbol == "600519"

    def test_get_history_with_date_range(self, stock_repo, mock_mysql):
        """Normal case: Get history with date range"""
        mock_mysql.query_all.return_value = []

        history = stock_repo.get_stock_history(
            "600519",
            start_date=date(2021, 1, 1),
            end_date=date(2021, 12, 31)
        )
        assert isinstance(history, list)

    def test_get_history_empty_result(self, stock_repo, mock_mysql):
        """Boundary case: No history data"""
        mock_mysql.query_all.return_value = []

        history = stock_repo.get_stock_history("999999")
        assert len(history) == 0

    def test_get_history_invalid_date_range(self, stock_repo, mock_mysql):
        """Error case: Invalid date range"""
        with pytest.raises(Exception):
            stock_repo.get_stock_history(
                "600519",
                start_date=date(2021, 12, 31),
                end_date=date(2021, 1, 1)
            )
