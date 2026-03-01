"""决策调度器

多智能体协作的核心决策模块：
- 整合技术指标、资金流向、新闻舆情
- 生成综合投资决策
- 调用风控模块进行审核
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json

from src.agents.base import BaseAgent, AgentResponse
from src.agents.news_analyst import NewsAnalyst
from src.quant.indicators import SignalGenerator, calculate_all_indicators
from src.quant.factors import FactorCalculator, FactorCompositor
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class DecisionResult:
    """决策结果"""
    decision: str  # 强烈买入/买入/观望/卖出/强烈卖出
    position: int  # 仓位建议 0-100
    confidence: float  # 决策置信度 0-10
    reason: str  # 决策理由
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class DecisionMaker(BaseAgent):
    """决策调度器 Agent

    工作流程:
    1. 收集数据: 行情数据、技术指标、资金流向
    2. 技术分析: 计算 RSI/MACD/KDJ 等信号
    3. 舆情分析: 调用 NewsAnalyst 分析新闻
    4. 综合打分: 因子合成
    5. 决策输出: 生成交易建议
    """

    def __init__(self):
        """初始化决策调度器"""
        super().__init__(name="DecisionMaker")
        self.news_analyst = NewsAnalyst()
        self.signal_generator = SignalGenerator()
        self.factor_calculator = FactorCalculator()
        self.factor_compositor = FactorCompositor()

    def run(self,
           symbol: str,
           price: float,
           market_data: Dict,
           news_list: List[Dict] = None,
           stock_name: str = '') -> AgentResponse:
        """执行决策

        Args:
            symbol: 股票代码
            price: 当前价格
            market_data: 市场数据 (需包含 open/high/low/close/volume)
            news_list: 新闻列表 (可选)
            stock_name: 股票名称

        Returns:
            AgentResponse，包含 DecisionResult
        """
        try:
            # Step 1: 技术指标分析
            indicators = self._analyze_indicators(market_data)

            # Step 2: 资金流向分析
            factors = self._analyze_factors(market_data)

            # Step 3: 新闻舆情分析
            sentiment_score = 0
            if news_list and len(news_list) > 0:
                sentiment_score = self._analyze_news(news_list, symbol, stock_name or symbol)

            # Step 4: 综合打分
            composite_score = self._calculate_composite_score(
                indicators, factors, sentiment_score
            )

            # Step 5: 生成决策
            decision = self._generate_decision(
                indicators, factors, sentiment_score, composite_score
            )

            return AgentResponse(
                success=True,
                data=decision
            )

        except Exception as e:
            logger.error(f"Decision making error: {e}")
            return AgentResponse(
                success=False,
                data=None,
                error=str(e)
            )

    def _analyze_indicators(self, market_data: Dict) -> Dict:
        """分析技术指标"""
        import pandas as pd

        # 构建 DataFrame
        df = pd.DataFrame([market_data])

        # 计算指标
        indicators = calculate_all_indicators(df)

        # 生成信号
        rsi = indicators.get('rsi', 50)
        k = indicators.get('k', 50)
        d = indicators.get('d', 50)
        j = indicators.get('j', 50)

        rsi_signal = self.signal_generator.generate_rsi_signal(rsi)
        kdj_signal = self.signal_generator.generate_kdj_signal(k, d, j)

        # 均线信号
        ma_signal = 'neutral'
        if 'ma5' in indicators and 'ma10' in indicators:
            price = df['close'].iloc[-1] if len(df) > 0 else 0
            ma_signal = self.signal_generator.generate_ma_signal(
                price,
                indicators.get('ma5', 0),
                indicators.get('ma10', 0),
                indicators.get('ma20', 0)
            )

        return {
            'rsi': rsi,
            'rsi_signal': rsi_signal,
            'kdj_signal': kdj_signal,
            'ma_signal': ma_signal,
            'macd_histogram': indicators.get('macd_histogram', 0)
        }

    def _analyze_factors(self, market_data: Dict) -> Dict:
        """分析资金流向"""
        import pandas as pd

        df = pd.DataFrame([market_data])
        factors = FactorCalculator.calculate_all_factors(df)

        return factors

    def _analyze_news(self, news_list: List[Dict], symbol: str, name: str) -> float:
        """分析新闻舆情"""
        try:
            result = self.news_analyst.run(
                news=news_list[:5],  # 取最新5条
                symbol=symbol,
                name=name,
                batch=True
            )

            if result.success and 'composite_score' in result.data:
                return result.data['composite_score']

        except Exception as e:
            logger.warning(f"News analysis failed: {e}")

        return 0  # 默认中性

    def _calculate_composite_score(self,
                                  indicators: Dict,
                                  factors: Dict,
                                  sentiment_score: float) -> float:
        """计算综合评分"""
        # 构建因子字典
        factor_dict = {
            'rsi': indicators.get('rsi', 50),
            'momentum_5d': factors.get('momentum_5d', 0),
            'main_flow_rate': factors.get('main_flow_rate', 0),
            'volume_ratio': factors.get('volume_ratio', 1),
        }

        # 添加舆情分数
        factor_dict['sentiment'] = sentiment_score * 100  # 转换为 -100 到 100

        # 计算综合评分
        weights = {
            'rsi': 15,
            'momentum_5d': 15,
            'main_flow_rate': 20,
            'volume_ratio': 10,
            'sentiment': 20
        }

        score = self.factor_compositor.calculate_composite_score(factor_dict, weights)

        return score

    def _generate_decision(self,
                          indicators: Dict,
                          factors: Dict,
                          sentiment_score: float,
                          composite_score: float) -> DecisionResult:
        """生成投资决策"""
        # 基于综合评分判断
        if composite_score > 50:
            decision = "强烈买入"
            position = min(100, int(50 + composite_score))
            confidence = min(10, (composite_score - 50) / 5 + 5)
        elif composite_score > 30:
            decision = "买入"
            position = min(80, int(30 + composite_score / 2))
            confidence = min(10, (composite_score - 30) / 2 + 5)
        elif composite_score > -30:
            decision = "观望"
            position = min(30, int((composite_score + 30)))
            confidence = 5
        elif composite_score > -50:
            decision = "卖出"
            position = max(0, 50 + int(composite_score / 2))
            confidence = min(10, (-composite_score - 30) / 2 + 5)
        else:
            decision = "强烈卖出"
            position = max(0, 50 + int(composite_score))
            confidence = min(10, (-composite_score - 50) / 5 + 5)

        # 生成理由
        reason_parts = []

        # 技术面
        if indicators.get('rsi_signal') == 'buy':
            reason_parts.append("RSI超卖")
        elif indicators.get('rsi_signal') == 'sell':
            reason_parts.append("RSI超买")

        if indicators.get('kdj_signal') == 'buy':
            reason_parts.append("KDJ金叉")
        elif indicators.get('kdj_signal') == 'sell':
            reason_parts.append("KDJ死叉")

        # 资金面
        main_flow = factors.get('main_flow', 0)
        if main_flow > 100000000:  # 1亿
            reason_parts.append("主力资金大幅流入")
        elif main_flow < -100000000:
            reason_parts.append("主力资金大幅流出")

        # 舆情
        if sentiment_score > 0.3:
            reason_parts.append("舆情利好")
        elif sentiment_score < -0.3:
            reason_parts.append("舆情利空")

        reason = "; ".join(reason_parts) if reason_parts else "综合分析"

        return DecisionResult(
            decision=decision,
            position=position,
            confidence=confidence,
            reason=reason
        )


# 便捷函数
def make_decision(symbol: str,
                 price: float,
                 market_data: Dict,
                 news_list: List[Dict] = None,
                 stock_name: str = '') -> AgentResponse:
    """快速决策

    Args:
        symbol: 股票代码
        price: 当前价格
        market_data: 市场数据
        news_list: 新闻列表
        stock_name: 股票名称

    Returns:
        决策结果
    """
    maker = DecisionMaker()
    return maker.run(symbol, price, market_data, news_list, stock_name)
