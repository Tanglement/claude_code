"""新闻分析智能体

基于 LLM 的新闻情感分析 Agent
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import json

from .base import BaseAgent, AgentResponse, LLMClient, PromptTemplate
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class NewsAnalysisResult:
    """新闻分析结果"""
    sentiment: str  # bullish, bearish, neutral
    impact_score: int  # 1-10
    time_horizon: str  # short, medium, long
    confidence: float  # 0-10
    reason: str


class NewsAnalyst(BaseAgent):
    """新闻分析 Agent

    功能:
    - 分析单条新闻对股票的影响
    - 批量分析多条新闻
    - 生成综合情感评分
    """

    def __init__(self, llm_client: Optional[LLMClient] = None):
        """初始化新闻分析 Agent"""
        super().__init__(name="NewsAnalyst", llm_client=llm_client)

    def analyze_single_news(self,
                          news: Dict,
                          symbol: str,
                          name: str) -> AgentResponse:
        """分析单条新闻

        Args:
            news: 新闻数据字典
            symbol: 股票代码
            name: 股票名称

        Returns:
            AgentResponse，包含 NewsAnalysisResult
        """
        # 验证输入
        error = self.validate_input(
            ['title', 'source'],
            news
        )
        if error:
            return AgentResponse(success=False, data=None, error=error)

        # 构建提示词
        prompt = PromptTemplate.render(
            PromptTemplate.NEWS_ANALYST_PROMPT,
            symbol=symbol,
            name=name,
            title=news.get('title', ''),
            source=news.get('source', ''),
            publish_time=news.get('publish_time', ''),
            content=news.get('content', '')[:2000]  # 限制内容长度
        )

        # 调用 LLM
        messages = [
            {"role": "system", "content": "你是一位专业的股票分析师，擅长分析新闻对股价的影响。"},
            {"role": "user", "content": prompt}
        ]

        response = self.llm_client.chat(
            messages=messages,
            temperature=0.3,  # 低温度，更确定性
            max_tokens=500
        )

        if not response.success:
            return response

        # 解析结果
        try:
            result = self._parse_llm_response(response.data)
            return AgentResponse(
                success=True,
                data=result
            )
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            return AgentResponse(
                success=False,
                data=None,
                error=f"Failed to parse response: {e}"
            )

    def analyze_batch(self,
                     news_list: List[Dict],
                     symbol: str,
                     name: str) -> AgentResponse:
        """批量分析新闻

        Args:
            news_list: 新闻列表
            symbol: 股票代码
            name: 股票名称

        Returns:
            AgentResponse，包含分析结果列表
        """
        if not news_list:
            return AgentResponse(
                success=True,
                data=[],
                error="No news to analyze"
            )

        results = []
        for news in news_list:
            result = self.analyze_single_news(news, symbol, name)
            if result.success:
                results.append(result.data)

        # 计算综合评分
        composite_score = self._calculate_composite_score(results)

        return AgentResponse(
            success=True,
            data={
                'individual_results': results,
                'composite_score': composite_score,
                'news_count': len(results)
            }
        )

    def run(self, news: Dict, symbol: str, name: str, batch: bool = False, **kwargs) -> AgentResponse:
        """执行新闻分析任务

        Args:
            news: 单条新闻或新闻列表
            symbol: 股票代码
            name: 股票名称
            batch: 是否批量分析
            **kwargs: 其他参数

        Returns:
            AgentResponse
        """
        if batch or isinstance(news, list):
            return self.analyze_batch(news if isinstance(news, list) else [news], symbol, name)
        else:
            return self.analyze_single_news(news, symbol, name)

    def _parse_llm_response(self, response: str) -> NewsAnalysisResult:
        """解析 LLM 返回的 JSON

        Args:
            response: LLM 返回的文本

        Returns:
            NewsAnalysisResult 对象
        """
        # 尝试提取 JSON 部分
        json_str = self._extract_json(response)

        data = json.loads(json_str)

        return NewsAnalysisResult(
            sentiment=data.get('sentiment', 'neutral'),
            impact_score=int(data.get('impact_score', 5)),
            time_horizon=data.get('time_horizon', 'short'),
            confidence=float(data.get('confidence', 5)),
            reason=data.get('reason', '')
        )

    def _extract_json(self, text: str) -> str:
        """从文本中提取 JSON 部分

        Args:
            text: 包含 JSON 的文本

        Returns:
            JSON 字符串
        """
        # 尝试找到 JSON 块
        start = text.find('{')
        end = text.rfind('}')

        if start != -1 and end != -1 and end > start:
            return text[start:end+1]

        # 如果没有找到，返回原始文本（可能会导致解析错误）
        return text

    def _calculate_composite_score(self, results: List[NewsAnalysisResult]) -> float:
        """计算综合情感评分

        Args:
            results: 分析结果列表

        Returns:
            综合评分 (-1 到 1)
        """
        if not results:
            return 0.0

        total_weight = 0
        weighted_score = 0

        sentiment_map = {
            'bullish': 1,
            'bearish': -1,
            'neutral': 0
        }

        for result in results:
            sentiment = sentiment_map.get(result.sentiment, 0)
            weight = result.confidence * result.impact_score

            weighted_score += sentiment * weight
            total_weight += weight

        if total_weight > 0:
            return weighted_score / total_weight
        return 0.0


# 便捷函数
def quick_analyze_news(news: Dict, symbol: str, name: str,
                      use_mock: bool = False) -> AgentResponse:
    """快速分析新闻

    Args:
        news: 新闻数据
        symbol: 股票代码
        name: 股票名称
        use_mock: 是否使用模拟客户端

    Returns:
        分析结果
    """
    if use_mock:
        from .base import MockLLMClient
        client = MockLLMClient('{"sentiment": "bullish", "impact_score": 7, "time_horizon": "short", "confidence": 8, "reason": "测试"}')
    else:
        client = None

    agent = NewsAnalyst(client)
    return agent.run(news, symbol, name)
