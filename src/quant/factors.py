"""量化因子库

提供常用量化因子计算：
- 资金流向因子
- 波动率因子
- 动量因子
- 成交量因子
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


@dataclass
class FactorResult:
    """因子计算结果"""
    name: str
    value: float
    unit: str  # 亿元, 万元, % 等
    description: str


class FactorCalculator:
    """因子计算器"""

    @staticmethod
    def calculate_money_flow(df: pd.DataFrame,
                            period: int = 5) -> Dict[str, float]:
        """计算资金流向因子

        Args:
            df: 包含 close, volume 列的 DataFrame
            period: 计算周期

        Returns:
            资金流向相关因子
        """
        close = df['close']
        volume = df['volume']

        # 假设价格单位为元，成交量单位为股
        # 成交额 = 价格 * 成交量
        amount = close * volume

        # 主力资金净流入 (近似计算: 大单+超大单)
        # 这里简化处理: 假设大单为成交量的30%
        main_flow = amount * 0.3

        # 计算N日主力资金净流入
        main_flow_sum = main_flow.rolling(window=period).sum().iloc[-1] if len(main_flow) >= period else main_flow.sum()

        # 主力资金净流入率
        total_amount = amount.rolling(window=period).sum().iloc[-1] if len(amount) >= period else amount.sum()
        main_flow_rate = (main_flow_sum / total_amount * 100) if total_amount > 0 else 0

        # 资金流向趋势
        if len(main_flow) >= period * 2:
            current = main_flow.rolling(window=period).sum().iloc[-1]
            previous = main_flow.rolling(window=period).sum().iloc[-period-1]
            flow_trend = (current - previous) / abs(previous) * 100 if previous != 0 else 0
        else:
            flow_trend = 0

        return {
            'main_flow': float(main_flow_sum),
            'main_flow_rate': float(main_flow_rate),
            'flow_trend': float(flow_trend)
        }

    @staticmethod
    def calculate_volatility(df: pd.DataFrame,
                            period: int = 20) -> Dict[str, float]:
        """计算波动率因子

        Args:
            df: 包含 close 列的 DataFrame
            period: 计算周期

        Returns:
            波动率相关因子
        """
        close = df['close']

        # 日收益率
        returns = close.pct_change()

        # 历史波动率 (年化)
        daily_volatility = returns.rolling(window=period).std().iloc[-1] if len(returns) >= period else 0
        annualized_volatility = daily_volatility * np.sqrt(252)  # 年化

        # 价格波动范围
        price_range = (close.max() - close.min()) / close.min() * 100 if len(close) > 0 else 0

        # 布林带宽度
        ma = close.rolling(window=period).mean()
        std = close.rolling(window=period).std()
        bb_width = ((ma + 2*std) - (ma - 2*std)) / ma * 100

        return {
            'daily_volatility': float(daily_volatility),
            'annualized_volatility': float(annualized_volatility),
            'price_range': float(price_range),
            'bb_width': float(bb_width.iloc[-1]) if len(bb_width) > 0 else 0
        }

    @staticmethod
    def calculate_momentum(df: pd.DataFrame,
                         periods: List[int] = [5, 10, 20]) -> Dict[str, float]:
        """计算动量因子

        Args:
            df: 包含 close 列的 DataFrame
            periods: 计算周期列表

        Returns:
            动量相关因子
        """
        close = df['close']
        result = {}

        for period in periods:
            # 区间收益率
            if len(close) >= period:
                momentum = (close.iloc[-1] - close.iloc[-period]) / close.iloc[-period] * 100
            else:
                momentum = 0
            result[f'momentum_{period}d'] = float(momentum)

            # 区间累计收益率 (简化)
            cum_return = (close / close.iloc[0] - 1) * 100 if len(close) > 0 else 0
            result[f'cum_return_{period}d'] = float(cum_return)

        return result

    @staticmethod
    def calculate_volume_factors(df: pd.DataFrame,
                                 period: int = 5) -> Dict[str, float]:
        """计算成交量因子

        Args:
            df: 包含 volume, close 列的 DataFrame
            period: 计算周期

        Returns:
            成交量相关因子
        """
        volume = df['volume']
        close = df['close']

        # 成交量变化率
        vol_change = volume.pct_change().iloc[-1] * 100 if len(volume) > 1 else 0

        # 成交量均线
        vol_ma = volume.rolling(window=period).mean().iloc[-1] if len(volume) >= period else volume.mean()

        # 量价配合度 (成交量与价格变化的相关性)
        price_change = close.pct_change()
        if len(volume) >= period and price_change.std() != 0:
            correlation = volume.rolling(window=period).corr(price_change).iloc[-1]
        else:
            correlation = 0

        # 放量缩量指标
        avg_volume = volume.rolling(window=period).mean()
        volume_ratio = (volume.iloc[-1] / avg_volume.iloc[-1]) if len(avg_volume) > 0 and avg_volume.iloc[-1] != 0 else 1

        return {
            'vol_change': float(vol_change),
            'vol_ma': float(vol_ma),
            'vol_price_correlation': float(correlation),
            'volume_ratio': float(volume_ratio)
        }

    @staticmethod
    def calculate_price_factors(df: pd.DataFrame) -> Dict[str, float]:
        """计算价格相关因子

        Args:
            df: 包含 high, low, close, open 列的 DataFrame

        Returns:
            价格相关因子
        """
        close = df['close']
        high = df['high']
        low = df['low']
        open_price = df['open']

        # 当前价格位置 (在N日区间中的位置)
        period = 20
        if len(close) >= period:
            price_position = (close.iloc[-1] - low.rolling(window=period).min().iloc[-1]) / \
                           (high.rolling(window=period).max().iloc[-1] - low.rolling(window=period).min().iloc[-1]) * 100 \
                           if (high.rolling(window=period).max().iloc[-1] - low.rolling(window=period).min().iloc[-1]) != 0 else 50
        else:
            price_position = 50

        # 涨跌停判断
        is_limit_up = False
        is_limit_down = False
        if len(close) >= 2:
            prev_close = close.iloc[-2]
            if close.iloc[-1] >= prev_close * 1.10:  # 10% 涨停
                is_limit_up = True
            elif close.iloc[-1] <= prev_close * 0.90:  # 10% 跌停
                is_limit_down = True

        # 上下影线比例
        if len(close) > 0:
            upper_shadow = high.iloc[-1] - max(open_price.iloc[-1], close.iloc[-1])
            lower_shadow = min(open_price.iloc[-1], close.iloc[-1]) - low.iloc[-1]
            body = abs(close.iloc[-1] - open_price.iloc[-1])
            shadow_ratio = (upper_shadow + lower_shadow) / body if body != 0 else 0
        else:
            shadow_ratio = 0

        return {
            'price_position': float(price_position),
            'is_limit_up': is_limit_up,
            'is_limit_down': is_limit_down,
            'shadow_ratio': float(shadow_ratio)
        }

    @staticmethod
    def calculate_all_factors(df: pd.DataFrame) -> Dict[str, float]:
        """计算所有因子

        Args:
            df: 包含所需列的 DataFrame

        Returns:
            所有因子的字典
        """
        result = {}

        # 资金流因子
        result.update(FactorCalculator.calculate_money_flow(df))

        # 波动率因子
        result.update(FactorCalculator.calculate_volatility(df))

        # 动量因子
        result.update(FactorCalculator.calculate_momentum(df))

        # 成交量因子
        result.update(FactorCalculator.calculate_volume_factors(df))

        # 价格因子
        result.update(FactorCalculator.calculate_price_factors(df))

        return result


class FactorCompositor:
    """因子合成器 - 将多个因子组合成综合评分"""

    @staticmethod
    def calculate_composite_score(factors: Dict[str, float],
                                 weights: Optional[Dict[str, float]] = None) -> float:
        """计算综合评分

        Args:
            factors: 因子字典
            weights: 因子权重 (可选)

        Returns:
            综合评分 (-100 到 100)
        """
        # 默认权重
        if weights is None:
            weights = {
                'momentum_5d': 15,
                'momentum_10d': 10,
                'rsi': 15,
                'main_flow_rate': 20,
                'volume_ratio': 10,
                'price_position': 15,
                'vol_change': 15
            }

        score = 0
        total_weight = 0

        for factor_name, weight in weights.items():
            if factor_name in factors:
                value = factors[factor_name]

                # 归一化处理
                if factor_name in ['rsi']:
                    # RSI: 0-100 -> -50 到 50
                    normalized = (value - 50) * weight / 100 * 2
                elif factor_name in ['momentum_5d', 'momentum_10d']:
                    # 动量: 假设范围 -20% 到 20%
                    normalized = (value / 20) * weight
                elif factor_name in ['main_flow_rate', 'volume_ratio']:
                    # 资金流: 假设范围 -50% 到 50%
                    normalized = (value / 50) * weight
                elif factor_name in ['price_position']:
                    # 价格位置: 0-100 -> -50 到 50
                    normalized = (value - 50) * weight / 100 * 2
                elif factor_name in ['vol_change']:
                    # 成交量变化: 假设范围 -100% 到 100%
                    normalized = (value / 100) * weight
                else:
                    normalized = 0

                score += normalized
                total_weight += weight

        # 归一化到 -100 到 100
        if total_weight > 0:
            score = score / total_weight * 100

        return float(score)

    @staticmethod
    def generate_trading_signal(score: float,
                               buy_threshold: float = 30,
                               sell_threshold: float = -30) -> str:
        """基于综合评分生成交易信号

        Args:
            score: 综合评分
            buy_threshold: 买入阈值
            sell_threshold: 卖出阈值

        Returns:
            信号: buy, sell, neutral
        """
        if score > buy_threshold:
            return 'buy'
        elif score < sell_threshold:
            return 'sell'
        else:
            return 'neutral'
