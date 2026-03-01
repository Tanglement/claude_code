"""多智能体协调器

协调所有智能体完成投资决策流程
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import json
import os

# 导入提示词配置
from config.prompts import *
from src.agents.base import BaseAgent, AgentResponse, LLMClient, PromptTemplate
from src.services.data_provider import (
    MarketDataProvider,
    FundamentalProvider,
    StockQuoteClient,
    TushareProvider
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


# ============================================================
# 数据结构定义
# ============================================================

@dataclass
class AgentResult:
    """单个智能体的结果"""
    agent_name: str
    success: bool
    result: Any
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class WorkflowResult:
    """工作流执行结果"""
    workflow_id: str
    symbol: str
    agent_results: List[AgentResult]
    final_decision: Optional[Dict] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        return {
            'workflow_id': self.workflow_id,
            'symbol': self.symbol,
            'agent_results': [
                {
                    'agent_name': r.agent_name,
                    'success': r.success,
                    'result': r.result,
                    'error': r.error,
                    'timestamp': r.timestamp.isoformat()
                }
                for r in self.agent_results
            ],
            'final_decision': self.final_decision,
            'timestamp': self.timestamp.isoformat()
        }


# ============================================================
# 基础智能体实现
# ============================================================

class MacroAnalyst(BaseAgent):
    """宏观分析师"""
    PROMPT = PROMPT_MACRO_ANALYST

    def run(self, **kwargs) -> AgentResponse:
        market_context = kwargs.get('market_context', '')
        prompt = self.PROMPT.format(market_context=market_context)
        return self._call_llm(prompt)


class FundamentalAnalyst(BaseAgent):
    """基本面分析师"""
    PROMPT = PROMPT_FUNDAMENTAL_ANALYST

    def run(self, **kwargs) -> AgentResponse:
        industry = kwargs.get('industry', '')
        industry_data = kwargs.get('industry_data', '')
        prompt = self.PROMPT.format(industry=industry, industry_data=industry_data)
        return self._call_llm(prompt)


class TechnicalAnalyst(BaseAgent):
    """技术分析师"""
    PROMPT = PROMPT_TECHNICAL_ANALYST

    def run(self, **kwargs) -> AgentResponse:
        symbol = kwargs.get('symbol', '')
        kline_data = kwargs.get('kline_data', '')
        prompt = self.PROMPT.format(symbol=symbol, kline_data=kline_data)
        return self._call_llm(prompt)


class InsiderInfoAnalyst(BaseAgent):
    """权威内部信息分析师"""
    PROMPT = PROMPT_INSIDER_ANALYST

    def run(self, **kwargs) -> AgentResponse:
        symbol = kwargs.get('symbol', '')
        known_info = kwargs.get('known_info', '')
        prompt = self.PROMPT.format(symbol=symbol, known_info=known_info)
        return self._call_llm(prompt)


class ResearchReportAnalyst(BaseAgent):
    """外部研报分析师"""
    PROMPT = PROMPT_RESEARCH_ANALYST

    def run(self, **kwargs) -> AgentResponse:
        symbol = kwargs.get('symbol', '')
        reports = kwargs.get('reports', '')
        prompt = self.PROMPT.format(symbol=symbol, reports=reports)
        return self._call_llm(prompt)


class GeopoliticalAnalyst(BaseAgent):
    """地缘政治分析师"""
    PROMPT = PROMPT_GEOPOLITICAL_ANALYST

    def run(self, **kwargs) -> AgentResponse:
        industry = kwargs.get('industry', '')
        geo_info = kwargs.get('geopolitical_info', '')
        prompt = self.PROMPT.format(industry=industry, geopolitical_info=geo_info)
        return self._call_llm(prompt)


class MarketNewsAnalyst(BaseAgent):
    """市场信息分析师"""
    PROMPT = PROMPT_MARKET_NEWS_ANALYST

    def run(self, **kwargs) -> AgentResponse:
        symbol = kwargs.get('symbol', '')
        news = kwargs.get('news', '')
        prompt = self.PROMPT.format(symbol=symbol, news=news)
        return self._call_llm(prompt)


class BullishAnalyst(BaseAgent):
    """多头机会研究员"""
    PROMPT = PROMPT_BULL_ANALYST

    def run(self, **kwargs) -> AgentResponse:
        data = kwargs.get('data', '')
        prompt = self.PROMPT.format(data=data)
        return self._call_llm(prompt)


class BearishAnalyst(BaseAgent):
    """空头机会研究员"""
    PROMPT = PROMPT_BEAR_ANALYST

    def run(self, **kwargs) -> AgentResponse:
        data = kwargs.get('data', '')
        prompt = self.PROMPT.format(data=data)
        return self._call_llm(prompt)


class ContrarianAnalyst(BaseAgent):
    """核心矛盾研究员"""
    PROMPT = PROMPT_CONTRARIAN_ANALYST

    def run(self, **kwargs) -> AgentResponse:
        views = kwargs.get('views', '')
        prompt = self.PROMPT.format(views=views)
        return self._call_llm(prompt)


class IndustrySecretary(BaseAgent):
    """行业汇总秘书"""
    PROMPT = PROMPT_INDUSTRY_SECRETARY

    def run(self, **kwargs) -> AgentResponse:
        views = kwargs.get('analyst_views', '')
        prompt = self.PROMPT.format(analyst_views=views)
        return self._call_llm(prompt)


# 配置团队
class PortfolioTrader(BaseAgent):
    """组合配置交易员"""
    PROMPT = PROMPT_PORTFOLIO_TRADER

    def run(self, **kwargs) -> AgentResponse:
        industry_view = kwargs.get('industry_view', '')
        current_portfolio = kwargs.get('current_portfolio', '')
        rules = kwargs.get('allocation_rules', '')
        prompt = self.PROMPT.format(
            industry_view=industry_view,
            current_portfolio=current_portfolio,
            allocation_rules=rules
        )
        return self._call_llm(prompt)


class AllocationSecretary(BaseAgent):
    """配置汇总秘书"""
    PROMPT = PROMPT_ALLOCATION_SECRETARY

    def run(self, **kwargs) -> AgentResponse:
        plan = kwargs.get('allocation_plan', '')
        prompt = self.PROMPT.format(allocation_plan=plan)
        return self._call_llm(prompt)


# 风控团队
class RiskScanner(BaseAgent):
    """资产短期风险研究员"""
    PROMPT = PROMPT_RISK_SCANNER

    def run(self, **kwargs) -> AgentResponse:
        assets = kwargs.get('assets', '')
        prompt = self.PROMPT.format(assets=assets)
        return self._call_llm(prompt)


class PortfolioRiskAnalyst(BaseAgent):
    """组合风险研究员"""
    PROMPT = PROMPT_PORTFOLIO_RISK_ANALYST

    def run(self, **kwargs) -> AgentResponse:
        trade = kwargs.get('trade', '')
        holdings = kwargs.get('holdings', '')
        prompt = self.PROMPT.format(trade=trade, holdings=holdings)
        return self._call_llm(prompt)


class RiskSecretary(BaseAgent):
    """风控汇总秘书"""
    PROMPT = PROMPT_RISK_SECRETARY

    def run(self, **kwargs) -> AgentResponse:
        assessment = kwargs.get('risk_assessment', '')
        prompt = self.PROMPT.format(risk_assessment=assessment)
        return self._call_llm(prompt)


# 个股精选团队
class StockScreener(BaseAgent):
    """个股筛选器"""
    PROMPT = PROMPT_STOCK_SCREENER

    def run(self, **kwargs) -> AgentResponse:
        industry = kwargs.get('industry', '')
        criteria = kwargs.get('criteria', '')
        pool = kwargs.get('stock_pool', '')
        prompt = self.PROMPT.format(industry=industry, criteria=criteria, stock_pool=pool)
        return self._call_llm(prompt)


class FinancialDetective(BaseAgent):
    """财务侦探"""
    PROMPT = PROMPT_FINANCIAL_DETECTIVE

    def run(self, **kwargs) -> AgentResponse:
        symbol = kwargs.get('symbol', '')
        data = kwargs.get('financial_data', '')
        prompt = self.PROMPT.format(symbol=symbol, financial_data=data)
        return self._call_llm(prompt)


class ValuationExpert(BaseAgent):
    """个股估值师"""
    PROMPT = PROMPT_VALUATION_EXPERT

    def run(self, **kwargs) -> AgentResponse:
        symbol = kwargs.get('symbol', '')
        data = kwargs.get('financial_data', '')
        price = kwargs.get('current_price', '')
        prompt = self.PROMPT.format(symbol=symbol, financial_data=data, current_price=price)
        return self._call_llm(prompt)


class AlphaResearcher(BaseAgent):
    """Alpha因子研究员"""
    PROMPT = PROMPT_ALPHA_RESEARCHER

    def run(self, **kwargs) -> AgentResponse:
        symbol = kwargs.get('symbol', '')
        info = kwargs.get('company_info', '')
        prompt = self.PROMPT.format(symbol=symbol, company_info=info)
        return self._call_llm(prompt)


class StockRiskAnalyst(BaseAgent):
    """个股风控分析师"""
    PROMPT = PROMPT_STOCK_RISK_ANALYST

    def run(self, **kwargs) -> AgentResponse:
        symbol = kwargs.get('symbol', '')
        info = kwargs.get('company_info', '')
        prompt = self.PROMPT.format(symbol=symbol, company_info=info)
        return self._call_llm(prompt)


# 交易执行
class TradeExecutor(BaseAgent):
    """交易执行员"""
    PROMPT = PROMPT_TRADER

    def run(self, **kwargs) -> AgentResponse:
        instruction = kwargs.get('trade_instruction', '')
        market = kwargs.get('market_data', '')
        prompt = self.PROMPT.format(trade_instruction=instruction, market_data=market)
        return self._call_llm(prompt)


class FinalDecisionMaker(BaseAgent):
    """最终决策者"""
    PROMPT = PROMPT_FINAL_DECISION

    def run(self, **kwargs) -> AgentResponse:
        industry = kwargs.get('industry_analysis', '')
        allocation = kwargs.get('allocation', '')
        risk = kwargs.get('risk', '')
        stocks = kwargs.get('stock_selection', '')
        prompt = self.PROMPT.format(
            industry_analysis=industry,
            allocation=allocation,
            risk=risk,
            stock_selection=stocks
        )
        return self._call_llm(prompt)


# ============================================================
# 多智能体协调器
# ============================================================

class MultiAgentCoordinator:
    """多智能体协调器

    协调17+个智能体完成投资决策
    """

    def __init__(self, llm_client: LLMClient = None):
        """初始化协调器

        Args:
            llm_client: LLM客户端
        """
        self.llm_client = llm_client or LLMClient()

        # 初始化所有智能体
        self._init_agents()

    def _init_agents(self):
        """初始化所有智能体"""
        # 行业分析团队 (11个)
        self.agents = {
            'macro_analyst': MacroAnalyst('宏观分析师', self.llm_client),
            'fundamental_analyst': FundamentalAnalyst('基本面分析师', self.llm_client),
            'technical_analyst': TechnicalAnalyst('技术分析师', self.llm_client),
            'insider_analyst': InsiderInfoAnalyst('内部信息分析师', self.llm_client),
            'research_analyst': ResearchReportAnalyst('研报分析师', self.llm_client),
            'geo_analyst': GeopoliticalAnalyst('地缘政治分析师', self.llm_client),
            'news_analyst': MarketNewsAnalyst('市场信息分析师', self.llm_client),
            'bull_analyst': BullishAnalyst('多头研究员', self.llm_client),
            'bear_analyst': BearishAnalyst('空头研究员', self.llm_client),
            'contrarian_analyst': ContrarianAnalyst('核心矛盾研究员', self.llm_client),
            'industry_secretary': IndustrySecretary('行业秘书', self.llm_client),

            # 配置团队 (2个)
            'portfolio_trader': PortfolioTrader('配置交易员', self.llm_client),
            'allocation_secretary': AllocationSecretary('配置秘书', self.llm_client),

            # 风控团队 (3个)
            'risk_scanner': RiskScanner('风险扫描员', self.llm_client),
            'portfolio_risk_analyst': PortfolioRiskAnalyst('组合风险分析师', self.llm_client),
            'risk_secretary': RiskSecretary('风控秘书', self.llm_client),

            # 个股精选 (5个)
            'stock_screener': StockScreener('个股筛选器', self.llm_client),
            'financial_detective': FinancialDetective('财务侦探', self.llm_client),
            'valuation_expert': ValuationExpert('估值专家', self.llm_client),
            'alpha_researcher': AlphaResearcher('Alpha研究员', self.llm_client),
            'stock_risk_analyst': StockRiskAnalyst('个股风控师', self.llm_client),

            # 交易执行 (1个)
            'trade_executor': TradeExecutor('交易执行员', self.llm_client),

            # 最终决策 (1个)
            'final_decider': FinalDecisionMaker('最终决策者', self.llm_client),
        }

    def _call_llm(self, prompt: str) -> Dict:
        """调用LLM

        Args:
            prompt: 提示词

        Returns:
            LLM响应
        """
        messages = [
            {"role": "system", "content": "你是一位专业的投资分析师。"},
            {"role": "user", "content": prompt}
        ]
        response = self.llm_client.chat(messages, temperature=0.3)
        if response.success:
            return {'success': True, 'data': response.data}
        return {'success': False, 'error': response.error}

    def run_stock_analysis(self, symbol: str) -> WorkflowResult:
        """运行完整的股票分析流程

        Args:
            symbol: 股票代码

        Returns:
            工作流结果
        """
        import uuid
        workflow_id = str(uuid.uuid4())
        results = []

        logger.info(f"开始股票分析流程: {symbol}")

        # Step 1: 收集数据
        stock_data = self._collect_stock_data(symbol)

        # Step 2: 行业分析团队
        industry_result = self._run_industry_team(symbol, stock_data)
        results.extend(industry_result)

        # Step 3: 个股精选团队
        stock_result = self._run_stock_selection(symbol, stock_data)
        results.append(stock_result)

        # Step 4: 风控评估
        risk_result = self._run_risk_assessment(symbol, stock_data)
        results.append(risk_result)

        # Step 5: 最终决策
        final_decision = self._make_final_decision(results)

        return WorkflowResult(
            workflow_id=workflow_id,
            symbol=symbol,
            agent_results=results,
            final_decision=final_decision
        )

    def _collect_stock_data(self, symbol: str) -> Dict:
        """收集股票数据"""
        data = {
            'symbol': symbol,
            'realtime': {},
            'kline': [],
            'news': [],
            'announcements': [],
            'financial': {}
        }

        # 实时行情
        try:
            df = StockQuoteClient.get_quote([symbol])
            if not df.empty:
                data['realtime'] = df.iloc[0].to_dict()
        except Exception as e:
            logger.warning(f"获取行情失败: {e}")

        # K线数据
        try:
            df = MarketDataProvider.get_stock_daily(symbol, start_date='20250101')
            if not df.empty:
                data['kline'] = df.tail(30).to_dict('records')
        except Exception as e:
            logger.warning(f"获取K线失败: {e}")

        # 新闻
        try:
            df = FundamentalProvider.get_stock_news(symbol)
            if not df.empty:
                data['news'] = df.head(10).to_dict('records')
        except Exception as e:
            logger.warning(f"获取新闻失败: {e}")

        # 公告
        try:
            df = MarketDataProvider.get_stock_announcements(symbol, limit=5)
            if not df.empty:
                data['announcements'] = df.to_dict('records')
        except Exception as e:
            logger.warning(f"获取公告失败: {e}")

        return data

    def _run_industry_team(self, symbol: str, data: Dict) -> List[AgentResult]:
        """运行行业分析团队"""
        results = []

        # 准备数据
        news_text = '\n'.join([n.get('title', '') for n in data.get('news', [])])
        kline_text = str(data.get('kline', [])[:5])

        # 多头分析
        bull_data = f"新闻: {news_text}\n行情: {kline_text}"
        resp = self.agents['bull_analyst'].run(data=bull_data)
        results.append(AgentResult(
            agent_name='bull_analyst',
            success=resp.success,
            result=resp.data if resp.success else None,
            error=resp.error
        ))

        # 空头分析
        resp = self.agents['bear_analyst'].run(data=bull_data)
        results.append(AgentResult(
            agent_name='bear_analyst',
            success=resp.success,
            result=resp.data if resp.success else None,
            error=resp.error
        ))

        # 技术分析
        resp = self.agents['technical_analyst'].run(
            symbol=symbol,
            kline_data=kline_text
        )
        results.append(AgentResult(
            agent_name='technical_analyst',
            success=resp.success,
            result=resp.data if resp.success else None,
            error=resp.error
        ))

        return results

    def _run_stock_selection(self, symbol: str, data: Dict) -> AgentResult:
        """运行个股精选团队"""
        # 简化版：直接分析单只股票
        resp = self.agents['valuation_expert'].run(
            symbol=symbol,
            financial_data=str(data.get('financial', {})),
            current_price=str(data.get('realtime', {}).get('close', ''))
        )

        return AgentResult(
            agent_name='stock_selection',
            success=resp.success,
            result=resp.data if resp.success else None,
            error=resp.error
        )

    def _run_risk_assessment(self, symbol: str, data: Dict) -> AgentResult:
        """运行风控评估"""
        resp = self.agents['risk_scanner'].run(
            assets=f"分析股票: {symbol}"
        )

        return AgentResult(
            agent_name='risk_assessment',
            success=resp.success,
            result=resp.data if resp.success else None,
            error=resp.error
        )

    def _make_final_decision(self, results: List[AgentResult]) -> Dict:
        """做出最终决策"""
        # 收集所有分析结果
        analysis_text = '\n'.join([
            f"{r.agent_name}: {r.result[:200] if r.result else r.error}"
            for r in results
        ])

        resp = self.agents['final_decider'].run(
            industry_analysis=analysis_text,
            allocation="待定",
            risk="待评估",
            stocks="待选"
        )

        return {
            'decision': resp.data if resp.success else "分析中",
            'all_analysis': analysis_text
        }

    def run_simple_analysis(self, symbol: str, use_mock: bool = True) -> Dict:
        """简化的股票分析 (无需LLM)

        Args:
            symbol: 股票代码
            use_mock: 是否使用模拟数据

        Returns:
            分析结果
        """
        # 收集数据
        data = self._collect_stock_data(symbol)

        # 如果使用mock
        if use_mock:
            return {
                'symbol': symbol,
                'data': data,
                'analysis': {
                    'technical': '基于K线分析，建议关注支撑位和压力位',
                    'news_sentiment': self._analyze_news_sentiment(data.get('news', [])),
                    'risk_level': '中'
                },
                'decision': '建议观望，等待更多信息'
            }

        # 使用真实LLM
        workflow_result = self.run_stock_analysis(symbol)
        return workflow_result.to_dict()

    def _analyze_news_sentiment(self, news: List[Dict]) -> str:
        """简单的新闻情感分析"""
        if not news:
            return "暂无新闻"

        positive_words = ['上涨', '增长', '盈利', '利好', '突破', '创新']
        negative_words = ['下跌', '亏损', '利空', '风险', '违规', '调查']

        positive_count = 0
        negative_count = 0

        for item in news:
            title = str(item.get('title', ''))
            for word in positive_words:
                if word in title:
                    positive_count += 1
            for word in negative_words:
                if word in title:
                    negative_count += 1

        if positive_count > negative_count:
            return "偏利好"
        elif negative_count > positive_count:
            return "偏利空"
        return "中性"


# 全局协调器
_coordinator: Optional[MultiAgentCoordinator] = None


def get_coordinator() -> MultiAgentCoordinator:
    """获取协调器实例"""
    global _coordinator
    if _coordinator is None:
        _coordinator = MultiAgentCoordinator()
    return _coordinator


def analyze_stock(symbol: str, use_mock: bool = True) -> Dict:
    """快速股票分析

    Args:
        symbol: 股票代码
        use_mock: 是否使用模拟

    Returns:
        分析结果
    """
    coordinator = get_coordinator()
    return coordinator.run_simple_analysis(symbol, use_mock)
