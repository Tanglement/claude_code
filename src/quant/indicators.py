"""技术指标计算模块

提供常用的股票技术指标计算：
- 移动平均线 (MA)
- 指数移动平均线 (EMA)
- MACD
- RSI
- KDJ
- 布林带 (Bollinger Bands)
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


@dataclass
class IndicatorResult:
    """指标计算结果"""
    name: str
    value: float
    signal: str  # buy, sell, neutral
    description: str


class IndicatorCalculator:
    """技术指标计算器"""

    @staticmethod
    def calculate_ma(prices: pd.Series, period: int) -> pd.Series:
        """计算简单移动平均线 (MA)

        Args:
            prices: 价格序列
            period: 周期

        Returns:
            MA 值序列
        """
        return prices.rolling(window=period).mean()

    @staticmethod
    def calculate_ema(prices: pd.Series, period: int) -> pd.Series:
        """计算指数移动平均线 (EMA)

        Args:
            prices: 价格序列
            period: 周期

        Returns:
            EMA 值序列
        """
        return prices.ewm(span=period, adjust=False).mean()

    @staticmethod
    def calculate_macd(prices: pd.Series,
                      fast: int = 12,
                      slow: int = 26,
                      signal: int = 9) -> Dict[str, pd.Series]:
        """计算 MACD 指标

        Args:
            prices: 价格序列
            fast: 快线周期
            slow: 慢线周期
            signal: 信号线周期

        Returns:
            包含 macd, signal, histogram 的字典
        """
        ema_fast = prices.ewm(span=fast, adjust=False).mean()
        ema_slow = prices.ewm(span=slow, adjust=False).mean()

        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line

        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }

    @staticmethod
    def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """计算相对强弱指标 (RSI)

        Args:
            prices: 价格序列
            period: 周期

        Returns:
            RSI 值序列 (0-100)
        """
        delta = prices.diff()

        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()

        # 使用 EMA 方式计算平均
        avg_gain = gain.ewm(span=period, adjust=False).mean()
        avg_loss = loss.ewm(span=period, adjust=False).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    @staticmethod
    def calculate_kdj(high: pd.Series,
                     low: pd.Series,
                     close: pd.Series,
                     period: int = 9) -> Dict[str, pd.Series]:
        """计算 KDJ 随机指标

        Args:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            period: 周期

        Returns:
            包含 k, d, j 的字典
        """
        lowest_low = low.rolling(window=period).min()
        highest_high = high.rolling(window=period).max()

        rsv = (close - lowest_low) / (highest_high - lowest_low) * 100

        k = rsv.ewm(com=2, adjust=False).mean()
        d = k.ewm(com=2, adjust=False).mean()
        j = 3 * k - 2 * d

        return {
            'k': k,
            'd': d,
            'j': j
        }

    @staticmethod
    def calculate_bollinger_bands(prices: pd.Series,
                                period: int = 20,
                                std_dev: float = 2.0) -> Dict[str, pd.Series]:
        """计算布林带

        Args:
            prices: 价格序列
            period: 周期
            std_dev: 标准差倍数

        Returns:
            包含 upper, middle, lower 的字典
        """
        middle = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()

        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)

        return {
            'upper': upper,
            'middle': middle,
            'lower': lower
        }

    @staticmethod
    def calculate_atr(high: pd.Series,
                    low: pd.Series,
                    close: pd.Series,
                    period: int = 14) -> pd.Series:
        """计算平均真实波幅 (ATR)

        Args:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            period: 周期

        Returns:
            ATR 值序列
        """
        high_low = high - low
        high_close = (high - close.shift()).abs()
        low_close = (low - close.shift()).abs()

        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()

        return atr

    @staticmethod
    def calculate_obv(close: pd.Series, volume: pd.Series) -> pd.Series:
        """计算能量潮指标 (OBV)

        Args:
            close: 收盘价序列
            volume: 成交量序列

        Returns:
            OBV 值序列
        """
        obv = pd.Series(index=close.index, dtype=float)
        obv.iloc[0] = volume.iloc[0]

        for i in range(1, len(close)):
            if close.iloc[i] > close.iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] + volume.iloc[i]
            elif close.iloc[i] < close.iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] - volume.iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i-1]

        return obv

    @staticmethod
    def calculate_ema_12_26(close: pd.Series) -> Tuple[float, float]:
        """计算 EMA(12) 和 EMA(26) 的当前值

        Args:
            close: 收盘价序列

        Returns:
            (ema_12, ema_26) 元组
        """
        ema_12 = close.ewm(span=12, adjust=False).mean().iloc[-1]
        ema_26 = close.ewm(span=26, adjust=False).mean().iloc[-1]
        return ema_12, ema_26


class SignalGenerator:
    """交易信号生成器"""

    @staticmethod
    def generate_rsi_signal(rsi: float) -> str:
        """基于 RSI 生成交易信号

        Args:
            rsi: RSI 值 (0-100)

        Returns:
            信号: buy, sell, neutral
        """
        if rsi < 30:
            return 'buy'  # 超卖，可能反弹
        elif rsi > 70:
            return 'sell'  # 超买，可能回调
        else:
            return 'neutral'

    @staticmethod
    def generate_macd_signal(macd: float, signal: float, histogram: float) -> str:
        """基于 MACD 生成交易信号

        Args:
            macd: MACD 线值
            signal: 信号线值
            histogram: 柱状图值

        Returns:
            信号: buy, sell, neutral
        """
        if histogram > 0 and histogram > histogram.shift(1) if hasattr(histogram, 'shift') else 0:
            return 'buy'  # 金叉且动能增强
        elif histogram < 0 and histogram < histogram.shift(1) if hasattr(histogram, 'shift') else 0:
            return 'sell'  # 死叉且动能减弱
        else:
            return 'neutral'

    @staticmethod
    def generate_kdj_signal(k: float, d: float, j: float) -> str:
        """基于 KDJ 生成交易信号

        Args:
            k: K 值
            d: D 值
            j: J 值

        Returns:
            信号: buy, sell, neutral
        """
        if k < 20 and d < 20 and j < 20:
            return 'buy'  # 超卖区域
        elif k > 80 and d > 80 and j > 80:
            return 'sell'  # 超买区域
        elif k > d and k > 80:  # K上穿D
            return 'buy'
        elif k < d and k < 20:  # K下穿D
            return 'sell'
        else:
            return 'neutral'

    @staticmethod
    def generate_ma_signal(price: float, ma5: float, ma10: float, ma20: float) -> str:
        """基于均线生成交易信号

        Args:
            price: 当前价格
            ma5: 5日均线
            ma10: 10日均线
            ma20: 20日均线

        Returns:
            信号: buy, sell, neutral
        """
        # 多头排列: 价格 > MA5 > MA10 > MA20
        if price > ma5 > ma10 > ma20:
            return 'buy'
        # 空头排列: 价格 < MA5 < MA10 < MA20
        elif price < ma5 < ma10 < ma20:
            return 'sell'
        else:
            return 'neutral'


# 便捷函数
def calculate_all_indicators(df: pd.DataFrame) -> Dict[str, any]:
    """计算所有技术指标

    Args:
        df: 包含 high, low, close, volume 列的 DataFrame

    Returns:
        包含所有指标的字典
    """
    calc = IndicatorCalculator()
    result = {}

    # 均线
    result['ma5'] = calc.calculate_ma(df['close'], 5)
    result['ma10'] = calc.calculate_ma(df['close'], 10)
    result['ma20'] = calc.calculate_ma(df['close'], 20)
    result['ma60'] = calc.calculate_ma(df['close'], 60)

    # EMA
    result['ema12'], result['ema26'] = calc.calculate_ema_12_26(df['close'])

    # MACD
    macd = calc.calculate_macd(df['close'])
    result['macd'] = macd['macd'].iloc[-1] if len(macd['macd']) > 0 else 0
    result['macd_signal'] = macd['signal'].iloc[-1] if len(macd['signal']) > 0 else 0
    result['macd_histogram'] = macd['histogram'].iloc[-1] if len(macd['histogram']) > 0 else 0

    # RSI
    result['rsi'] = calc.calculate_rsi(df['close']).iloc[-1]

    # KDJ
    kdj = calc.calculate_kdj(df['high'], df['low'], df['close'])
    result['k'] = kdj['k'].iloc[-1] if len(kdj['k']) > 0 else 0
    result['d'] = kdj['d'].iloc[-1] if len(kdj['d']) > 0 else 0
    result['j'] = kdj['j'].iloc[-1] if len(kdj['j']) > 0 else 0

    # 布林带
    bb = calc.calculate_bollinger_bands(df['close'])
    result['bb_upper'] = bb['upper'].iloc[-1] if len(bb['upper']) > 0 else 0
    result['bb_middle'] = bb['middle'].iloc[-1] if len(bb['middle']) > 0 else 0
    result['bb_lower'] = bb['lower'].iloc[-1] if len(bb['lower']) > 0 else 0

    return result
