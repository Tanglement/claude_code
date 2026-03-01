"""分析服务模块

整合股票数据分析功能：
- 新闻分析
- 公告分析
- 综合研报分析
"""

from typing import Dict, List, Optional
import pandas as pd

from src.services.data_provider import (
    MarketDataProvider,
    FundamentalProvider,
    StockQuoteClient
)
from src.agents.news_analyst import NewsAnalyst, quick_analyze_news
from src.agents.base import LLMClient, MockLLMClient, AgentResponse
from src.utils.logger import get_logger

logger = get_logger(__name__)


class StockAnalysisService:
    """股票分析服务"""

    def __init__(self, use_llm: bool = False, llm_provider: str = 'openai'):
        """初始化分析服务

        Args:
            use_llm: 是否使用 LLM 进行分析
            llm_provider: LLM 提供商
        """
        self.use_llm = use_llm
        if use_llm:
            self.llm_client = LLMClient(provider=llm_provider)
        else:
            self.llm_client = MockLLMClient()
        self.news_analyst = NewsAnalyst(self.llm_client)

    def analyze_stock(self, symbol: str) -> Dict:
        """综合分析股票

        Args:
            symbol: 股票代码

        Returns:
            分析结果字典
        """
        result = {
            'symbol': symbol,
            'realtime': {},
            'news': [],
            'announcements': [],
            'analysis': {}
        }

        # 1. 获取实时行情
        try:
            quotes = StockQuoteClient.get_quote([symbol])
            if not quotes.empty:
                q = quotes.iloc[0]
                result['realtime'] = {
                    'price': float(q.get('close', 0)),
                    'change_pct': float(q.get('change_pct', 0)),
                    'volume': int(q.get('volume', 0)) if q.get('volume') else 0
                }
        except Exception as e:
            logger.warning(f"获取实时行情失败: {e}")

        # 2. 获取新闻
        try:
            news_df = FundamentalProvider.get_stock_news(symbol)
            if not news_df.empty:
                result['news'] = news_df.head(5).to_dict('records')
        except Exception as e:
            logger.warning(f"获取新闻失败: {e}")

        # 3. 获取公告
        try:
            ann_df = MarketDataProvider.get_stock_announcements(symbol, limit=5)
            if not ann_df.empty:
                result['announcements'] = ann_df.to_dict('records')
        except Exception as e:
            logger.warning(f"获取公告失败: {e}")

        # 4. LLM 分析 (如果有新闻)
        if self.use_llm and result['news']:
            try:
                # 分析新闻情感
                news_analysis = self.news_analyst.analyze_batch(
                    result['news'],
                    symbol,
                    symbol
                )
                if news_analysis.success:
                    result['analysis']['news_sentiment'] = news_analysis.data
            except Exception as e:
                logger.warning(f"新闻分析失败: {e}")

        return result

    def quick_analysis(self, symbol: str) -> Dict:
        """快速分析 (无需 LLM)

        Args:
            symbol: 股票代码

        Returns:
            分析结果
        """
        return self.analyze_stock(symbol)

    def generate_report(self, symbol: str) -> str:
        """生成分析报告

        Args:
            symbol: 股票代码

        Returns:
            报告文本
        """
        data = self.analyze_stock(symbol)

        report = f"""
# {symbol} 分析报告

## 实时行情
- 当前价格: {data['realtime'].get('price', 'N/A')}
- 涨跌幅: {data['realtime'].get('change_pct', 'N/A')}%
- 成交量: {data['realtime'].get('volume', 'N/A')}

## 新闻动态 ({len(data['news'])} 条)
"""
        for i, news in enumerate(data['news'][:3], 1):
            title = news.get('title', news.get('标题', '无标题'))
            report += f"{i}. {title}\n"

        if data.get('analysis', {}).get('news_sentiment'):
            sentiment = data['analysis']['news_sentiment']
            score = sentiment.get('composite_score', 0)
            sentiment_text = "利好" if score > 0.2 else "利空" if score < -0.2 else "中性"
            report += f"""
## 新闻情感分析
- 综合评分: {score:.2f} ({sentiment_text})
- 覆盖新闻: {sentiment.get('news_count', 0)} 条
"""

        report += f"""
## 公告 ({len(data['announcements'])} 条)
"""
        for i, ann in enumerate(data['announcements'][:3], 1):
            title = ann.get('title', ann.get('公告标题', '无标题'))
            report += f"{i}. {title}\n"

        return report


# 全局服务实例
_analysis_service: Optional[StockAnalysisService] = None


def get_analysis_service(use_llm: bool = False, provider: str = 'openai') -> StockAnalysisService:
    """获取分析服务实例"""
    global _analysis_service
    if _analysis_service is None:
        _analysis_service = StockAnalysisService(use_llm=use_llm, llm_provider=provider)
    return _analysis_service


def quick_stock_analysis(symbol: str) -> Dict:
    """快速股票分析"""
    service = get_analysis_service()
    return service.analyze_stock(symbol)


def generate_stock_report(symbol: str) -> str:
    """生成股票分析报告"""
    service = get_analysis_service()
    return service.generate_report(symbol)
