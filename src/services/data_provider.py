"""数据提供模块 (Data Provider)

基于 akshare 和 Tushare 封装数据接口，为 Multi-Agent 系统提供数据支持：
- Tushare: 实时行情、历史K线、财务数据 (推荐)
- akshare: 新闻、研报、资金流 (补充)
"""

import akshare as ak
import tushare as ts
import pandas as pd
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import time
import hashlib
import json

from src.utils.logger import get_logger
from src.db.mysql_db import get_mysql

logger = get_logger(__name__)

# Tushare 初始化
TUSHARE_TOKEN = '202f4794ff36d1b56a3ddc17038c4f962a8c43dc59954c1c7858afea'
try:
    ts.set_token(TUSHARE_TOKEN)
    _tushare_pro = ts.pro_api()
    logger.info("Tushare initialized successfully")
except Exception as e:
    logger.warning(f"Tushare initialization failed: {e}")
    _tushare_pro = None


class DataCache:
    """简单的内存缓存"""

    def __init__(self, ttl: int = 60):
        """初始化缓存

        Args:
            ttl: 缓存有效期(秒)，默认60秒
        """
        self._cache: Dict[str, tuple] = {}
        self.ttl = ttl

    def get(self, key: str) -> Optional[pd.DataFrame]:
        """获取缓存数据

        Args:
            key: 缓存键

        Returns:
            缓存的数据或 None
        """
        if key in self._cache:
            data, expire_time = self._cache[key]
            if time.time() < expire_time:
                return data
            else:
                del self._cache[key]
        return None

    def set(self, key: str, data: pd.DataFrame, ttl: int = None):
        """设置缓存数据

        Args:
            key: 缓存键
            data: 数据
            ttl: 缓存有效期(秒)，None 则使用默认值
        """
        if ttl is None:
            ttl = self.ttl
        expire_time = time.time() + ttl
        self._cache[key] = (data, expire_time)

    def clear(self):
        """清空缓存"""
        self._cache.clear()


# 全局缓存实例
_cache = DataCache(ttl=60)


def _convert_columns_to_english(df: pd.DataFrame) -> pd.DataFrame:
    """将中文列名转换为英文

    Args:
        df: 原始 DataFrame

    Returns:
        列名转换后的 DataFrame
    """
    if df is None or df.empty:
        return df

    # 常见的中文列名映射
    column_mapping = {
        '日期': 'date',
        '股票代码': 'symbol',
        '股票名称': 'name',
        '开盘': 'open',
        '收盘': 'close',
        '最高': 'high',
        '最低': 'low',
        '成交量': 'volume',
        '成交额': 'amount',
        '振幅': 'amplitude',
        '涨跌幅': 'change_pct',
        '涨跌额': 'change',
        '换手率': 'turnover',
        '市盈率': 'pe',
        '市净率': 'pb',
        '总市值': 'total_market_cap',
        '流通市值': 'float_market_cap',
        '买入': 'buy',
        '卖出': 'sell',
        '净额': 'net_amount',
        '净流入': 'net_inflow',
        '主力净流入': 'main_net_inflow',
        '散户净流入': 'retail_net_inflow',
    }

    # 重命名列
    new_columns = {}
    for col in df.columns:
        if col in column_mapping:
            new_columns[col] = column_mapping[col]
        else:
            # 尝试转换未映射的列
            new_columns[col] = col

    return df.rename(columns=new_columns)


# ============================================================
# 1. Market Data (行情数据)
# ============================================================

class MarketDataProvider:
    """行情数据提供者"""

    @staticmethod
    def get_stock_daily(symbol: str, period: str = "daily",
                       start_date: str = None, end_date: str = None,
                       adjust: str = "qfq") -> pd.DataFrame:
        """获取A股日线数据

        Args:
            symbol: 股票代码 (如 002738)
            period: 周期 (daily/weekly/monthly)
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            adjust: 复权类型 (qfq/bfq/空)

        Returns:
            日线数据 DataFrame
        """
        try:
            # 转换代码格式
            if not symbol.startswith('sh') and not symbol.startswith('sz'):
                symbol = f"sh{symbol}"

            # 默认获取一年数据
            if not start_date:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')

            # 检查缓存
            cache_key = f"stock_daily_{symbol}_{period}_{start_date}_{end_date}_{adjust}"
            cached = _cache.get(cache_key)
            if cached is not None:
                logger.info(f"返回缓存数据: {symbol}")
                return cached

            df = ak.stock_zh_a_hist(
                symbol=symbol,
                period=period,
                start_date=start_date,
                end_date=end_date,
                adjust=adjust
            )

            df = _convert_columns_to_english(df)
            _cache.set(cache_key, df)
            logger.info(f"获取日线数据成功: {symbol}, {len(df)} 条")
            return df

        except Exception as e:
            logger.error(f"获取日线数据失败: {symbol}, {e}")
            return pd.DataFrame()

    @staticmethod
    def get_realtime_quotes(symbols: List[str] = None) -> pd.DataFrame:
        """获取A股实时快照

        Args:
            symbols: 股票代码列表，为空则获取全部

        Returns:
            实时行情 DataFrame
        """
        try:
            cache_key = "realtime_quotes_all"
            if symbols:
                cache_key = f"realtime_quotes_{'_'.join(symbols)}"

            # 缓存时间缩短为10秒
            cached = _cache.get(cache_key)
            if cached is not None:
                return cached

            df = ak.stock_zh_a_spot_em()

            if symbols:
                df = df[df['代码'].isin(symbols)]

            df = _convert_columns_to_english(df)
            _cache.set(cache_key, df)
            return df

        except Exception as e:
            logger.error(f"获取实时行情失败: {e}")
            return pd.DataFrame()

    @staticmethod
    def get_industry_constituents(symbol: str) -> pd.DataFrame:
        """获取行业成分股

        Args:
            symbol: 行业板块代码

        Returns:
            成分股 DataFrame
        """
        try:
            cache_key = f"industry_cons_{symbol}"
            cached = _cache.get(cache_key)
            if cached is not None:
                return cached

            df = ak.stock_board_industry_cons_em(symbol=symbol)
            df = _convert_columns_to_english(df)
            _cache.set(cache_key, df)
            return df

        except Exception as e:
            logger.error(f"获取行业成分股失败: {symbol}, {e}")
            return pd.DataFrame()

    @staticmethod
    def get_industry_history(symbol: str, start_date: str = None,
                           end_date: str = None) -> pd.DataFrame:
        """获取行业指数历史

        Args:
            symbol: 行业板块代码
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            行业指数历史 DataFrame
        """
        try:
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')

            cache_key = f"industry_hist_{symbol}_{start_date}_{end_date}"
            cached = _cache.get(cache_key)
            if cached is not None:
                return cached

            df = ak.stock_board_industry_hist_em(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date
            )
            df = _convert_columns_to_english(df)
            _cache.set(cache_key, df)
            return df

        except Exception as e:
            logger.error(f"获取行业指数历史失败: {symbol}, {e}")
            return pd.DataFrame()

    @staticmethod
    def get_hot_stocks(limit: int = 10) -> pd.DataFrame:
        """获取热门股票排行

        Args:
            limit: 返回数量

        Returns:
            热门股票 DataFrame
        """
        try:
            cache_key = f"hot_stocks_{limit}"
            cached = _cache.get(cache_key)
            if cached is not None:
                return cached

            df = ak.stock_hot_rank_latest_em()
            if not df.empty and limit:
                df = df.head(limit)

            df = _convert_columns_to_english(df)
            _cache.set(cache_key, df, ttl=300)  # 缓存5分钟
            return df

        except Exception as e:
            logger.error(f"获取热门股票失败: {e}")
            return pd.DataFrame()

    @staticmethod
    def get_stock_announcements(symbol: str, limit: int = 20) -> pd.DataFrame:
        """获取上市公司公告

        Args:
            symbol: 股票代码 (如 002738)
            limit: 返回数量

        Returns:
            公告 DataFrame
        """
        try:
            cache_key = f"announcements_{symbol}_{limit}"
            cached = _cache.get(cache_key)
            if cached is not None:
                return cached

            df = ak.stock_zh_a_disclosure_report_cninfo(symbol=symbol)
            if not df.empty and limit:
                df = df.head(limit)

            df = _convert_columns_to_english(df)
            _cache.set(cache_key, df, ttl=1800)  # 缓存30分钟
            return df

        except Exception as e:
            logger.error(f"获取公告失败: {symbol}, {e}")
            return pd.DataFrame()


# ============================================================
# 2. Fundamental & News (基本面与新闻)
# ============================================================

class FundamentalProvider:
    """基本面数据提供者"""

    @staticmethod
    def get_financial_indicator(symbol: str) -> pd.DataFrame:
        """获取财务指标 (使用财务摘要接口)

        Args:
            symbol: 股票代码 (如 002738)

        Returns:
            财务指标 DataFrame
        """
        try:
            cache_key = f"financial_indicator_{symbol}"
            cached = _cache.get(cache_key)
            if cached is not None:
                return cached

            # 使用财务摘要接口 (更稳定)
            df = ak.stock_financial_abstract(symbol=symbol)
            df = _convert_columns_to_english(df)
            _cache.set(cache_key, df, ttl=3600)  # 财务数据缓存1小时
            return df

        except Exception as e:
            logger.error(f"获取财务指标失败: {symbol}, {e}")
            return pd.DataFrame()

    @staticmethod
    def get_stock_news(symbol: str) -> pd.DataFrame:
        """获取个股新闻 (用于 LLM 情感分析)

        Args:
            symbol: 股票代码

        Returns:
            新闻 DataFrame
        """
        try:
            cache_key = f"stock_news_{symbol}"
            cached = _cache.get(cache_key)
            if cached is not None:
                return cached

            df = ak.stock_news_em(symbol=symbol)
            df = _convert_columns_to_english(df)
            _cache.set(cache_key, df, ttl=300)  # 新闻缓存5分钟
            return df

        except Exception as e:
            logger.error(f"获取个股新闻失败: {symbol}, {e}")
            return pd.DataFrame()

    @staticmethod
    def get_global_news() -> pd.DataFrame:
        """获取财联社电报 (用于宏观分析)

        Returns:
            电报 DataFrame
        """
        try:
            cache_key = "global_news"
            cached = _cache.get(cache_key)
            if cached is not None:
                return cached

            df = ak.stock_info_global_cls()
            df = _convert_columns_to_english(df)
            _cache.set(cache_key, df, ttl=300)
            return df

        except Exception as e:
            logger.error(f"获取财联社电报失败: {e}")
            return pd.DataFrame()

    @staticmethod
    def get_research_reports(symbol: str) -> pd.DataFrame:
        """获取个股研报

        Args:
            symbol: 股票代码

        Returns:
            研报 DataFrame
        """
        try:
            cache_key = f"research_report_{symbol}"
            cached = _cache.get(cache_key)
            if cached is not None:
                return cached

            df = ak.stock_research_report_em(symbol=symbol)
            df = _convert_columns_to_english(df)
            _cache.set(cache_key, df, ttl=3600)  # 研报缓存1小时
            return df

        except Exception as e:
            logger.error(f"获取个股研报失败: {symbol}, {e}")
            return pd.DataFrame()


# ============================================================
# 3. Quant Factors (量化因子数据)
# ============================================================

class QuantFactorProvider:
    """量化因子数据提供者"""

    @staticmethod
    def get_fund_flow(symbol: str) -> pd.DataFrame:
        """获取个股资金流

        Args:
            symbol: 股票代码 (如 002738)

        Returns:
            资金流 DataFrame
        """
        try:
            cache_key = f"fund_flow_{symbol}"
            cached = _cache.get(cache_key)
            if cached is not None:
                return cached

            # 判断市场
            if symbol.startswith('6'):
                market = 'sh'
            elif symbol.startswith(('0', '3')):
                market = 'sz'
            else:
                market = 'sh'

            df = ak.stock_individual_fund_flow(stock=symbol, market=market)
            df = _convert_columns_to_english(df)
            _cache.set(cache_key, df, ttl=300)  # 资金流缓存5分钟
            return df

        except Exception as e:
            logger.error(f"获取资金流失败: {symbol}, {e}")
            return pd.DataFrame()

    @staticmethod
    def get_hsgt_flow(symbol: str = "all") -> pd.DataFrame:
        """获取北向资金流向

        Args:
            symbol: 股票代码或 "all"

        Returns:
            北向资金 DataFrame
        """
        try:
            cache_key = f"hsgt_flow_{symbol}"
            cached = _cache.get(cache_key)
            if cached is not None:
                return cached

            df = ak.stock_hsgt_hist_em(symbol=symbol)
            df = _convert_columns_to_english(df)
            _cache.set(cache_key, df, ttl=300)
            return df

        except Exception as e:
            logger.error(f"获取北向资金失败: {e}")
            return pd.DataFrame()

    @staticmethod
    def get_lhb_details(start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """获取龙虎榜明细

        Args:
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)

        Returns:
            龙虎榜 DataFrame
        """
        try:
            if not start_date:
                start_date = datetime.now().strftime('%Y%m%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y%m%d')

            cache_key = f"lhb_detail_{start_date}_{end_date}"
            cached = _cache.get(cache_key)
            if cached is not None:
                return cached

            df = ak.stock_lhb_detail_em(start_date=start_date, end_date=end_date)
            df = _convert_columns_to_english(df)
            _cache.set(cache_key, df, ttl=600)  # 龙虎榜缓存10分钟
            return df

        except Exception as e:
            logger.error(f"获取龙虎榜失败: {e}")
            return pd.DataFrame()


# ============================================================
# 4. Macro & Risk (宏观风控数据)
# ============================================================

class MacroRiskProvider:
    """宏观风控数据提供者"""

    @staticmethod
    def get_bond_rates() -> pd.DataFrame:
        """获取中美债收益率

        Returns:
            债收益率 DataFrame
        """
        try:
            cache_key = "bond_rates"
            cached = _cache.get(cache_key)
            if cached is not None:
                return cached

            df = ak.bond_zh_us_rate()
            df = _convert_columns_to_english(df)
            _cache.set(cache_key, df, ttl=3600)  # 债券数据缓存1小时
            return df

        except Exception as e:
            logger.error(f"获取债收益率失败: {e}")
            return pd.DataFrame()

    @staticmethod
    def get_vix() -> pd.DataFrame:
        """获取恐慌指数 (VIX proxy)

        Returns:
            恐慌指数 DataFrame
        """
        try:
            cache_key = "vix"
            cached = _cache.get(cache_key)
            if cached is not None:
                return cached

            df = ak.index_option_50etf_qvix()
            df = _convert_columns_to_english(df)
            _cache.set(cache_key, df, ttl=300)
            return df

        except Exception as e:
            logger.error(f"获取恐慌指数失败: {e}")
            return pd.DataFrame()

    @staticmethod
    def get_gold_price() -> pd.DataFrame:
        """获取黄金价格

        Returns:
            黄金价格 DataFrame
        """
        try:
            cache_key = "gold_price"
            cached = _cache.get(cache_key)
            if cached is not None:
                return cached

            df = ak.spot_hist_sge()
            df = _convert_columns_to_english(df)
            _cache.set(cache_key, df, ttl=3600)
            return df

        except Exception as e:
            logger.error(f"获取黄金价格失败: {e}")
            return pd.DataFrame()


# ============================================================
# 便捷函数
# ============================================================

def get_market_data(symbol: str, days: int = 30) -> pd.DataFrame:
    """快速获取市场数据

    Args:
        symbol: 股票代码
        days: 天数

    Returns:
        市场数据
    """
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
    end_date = datetime.now().strftime('%Y%m%d')
    return MarketDataProvider.get_stock_daily(symbol, start_date=start_date, end_date=end_date)


def get_news_for_analysis(symbol: str) -> pd.DataFrame:
    """获取用于 LLM 分析的新闻

    Args:
        symbol: 股票代码

    Returns:
        新闻数据
    """
    return FundamentalProvider.get_stock_news(symbol)


def get_quant_factors(symbol: str) -> Dict:
    """获取量化因子数据

    Args:
        symbol: 股票代码

    Returns:
        因子数据字典
    """
    factors = {}

    # 资金流
    fund_flow = QuantFactorProvider.get_fund_flow(symbol)
    if not fund_flow.empty:
        factors['fund_flow'] = fund_flow

    # 北向资金
    hsgt = QuantFactorProvider.get_hsgt_flow(symbol)
    if not hsgt.empty:
        factors['hsgt'] = hsgt

    return factors


# ============================================================
# 5. Tushare Provider (推荐使用)
# ============================================================

class TushareProvider:
    """Tushare 数据提供者 (推荐)

    Tushare 是专业金融数据接口，稳定性远高于 akshare
    """

    @staticmethod
    def _format_stock_code(symbol: str) -> str:
        """转换股票代码为 Tushare 格式

        Args:
            symbol: 股票代码 (如 002738 / 600519)

        Returns:
            Tushare 格式 (如 002738.SZ / 600519.SH)
        """
        if '.' in symbol:
            return symbol
        if symbol.startswith('6'):
            return f"{symbol}.SH"
        elif symbol.startswith(('0', '3')):
            return f"{symbol}.SZ"
        else:
            return f"{symbol}.SZ"

    @staticmethod
    def get_daily_price(symbol: str, days: int = 30) -> pd.DataFrame:
        """获取个股历史行情 (Tushare 推荐)

        Args:
            symbol: 股票代码 (如 002738 / 002738.SZ)
            days: 查询天数

        Returns:
            行情 DataFrame
        """
        try:
            if _tushare_pro is None:
                logger.error("Tushare not initialized")
                return pd.DataFrame()

            ts_code = TushareProvider._format_stock_code(symbol)
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')

            cache_key = f"tushare_daily_{ts_code}_{days}"
            cached = _cache.get(cache_key)
            if cached is not None:
                return cached

            df = _tushare_pro.daily(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date
            )

            # 转换列名
            df = df.rename(columns={
                'ts_code': 'symbol',
                'trade_date': 'date',
                'pre_close': 'pre_close',
                'change': 'change',
                'pct_chg': 'change_pct',
                'vol': 'volume',
                'amount': 'amount'
            })

            # 按日期排序
            df = df.sort_values('date')
            _cache.set(cache_key, df, ttl=300)
            logger.info(f"获取Tushare行情成功: {ts_code}, {len(df)} 条")
            return df

        except Exception as e:
            logger.error(f"获取Tushare行情失败: {symbol}, {e}")
            return pd.DataFrame()

    @staticmethod
    def get_realtime_quote(symbol: str) -> pd.DataFrame:
        """获取实时行情 (当日行情)

        Args:
            symbol: 股票代码

        Returns:
            实时行情 DataFrame
        """
        try:
            if _tushare_pro is None:
                logger.error("Tushare not initialized")
                return pd.DataFrame()

            ts_code = TushareProvider._format_stock_code(symbol)
            today = datetime.now().strftime('%Y%m%d')

            cache_key = f"tushare_realtime_{ts_code}"
            cached = _cache.get(cache_key)
            if cached is not None:
                return cached

            df = _tushare_pro.daily(
                ts_code=ts_code,
                start_date=today,
                end_date=today
            )

            if df.empty:
                return pd.DataFrame()

            # 添加实时字段
            df['最新价'] = df['close']
            df['涨跌幅'] = df['pct_chg']
            df['涨跌额'] = df['change']
            df['成交量'] = df['vol']
            df['成交额'] = df['amount']
            df['最高'] = df['high']
            df['最低'] = df['low']
            df['今开'] = df['open']
            df['昨收'] = df['pre_close']

            _cache.set(cache_key, df, ttl=60)
            return df

        except Exception as e:
            logger.error(f"获取实时行情失败: {symbol}, {e}")
            return pd.DataFrame()

    @staticmethod
    def get_stock_basic() -> pd.DataFrame:
        """获取股票基本信息

        Returns:
            股票基本信息 DataFrame
        """
        try:
            if _tushare_pro is None:
                return pd.DataFrame()

            cache_key = "tushare_stock_basic"
            cached = _cache.get(cache_key)
            if cached is not None:
                return cached

            df = _tushare_pro.stock_basic(exchange='', list_status='L')
            _cache.set(cache_key, df, ttl=86400)  # 缓存1天
            return df

        except Exception as e:
            logger.error(f"获取股票基本信息失败: {e}")
            return pd.DataFrame()


# 便捷函数
def get_price_tushare(symbol: str, days: int = 30) -> pd.DataFrame:
    """使用 Tushare 获取股票行情

    Args:
        symbol: 股票代码
        days: 天数

    Returns:
        行情数据
    """
    return TushareProvider.get_daily_price(symbol, days)


# ============================================================
# 股票列表和搜索
# ============================================================

class StockListProvider:
    """股票列表提供者 - 使用AKShare获取并缓存"""

    _stock_list_cache = None  # 内存缓存

    @classmethod
    def _load_from_tushare(cls) -> pd.DataFrame:
        """从Tushare加载股票列表到内存缓存"""
        if cls._stock_list_cache is not None and not cls._stock_list_cache.empty:
            return cls._stock_list_cache

        try:
            if _tushare_pro is None:
                logger.warning("Tushare未初始化")
                return pd.DataFrame()

            logger.info("从Tushare获取股票列表...")
            df = _tushare_pro.stock_basic(
                exchange='',
                list_status='L',
                fields='ts_code,symbol,name,area,industry,list_date'
            )
            if df is not None and not df.empty:
                # 判断市场
                df['market'] = df['ts_code'].apply(
                    lambda x: 'SH' if x.endswith('.SH') else ('SZ' if x.endswith('.SZ') else 'A股')
                )
                # 过滤ST股票
                df = df[~df['name'].str.contains(r'ST|退|\*ST', na=False, regex=True)]
                cls._stock_list_cache = df
                logger.info(f"从Tushare获取到 {len(df)} 只股票（过滤ST后）")
                return df
        except Exception as e:
            logger.warning(f"Tushare获取失败: {e}")

        return pd.DataFrame()

    @classmethod
    def _load_from_akshare(cls) -> pd.DataFrame:
        """从AKShare加载股票列表到内存缓存（备用方案）"""
        if cls._stock_list_cache is not None and not cls._stock_list_cache.empty:
            return cls._stock_list_cache

        try:
            logger.info("从AKShare获取股票列表...")
            df = ak.stock_info_a_code_name()
            if df is not None and not df.empty:
                df = df.rename(columns={'code': 'symbol', 'name': 'name'})
                # 判断市场
                df['market'] = df['symbol'].apply(
                    lambda x: 'SH' if str(x).startswith('6') else 'SZ'
                )
                # 过滤ST股票
                df = df[~df['name'].str.contains(r'ST|退|\*ST', na=False, regex=True)]
                cls._stock_list_cache = df
                logger.info(f"从AKShare获取到 {len(df)} 只股票（过滤ST后）")
                return df
        except Exception as e:
            logger.warning(f"AKShare获取失败: {e}")

        return pd.DataFrame()

    @classmethod
    def _load_stock_list(cls) -> pd.DataFrame:
        """加载股票列表 - 优先Tushare，备用AKShare"""
        # 优先尝试Tushare
        df = cls._load_from_tushare()
        if df is not None and not df.empty:
            return df

        # Tushare失败，使用AKShare备用
        logger.info("Tushare获取失败，切换到AKShare...")
        return cls._load_stock_list()

    @classmethod
    def load_stock_list_to_db(cls, force: bool = False) -> int:
        """加载股票列表（AKShare版本）

        Args:
            force: 是否强制重新加载

        Returns:
            加载的股票数量
        """
        df = cls._load_stock_list()
        if df is not None and not df.empty:
            return len(df)
        return 0

    @classmethod
    def search_stocks(cls, keyword: str, limit: int = 20) -> list:
        """模糊搜索股票 - 使用内存缓存

        Args:
            keyword: 搜索关键词（代码或名称）
            limit: 返回数量

        Returns:
            股票列表 [{symbol, name}, ...]
        """
        # 尝试多种编码处理关键词
        search_keywords = [keyword]

        # 如果关键词看起来像GBK编码（包含\x），尝试解码
        try:
            if '\\x' in repr(keyword):
                # 尝试将GBK编码的字符串转换为UTF-8
                gbk_bytes = keyword.encode('latin1')  # 先用latin1获取原始字节
                utf8_keyword = gbk_bytes.decode('gbk')
                if utf8_keyword != keyword:
                    search_keywords.append(utf8_keyword)
        except Exception:
            pass

        # 也尝试URL解码
        try:
            import urllib.parse
            url_decoded = urllib.parse.unquote(keyword)
            if url_decoded != keyword:
                search_keywords.append(url_decoded)
        except Exception:
            pass

        # 1. 确保缓存已加载
        if cls._stock_list_cache is None or cls._stock_list_cache.empty:
            cls._load_stock_list()

        # 2. 从缓存中搜索，尝试多个关键词
        if cls._stock_list_cache is not None and not cls._stock_list_cache.empty:
            for kw in search_keywords:
                keyword_upper = kw.upper()
                mask = cls._stock_list_cache['symbol'].astype(str).str.contains(keyword_upper, na=False) | \
                       cls._stock_list_cache['name'].str.contains(kw, na=False)
                results = cls._stock_list_cache[mask].head(limit)
                if not results.empty:
                    return [{'symbol': row['symbol'], 'name': row['name']}
                            for _, row in results.iterrows()]

        # 3. 返回空列表
        return []

    @classmethod
    def get_stock_count(cls) -> int:
        """获取股票数量"""
        if cls._stock_list_cache is None:
            cls._load_stock_list()
        if cls._stock_list_cache is not None:
            return len(cls._stock_list_cache)
        return 0


# ============================================================
# 6. 统一行情客户端 (Tushare + AKShare 互补)
# ============================================================

class StockQuoteClient:
    """统一的股票行情查询客户端

    特性:
    - Tushare 为主 AKShare 为兜底
    - 自动故障切换
    - 统一输出格式
    """

    # 统一字段映射
    FIELD_MAPPING = {
        '代码': 'symbol',
        '名称': 'name',
        '最新价': 'close',
        '涨跌幅': 'change_pct',
        '涨跌额': 'change',
        '成交量': 'volume',
        '成交额': 'amount',
        '最高': 'high',
        '最低': 'low',
        '今开': 'open',
        '昨收': 'pre_close'
    }

    @staticmethod
    def _format_code(symbol: str) -> str:
        """转换股票代码为 Tushare 格式

        Args:
            symbol: 股票代码

        Returns:
            Tushare 格式 (如 002738.SZ / 600519.SH)
        """
        if '.' in symbol:
            return symbol
        if symbol.startswith('6'):
            return f"{symbol}.SH"
        elif symbol.startswith(('0', '3')):
            return f"{symbol}.SZ"
        return f"{symbol}.SZ"

    @staticmethod
    def get_quote(symbols: list, prefer: str = 'tushare') -> pd.DataFrame:
        """统一查询入口

        Args:
            symbols: 股票代码列表 (如 ['002738', '600519'] 或 ['002738.SZ', '600519.SH'])
            prefer: 优先数据源 ('tushare' 或 'akshare')

        Returns:
            统一格式的行情数据 DataFrame
        """
        # 优先查询
        if prefer == 'tushare':
            result = StockQuoteClient._get_tushare_quote(symbols)
            if not result.empty:
                return result
            # 兜底 AKShare
            logger.warning("Tushare 查询失败，切换到 AKShare 兜底")
            return StockQuoteClient._get_akshare_quote(symbols)
        else:
            result = StockQuoteClient._get_akshare_quote(symbols)
            if not result.empty:
                return result
            # 兜底 Tushare
            logger.warning("AKShare 查询失败，切换到 Tushare 兜底")
            return StockQuoteClient._get_tushare_quote(symbols)

    @staticmethod
    def _get_tushare_quote(symbols: list) -> pd.DataFrame:
        """Tushare 查询指定股票行情 (最新行情)

        Args:
            symbols: 股票代码列表

        Returns:
            行情 DataFrame
        """
        try:
            if _tushare_pro is None:
                return pd.DataFrame()

            from datetime import datetime, timedelta

            # 获取最近5个交易日的日期
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=10)).strftime('%Y%m%d')

            df_list = []
            for symbol in symbols:
                ts_code = StockQuoteClient._format_code(symbol)
                daily_df = _tushare_pro.daily(
                    ts_code=ts_code,
                    start_date=start_date,
                    end_date=end_date
                )
                if not daily_df.empty:
                    # 取最新一条
                    latest = daily_df.sort_values('trade_date', ascending=False).head(1)
                    latest['symbol'] = ts_code
                    df_list.append(latest)

            if not df_list:
                return pd.DataFrame()

            full_df = pd.concat(df_list, ignore_index=True)

            # 统一字段名
            full_df = full_df.rename(columns={
                'ts_code': 'symbol',
                'trade_date': 'date',
                'pct_chg': 'change_pct',
                'vol': 'volume'
            })

            return full_df

        except Exception as e:
            logger.error(f"Tushare 查询失败: {e}")
            return pd.DataFrame()

    @staticmethod
    def _get_akshare_quote(symbols: list) -> pd.DataFrame:
        """AKShare 查询指定股票行情 (兜底)

        Args:
            symbols: 股票代码列表

        Returns:
            行情 DataFrame
        """
        try:
            time.sleep(1)  # 避免请求过快
            full_df = ak.stock_zh_a_spot_em()

            # 提取纯代码 (去掉 .SH/.SZ)
            simple_codes = [s.replace('.SH', '').replace('.SZ', '') for s in symbols]
            target_df = full_df[full_df['代码'].isin(simple_codes)]

            if target_df.empty:
                return pd.DataFrame()

            # 统一字段名
            target_df = target_df.rename(columns={
                '代码': 'symbol',
                '名称': 'name',
                '最新价': 'close',
                '涨跌幅': 'change_pct',
                '涨跌额': 'change',
                '成交量': 'volume',
                '成交额': 'amount',
                '最高': 'high',
                '最低': 'low',
                '今开': 'open',
                '昨收': 'pre_close'
            })

            return target_df

        except Exception as e:
            logger.error(f"AKShare 查询失败: {e}")
            return pd.DataFrame()


# 便捷函数
def get_stock_quote(symbols: list, prefer: str = 'tushare') -> pd.DataFrame:
    """获取股票行情 (统一接口)

    Args:
        symbols: 股票代码列表
        prefer: 优先数据源

    Returns:
        行情数据
    """
    return StockQuoteClient.get_quote(symbols, prefer)


# ============================================================
# 财务数据接口
# ============================================================

class FinancialDataProvider:
    """财务数据提供者"""

    @staticmethod
    def get_financial_summary(symbol: str, limit: int = 5) -> pd.DataFrame:
        """获取财务指标摘要

        Args:
            symbol: 股票代码
            limit: 返回记录数

        Returns:
            财务指标数据
        """
        cache_key = f"financial_summary_{symbol}"
        cached = _cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            # 使用AKShare获取财务指标
            df = ak.stock_financial_abstract_ths(symbol=symbol)
            if df is not None and not df.empty:
                df = df.head(limit)
                _cache.set(cache_key, df, ttl=3600)  # 缓存1小时
                return df
        except Exception as e:
            logger.warning(f"获取财务摘要失败: {e}")

        return pd.DataFrame()

    @staticmethod
    def get_income_statement(symbol: str, limit: int = 5) -> pd.DataFrame:
        """获取利润表数据

        Args:
            symbol: 股票代码
            limit: 返回记录数

        Returns:
            利润表数据
        """
        cache_key = f"income_{symbol}"
        cached = _cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            # 使用AKShare获取利润表
            df = ak.stock_financial_income_indicator(symbol=symbol)
            if df is not None and not df.empty:
                df = df.head(limit)
                _cache.set(cache_key, df, ttl=3600)
                return df
        except Exception as e:
            logger.warning(f"获取利润表失败: {e}")

        return pd.DataFrame()

    @staticmethod
    def get_balance_sheet(symbol: str, limit: int = 5) -> pd.DataFrame:
        """获取资产负债表数据

        Args:
            symbol: 股票代码
            limit: 返回记录数

        Returns:
            资产负债表数据
        """
        cache_key = f"balance_{symbol}"
        cached = _cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            # 使用AKShare获取资产负债表
            df = ak.stock_financial_balance_indicator(symbol=symbol)
            if df is not None and not df.empty:
                df = df.head(limit)
                _cache.set(cache_key, df, ttl=3600)
                return df
        except Exception as e:
            logger.warning(f"获取资产负债表失败: {e}")

        return pd.DataFrame()

    @staticmethod
    def get_cash_flow(symbol: str, limit: int = 5) -> pd.DataFrame:
        """获取现金流量表数据

        Args:
            symbol: 股票代码
            limit: 返回记录数

        Returns:
            现金流量表数据
        """
        cache_key = f"cashflow_{symbol}"
        cached = _cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            df = ak.stock_financial_cash_flow(symbol=symbol)
            if df is not None and not df.empty:
                df = df.head(limit)
                _cache.set(cache_key, df, ttl=3600)
                return df
        except Exception as e:
            logger.warning(f"获取现金流量表失败: {e}")

        return pd.DataFrame()


# ============================================================
# 行业数据接口
# ============================================================

class IndustryDataProvider:
    """行业数据提供者"""

    @staticmethod
    def get_industry_list() -> pd.DataFrame:
        """获取行业板块列表

        Returns:
            行业列表
        """
        cache_key = "industry_list"
        cached = _cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            df = ak.stock_board_industry_name_em()
            if df is not None and not df.empty:
                _cache.set(cache_key, df, ttl=3600)
                return df
        except Exception as e:
            logger.warning(f"获取行业列表失败: {e}")

        return pd.DataFrame()

    @staticmethod
    def get_industry_stocks(industry: str, limit: int = 50) -> pd.DataFrame:
        """获取行业成分股

        Args:
            industry: 行业名称
            limit: 返回数量

        Returns:
            行业成分股
        """
        cache_key = f"industry_stocks_{industry}"
        cached = _cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            df = ak.stock_board_industry_cons_em(symbol=industry)
            if df is not None and not df.empty:
                df = df.head(limit)
                _cache.set(cache_key, df, ttl=3600)
                return df
        except Exception as e:
            logger.warning(f"获取行业成分股失败: {e}")

        return pd.DataFrame()

    @staticmethod
    def get_concept_list() -> pd.DataFrame:
        """获取概念板块列表

        Returns:
            概念板块列表
        """
        cache_key = "concept_list"
        cached = _cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            df = ak.stock_board_concept_name_em()
            if df is not None and not df.empty:
                _cache.set(cache_key, df, ttl=3600)
                return df
        except Exception as e:
            logger.warning(f"获取概念列表失败: {e}")

        return pd.DataFrame()

    @staticmethod
    def get_concept_stocks(concept: str, limit: int = 50) -> pd.DataFrame:
        """获取概念成分股

        Args:
            concept: 概念名称
            limit: 返回数量

        Returns:
            概念成分股
        """
        cache_key = f"concept_stocks_{concept}"
        cached = _cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            df = ak.stock_board_concept_cons_em(symbol=concept)
            if df is not None and not df.empty:
                df = df.head(limit)
                _cache.set(cache_key, df, ttl=3600)
                return df
        except Exception as e:
            logger.warning(f"获取概念成分股失败: {e}")

        return pd.DataFrame()


# ============================================================
# 研报数据接口
# ============================================================

class ReportDataProvider:
    """研报数据提供者"""

    @staticmethod
    def get_research_reports(symbol: str, limit: int = 10) -> pd.DataFrame:
        """获取个股研报

        Args:
            symbol: 股票代码
            limit: 返回数量

        Returns:
            研报数据
        """
        cache_key = f"research_reports_{symbol}"
        cached = _cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            df = ak.stock_research_report_em(symbol=symbol)
            if df is not None and not df.empty:
                df = df.head(limit)
                _cache.set(cache_key, df, ttl=3600)
                return df
        except Exception as e:
            logger.warning(f"获取研报失败: {e}")

        return pd.DataFrame()

    @staticmethod
    def get_stock_forecast(symbol: str, limit: int = 5) -> pd.DataFrame:
        """获取业绩预测

        Args:
            symbol: 股票代码
            limit: 返回数量

        Returns:
            业绩预测数据
        """
        cache_key = f"forecast_{symbol}"
        cached = _cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            df = ak.stock_financial_forecast_em(symbol=symbol)
            if df is not None and not df.empty:
                df = df.head(limit)
                _cache.set(cache_key, df, ttl=3600)
                return df
        except Exception as e:
            logger.warning(f"获取业绩预测失败: {e}")

        return pd.DataFrame()


# ============================================================
# 资金流向接口
# ============================================================

class FundFlowProvider:
    """资金流向提供者"""

    @staticmethod
    def get_fund_flow(symbol: str, days: int = 5) -> pd.DataFrame:
        """获取个股资金流向

        Args:
            symbol: 股票代码
            days: 天数

        Returns:
            资金流向数据
        """
        cache_key = f"fund_flow_{symbol}_{days}"
        cached = _cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            df = ak.stock_individual_fund_flow(stock=symbol, market="sh")
            if df is not None and not df.empty:
                df = df.head(days)
                _cache.set(cache_key, df, ttl=300)  # 缓存5分钟
                return df
        except Exception as e:
            # 尝试深市
            try:
                df = ak.stock_individual_fund_flow(stock=symbol, market="sz")
                if df is not None and not df.empty:
                    df = df.head(days)
                    _cache.set(cache_key, df, ttl=300)
                    return df
            except Exception as e2:
                logger.warning(f"获取资金流向失败: {e2}")

        return pd.DataFrame()

    @staticmethod
    def get_sector_fund_flow(limit: int = 10) -> pd.DataFrame:
        """获取板块资金流向

        Args:
            limit: 返回数量

        Returns:
            板块资金流向
        """
        cache_key = f"sector_fund_flow_{limit}"
        cached = _cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            df = ak.stock_sector_fund_flow_rank(indicator="今日", sector_type="行业资金流")
            if df is not None and not df.empty:
                df = df.head(limit)
                _cache.set(cache_key, df, ttl=300)
                return df
        except Exception as e:
            logger.warning(f"获取板块资金流向失败: {e}")

        return pd.DataFrame()


# ============================================================
# 龙虎榜接口
# ============================================================

class TopListProvider:
    """龙虎榜数据提供者"""

    @staticmethod
    def get_top_list(date: str = None) -> pd.DataFrame:
        """获取当日龙虎榜

        Args:
            date: 日期 (YYYYMMDD)，默认最新

        Returns:
            龙虎榜数据
        """
        cache_key = f"top_list_{date or 'latest'}"
        cached = _cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            df = ak.stock_top_list_em(date=date)
            if df is not None and not df.empty:
                _cache.set(cache_key, df, ttl=3600)
                return df
        except Exception as e:
            logger.warning(f"获取龙虎榜失败: {e}")

        return pd.DataFrame()

    @staticmethod
    def get_top_inst(symbol: str, date: str = None) -> pd.DataFrame:
        """获取龙虎榜机构明细

        Args:
            symbol: 股票代码
            date: 日期

        Returns:
            机构明细
        """
        cache_key = f"top_inst_{symbol}_{date or 'latest'}"
        cached = _cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            df = ak.stock_top_inst_em(symbol=symbol, date=date)
            if df is not None and not df.empty:
                _cache.set(cache_key, df, ttl=3600)
                return df
        except Exception as e:
            logger.warning(f"获取龙虎榜机构明细失败: {e}")

        return pd.DataFrame()


# ============================================================
# 融资融券接口
# ============================================================

class MarginProvider:
    """融资融券数据提供者"""

    @staticmethod
    def get_margin_detail(symbol: str) -> pd.DataFrame:
        """获取个股融资融券明细

        Args:
            symbol: 股票代码

        Returns:
            融资融券明细
        """
        cache_key = f"margin_{symbol}"
        cached = _cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            df = ak.stock_margin_detail(symbol=symbol)
            if df is not None and not df.empty:
                _cache.set(cache_key, df, ttl=300)
                return df
        except Exception as e:
            logger.warning(f"获取融资融券明细失败: {e}")

        return pd.DataFrame()

    @staticmethod
    def get_margin_sx() -> pd.DataFrame:
        """获取融资融券余额

        Returns:
            融资融券余额
        """
        cache_key = "margin_sx"
        cached = _cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            df = ak.stock_margin_sx()
            if df is not None and not df.empty:
                _cache.set(cache_key, df, ttl=300)
                return df
        except Exception as e:
            logger.warning(f"获取融资融券余额失败: {e}")

        return pd.DataFrame()


# ============================================================
# 宏观数据接口
# ============================================================

class MacroDataProvider:
    """宏观数据提供者"""

    @staticmethod
    def get_gdp_data(quarter: str = None) -> pd.DataFrame:
        """获取GDP数据

        Args:
            quarter: 季度 (YYYYQX)，如 2024Q1

        Returns:
            GDP数据
        """
        cache_key = f"gdp_{quarter or 'all'}"
        cached = _cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            df = ak.macro_china_gdp()
            if df is not None and not df.empty:
                if quarter:
                    df = df[df['季度'].str.contains(quarter)]
                _cache.set(cache_key, df, ttl=86400)  # 缓存1天
                return df
        except Exception as e:
            logger.warning(f"获取GDP数据失败: {e}")

        return pd.DataFrame()

    @staticmethod
    def get_cpi_data(month: str = None) -> pd.DataFrame:
        """获取CPI数据

        Args:
            month: 月份 (YYYYMM)

        Returns:
            CPI数据
        """
        cache_key = f"cpi_{month or 'all'}"
        cached = _cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            df = ak.macro_china_cpi()
            if df is not None and not df.empty:
                if month:
                    df = df[df['月份'].str.contains(month)]
                _cache.set(cache_key, df, ttl=86400)
                return df
        except Exception as e:
            logger.warning(f"获取CPI数据失败: {e}")

        return pd.DataFrame()

    @staticmethod
    def get_money_supply() -> pd.DataFrame:
        """获取货币供应量数据

        Returns:
            货币供应量数据
        """
        cache_key = "money_supply"
        cached = _cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            df = ak.macro_china_m2()
            if df is not None and not df.empty:
                _cache.set(cache_key, df, ttl=86400)
                return df
        except Exception as e:
            logger.warning(f"获取货币供应量失败: {e}")

        return pd.DataFrame()

    @staticmethod
    def get_pmi_data() -> pd.DataFrame:
        """获取PMI数据

        Returns:
            PMI数据
        """
        cache_key = "pmi_data"
        cached = _cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            df = ak.macro_china_pmi()
            if df is not None and not df.empty:
                _cache.set(cache_key, df, ttl=86400)
                return df
        except Exception as e:
            logger.warning(f"获取PMI数据失败: {e}")

        return pd.DataFrame()

    @staticmethod
    def get_freight_index() -> pd.DataFrame:
        """获取波罗的海运费指数

        Returns:
            运费指数
        """
        cache_key = "freight_index"
        cached = _cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            df = ak.bd_index()
            if df is not None and not df.empty:
                _cache.set(cache_key, df, ttl=3600)
                return df
        except Exception as e:
            logger.warning(f"获取运费指数失败: {e}")

        return pd.DataFrame()

    @staticmethod
    def get_interest_rate() -> pd.DataFrame:
        """获取利率数据

        Returns:
            利率数据
        """
        cache_key = "interest_rate"
        cached = _cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            df = ak.macro_china_lpr()
            if df is not None and not df.empty:
                _cache.set(cache_key, df, ttl=86400)
                return df
        except Exception as e:
            logger.warning(f"获取利率数据失败: {e}")

        return pd.DataFrame()


# ============================================================
# 大宗交易接口
# ============================================================

class BlockTradeProvider:
    """大宗交易数据提供者"""

    @staticmethod
    def get_block_trades(symbol: str = None, date: str = None, limit: int = 20) -> pd.DataFrame:
        """获取大宗交易数据

        Args:
            symbol: 股票代码
            date: 日期 (YYYYMMDD)
            limit: 返回数量

        Returns:
            大宗交易数据
        """
        cache_key = f"block_trade_{symbol}_{date}_{limit}"
        cached = _cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            df = ak.stock_block_trade(date=date)
            if df is not None and not df.empty:
                if symbol:
                    df = df[df['股票代码'].astype(str).str.contains(symbol)]
                df = df.head(limit)
                _cache.set(cache_key, df, ttl=3600)
                return df
        except Exception as e:
            logger.warning(f"获取大宗交易失败: {e}")

        return pd.DataFrame()


# ============================================================
# 股东数据接口
# ============================================================

class HolderProvider:
    """股东数据提供者"""

    @staticmethod
    def get_holder_trade(symbol: str, limit: int = 10) -> pd.DataFrame:
        """获取股东增减持数据

        Args:
            symbol: 股票代码
            limit: 返回数量

        Returns:
            股东增减持数据
        """
        cache_key = f"holder_trade_{symbol}_{limit}"
        cached = _cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            df = ak.stock_holder_trade(stock=symbol)
            if df is not None and not df.empty:
                df = df.head(limit)
                _cache.set(cache_key, df, ttl=3600)
                return df
        except Exception as e:
            logger.warning(f"获取股东增减持失败: {e}")

        return pd.DataFrame()
