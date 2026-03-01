"""研报摘要智能体

基于 LLM 的研报分析摘要 Agent
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import json

from .base import BaseAgent, AgentResponse, LLMClient, PromptTemplate
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ReportSummaryResult:
    """研报摘要结果"""
    core_view: str  # 核心观点
    main_logic: str  # 主要逻辑
    recommendation: str  # 投资建议
    target_price: Optional[float]  # 目标价位
    risk_warning: str  # 风险提示


class ReportSummarizer(BaseAgent):
    """研报摘要 Agent

    功能:
    - 分析单篇研报
    - 提取核心观点
    - 生成投资建议
    """

    def __init__(self, llm_client: Optional[LLMClient] = None):
        """初始化研报摘要 Agent"""
        super().__init__(name="ReportSummarizer", llm_client=llm_client)

    def summarize_report(self,
                       report: Dict,
                       company: str) -> AgentResponse:
        """摘要单篇研报

        Args:
            report: 研报数据字典
            company: 公司名称

        Returns:
            AgentResponse，包含 ReportSummaryResult
        """
        # 验证输入
        error = self.validate_input(
            ['title', 'content'],
            report
        )
        if error:
            return AgentResponse(success=False, data=None, error=error)

        # 构建提示词
        prompt = PromptTemplate.render(
            PromptTemplate.REPORT_SUMMARIZER_PROMPT,
            title=report.get('title', ''),
            company=company,
            publish_time=report.get('publish_time', ''),
            content=report.get('content', '')[:5000]  # 限制内容长度
        )

        # 调用 LLM
        messages = [
            {"role": "system", "content": "你是一位专业的金融研究员，擅长解读投资研究报告。"},
            {"role": "user", "content": prompt}
        ]

        response = self.llm_client.chat(
            messages=messages,
            temperature=0.3,
            max_tokens=1000
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

    def summarize_reports(self,
                         reports: List[Dict],
                         company: str) -> AgentResponse:
        """批量摘要研报

        Args:
            reports: 研报列表
            company: 公司名称

        Returns:
            AgentResponse，包含摘要结果列表
        """
        if not reports:
            return AgentResponse(
                success=True,
                data=[],
                error="No reports to summarize"
            )

        results = []
        for report in reports:
            result = self.summarize_report(report, company)
            if result.success:
                results.append(result.data)

        # 综合分析
        overall = self._generate_overall_analysis(results)

        return AgentResponse(
            success=True,
            data={
                'individual_summaries': results,
                'overall_analysis': overall,
                'report_count': len(results)
            }
        )

    def run(self, report: Dict, company: str, batch: bool = False, **kwargs) -> AgentResponse:
        """执行研报摘要任务

        Args:
            report: 研报数据
            company: 公司名称
            batch: 是否批量处理
            **kwargs: 其他参数

        Returns:
            AgentResponse
        """
        if batch or isinstance(report, list):
            return self.summarize_reports(
                report if isinstance(report, list) else [report],
                company
            )
        else:
            return self.summarize_report(report, company)

    def _parse_llm_response(self, response: str) -> ReportSummaryResult:
        """解析 LLM 返回的 JSON

        Args:
            response: LLM 返回的文本

        Returns:
            ReportSummaryResult 对象
        """
        json_str = self._extract_json(response)
        data = json.loads(json_str)

        # 处理 target_price
        target_price = data.get('target_price')
        if target_price is not None:
            try:
                target_price = float(target_price)
            except (ValueError, TypeError):
                target_price = None

        return ReportSummaryResult(
            core_view=data.get('core_view', ''),
            main_logic=data.get('main_logic', ''),
            recommendation=data.get('recommendation', '持有'),
            target_price=target_price,
            risk_warning=data.get('risk_warning', '')
        )

    def _extract_json(self, text: str) -> str:
        """从文本中提取 JSON"""
        start = text.find('{')
        end = text.rfind('}')

        if start != -1 and end != -1 and end > start:
            return text[start:end+1]
        return text

    def _generate_overall_analysis(self,
                                   results: List[ReportSummaryResult]) -> Dict:
        """生成综合分析

        Args:
            results: 研报摘要列表

        Returns:
            综合分析字典
        """
        if not results:
            return {}

        # 统计投资建议
        recommendation_count = {}
        target_prices = []

        for result in results:
            rec = result.recommendation
            recommendation_count[rec] = recommendation_count.get(rec, 0) + 1

            if result.target_price:
                target_prices.append(result.target_price)

        # 多数意见
        overall_recommendation = max(recommendation_count, key=recommendation_count.get)

        # 目标价范围
        target_price_range = None
        if target_prices:
            target_price_range = {
                'min': min(target_prices),
                'max': max(target_prices),
                'avg': sum(target_prices) / len(target_prices)
            }

        return {
            'overall_recommendation': overall_recommendation,
            'recommendation_distribution': recommendation_count,
            'target_price_range': target_price_range,
            'report_count': len(results)
        }


# 便捷函数
def quick_summarize_report(report: Dict, company: str,
                         use_mock: bool = False) -> AgentResponse:
    """快速摘要研报

    Args:
        report: 研报数据
        company: 公司名称
        use_mock: 是否使用模拟客户端

    Returns:
        摘要结果
    """
    if use_mock:
        from .base import MockLLMClient
        client = MockLLMClient('{"core_view": "测试核心观点", "main_logic": "测试主要逻辑", "recommendation": "买入", "target_price": 100.0, "risk_warning": "测试风险提示"}')
    else:
        client = None

    agent = ReportSummarizer(client)
    return agent.run(report, company)
