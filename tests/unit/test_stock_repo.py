# Stock Repository Tests

import pytest
from src.repositories.stock_repo import (
    insert_stock_basic,
    get_stock_basic,
    get_all_stocks,
    insert_stock_realtime,
    get_stock_realtime,
    insert_stock_history,
    get_stock_history
)
from src.models.exceptions import StockNotFoundError, DatabaseError


# ==================== 股票基本信息测试 ====================

class TestInsertStockBasic:
    """测试插入股票基本信息"""

    def test_insert_stock_normal(self):
        """正常场景：插入股票基本信息成功"""
        result = insert_stock_basic(
            symbol="600519",
            name="贵州茅台",
            full_name="贵州茅台股份有限公司",
            market="A股",
            industry="白酒",
            listing_date="2001-08-27"
        )
        assert result is not None

    def test_insert_stock_duplicate(self):
        """异常场景：插入重复股票代码"""
        with pytest.raises(DatabaseError, match="股票代码已存在"):
            insert_stock_basic(
                symbol="600519",
                name="贵州茅台",
                market="A股"
            )

    def test_insert_stock_empty_symbol(self):
        """边界场景：股票代码为空"""
        with pytest.raises(ValueError, match="股票代码不能为空"):
            insert_stock_basic(
                symbol="",
                name="贵州茅台",
                market="A股"
            )

    def test_insert_stock_empty_name(self):
        """边界场景：股票名称为空"""
        with pytest.raises(ValueError, match="股票名称不能为空"):
            insert_stock_basic(
                symbol="600519",
                name="",
                market="A股"
            )

    def test_insert_stock_invalid_market(self):
        """异常场景：无效的市场类型"""
        with pytest.raises(ValueError, match="无效的市场类型"):
            insert_stock_basic(
                symbol="600519",
                name="贵州茅台",
                market="未知市场"
            )


class TestGetStockBasic:
    """测试查询股票基本信息"""

    def test_get_stock_normal(self):
        """正常场景：查询存在的股票"""
        stock = get_stock_basic("600519")
        assert stock is not None
        assert stock["symbol"] == "600519"
        assert stock["name"] == "贵州茅台"

    def test_get_stock_not_found(self):
        """异常场景：查询不存在的股票"""
        with pytest.raises(StockNotFoundError, match="股票不存在"):
            get_stock_basic("999999")

    def test_get_stock_empty_symbol(self):
        """边界场景：股票代码为空"""
        with pytest.raises(ValueError, match="股票代码不能为空"):
            get_stock_basic("")

    def test_get_all_stocks_normal(self):
        """正常场景：查询所有股票"""
        stocks = get_all_stocks()
        assert isinstance(stocks, list)
        assert len(stocks) > 0


# ==================== 实时行情测试 ====================

class TestInsertStockRealtime:
    """测试插入实时行情数据"""

    def test_insert_realtime_normal(self):
        """正常场景：插入实时行情成功"""
        result = insert_stock_realtime(
            symbol="600519",
            price=1686.00,
            change=10.00,
            change_pct=0.59,
            open_price=1676.00,
            high=1688.00,
            low=1675.00,
            close_yest=1676.00,
            volume=1234567,
            amount=2089000000,
            turnover=0.23,
            pe=58.52,
            pb=12.35,
            datetime="2021-06-25 15:00:00"
        )
        assert result is not None

    def test_insert_realtime_invalid_price(self):
        """异常场景：无效的价格（负数）"""
        with pytest.raises(ValueError, match="价格必须大于0"):
            insert_stock_realtime(
                symbol="600519",
                price=-100.00,
                change=0,
                change_pct=0,
                open_price=0,
                high=0,
                low=0,
                close_yest=0,
                volume=0,
                amount=0,
                turnover=0,
                pe=0,
                pb=0,
                datetime="2021-06-25 15:00:00"
            )

    def test_insert_realtime_invalid_change_pct(self):
        """边界场景：涨跌幅超过限制"""
        with pytest.raises(ValueError, match="涨跌幅超出范围"):
            insert_stock_realtime(
                symbol="600519",
                price=1686.00,
                change=100.00,
                change_pct=100.00,
                open_price=1676.00,
                high=1688.00,
                low=1675.00,
                close_yest=1676.00,
                volume=1234567,
                amount=2089000000,
                turnover=0.23,
                pe=58.52,
                pb=12.35,
                datetime="2021-06-25 15:00:00"
            )


class TestGetStockRealtime:
    """测试查询实时行情"""

    def test_get_realtime_normal(self):
        """正常场景：查询实时行情"""
        realtime = get_stock_realtime("600519")
        assert realtime is not None
        assert "price" in realtime
        assert "volume" in realtime

    def test_get_realtime_not_found(self):
        """异常场景：查询不存在的股票行情"""
        with pytest.raises(StockNotFoundError, match="行情数据不存在"):
            get_stock_realtime("999999")


# ==================== 历史行情测试 ====================

class TestInsertStockHistory:
    """测试插入历史行情数据"""

    def test_insert_history_normal(self):
        """正常场景：插入历史行情成功"""
        result = insert_stock_history(
            symbol="600519",
            trade_date="2021-06-25",
            open_price=1676.00,
            high=1688.00,
            low=1675.00,
            close=1686.00,
            volume=1234567,
            amount=2089000000,
            adj_close=1686.00,
            change_pct=0.59
        )
        assert result is not None

    def test_insert_history_duplicate(self):
        """异常场景：重复插入同一天行情"""
        with pytest.raises(DatabaseError, match="历史数据已存在"):
            insert_stock_history(
                symbol="600519",
                trade_date="2021-06-25",
                open_price=1676.00,
                high=1688.00,
                low=1675.00,
                close=1686.00,
                volume=1234567,
                amount=2089000000
            )

    def test_insert_history_future_date(self):
        """边界场景：插入未来日期"""
        with pytest.raises(ValueError, match="交易日期不能是未来日期"):
            insert_stock_history(
                symbol="600519",
                trade_date="2030-12-31",
                open_price=1676.00,
                high=1688.00,
                low=1675.00,
                close=1686.00,
                volume=1234567,
                amount=2089000000
            )


class TestGetStockHistory:
    """测试查询历史行情"""

    def test_get_history_normal(self):
        """正常场景：查询历史行情"""
        history = get_stock_history("600519", "2021-01-01", "2021-12-31")
        assert isinstance(history, list)

    def test_get_history_empty_result(self):
        """边界场景：无历史数据"""
        history = get_stock_history("999999", "2021-01-01", "2021-12-31")
        assert len(history) == 0

    def test_get_history_invalid_date_range(self):
        """异常场景：日期范围无效"""
        with pytest.raises(ValueError, match="开始日期不能晚于结束日期"):
            get_stock_history("600519", "2021-12-31", "2021-01-01")
