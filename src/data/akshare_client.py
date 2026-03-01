"""AKShare 数据接入模块

基于 akshare 库的数据获取接口
"""

import akshare as ak
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime, timedelta

from src.utils.logger import get_logger

logger = get_logger(__name__)


class AKShareClient:
    """AKShare 客户端

    提供股票、指数、基金等数据接口
    """

    @staticmethod
    def get_realtime_quotes(symbols: List[str] = None) -> pd.DataFrame:
        """获取实时行情

        Args:
            symbols: 股票代码列表，为空则获取全部

        Returns:
            行情数据 DataFrame
        """
        try:
            df = ak.stock_zh_a_spot_em()
            if symbols:
                # 过滤指定股票
                df = df[df['代码'].isin(symbols)]
            return df
        except Exception as e:
            logger.error(f"获取实时行情失败: {e}")
            return pd.DataFrame()

    @staticmethod
    def get_stock_daily(symbol: str, start_date: str = None,
                        end_date: str = None, adjust: str = "qfq") -> pd.DataFrame:
        """获取个股历史K线

        Args:
            symbol: 股票代码 (如 002738 或 sh002738)
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            adjust: 复权类型 (qfq/bfq/空)

        Returns:
            K线数据 DataFrame
        """
        try:
            # 转换代码格式
            if not symbol.startswith('sh') and not symbol.startswith('sz'):
                symbol = f"sh{symbol}"

            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')

            df = ak.stock_zh_a_daily(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                adjust=adjust
            )
            return df
        except Exception as e:
            logger.error(f"获取K线数据失败: {e}")
            return pd.DataFrame()

    @staticmethod
    def get_stock_info(symbol: str) -> Dict:
        """获取个股基本信息

        Args:
            symbol: 股票代码

        Returns:
            基本信息字典
        """
        try:
            df = ak.stock_individual_info_em(symbol=symbol)
            # 转换为字典
            info = dict(zip(df['item'], df['value']))
            return info
        except Exception as e:
            logger.error(f"获取个股信息失败: {e}")
            return {}

    @staticmethod
    def get_fund_flow(symbol: str) -> pd.DataFrame:
        """获取资金流向

        Args:
            symbol: 股票代码

        Returns:
            资金流向 DataFrame
        """
        try:
            df = ak.stock_individual_fund_flow(symbol=symbol)
            return df
        except Exception as e:
            logger.error(f"获取资金流向失败: {e}")
            return pd.DataFrame()

    @staticmethod
    def get_index_quotes() -> pd.DataFrame:
        """获取主要指数行情

        Returns:
            指数行情 DataFrame
        """
        try:
            df = ak.stock_zh_index_spot()
            return df
        except Exception as e:
            logger.error(f"获取指数行情失败: {e}")
            return pd.DataFrame()

    @staticmethod
    def get_margin_detail(symbol: str) -> pd.DataFrame:
        """获取融资融券明细

        Args:
            symbol: 股票代码

        Returns:
            融资融券 DataFrame
        """
        try:
            df = ak.stock_margin_detail(symbol=symbol)
            return df
        except Exception as e:
            logger.error(f"获取融资融券失败: {e}")
            return pd.DataFrame()


# 便捷函数
def get_stock_realtime(symbol: str) -> Dict:
    """快速获取股票实时数据

    Args:
        symbol: 股票代码

    Returns:
        实时数据字典
    """
    client = AKShareClient()
    quotes = client.get_realtime_quotes([symbol])
    if not quotes.empty:
        return quotes.iloc[0].to_dict()
    return {}


def get_stock_history(symbol: str, days: int = 30) -> pd.DataFrame:
    """快速获取股票历史数据

    Args:
        symbol: 股票代码
        days: 天数

    Returns:
        历史数据 DataFrame
    """
    client = AKShareClient()
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
    return client.get_stock_daily(symbol, start_date, end_date)
