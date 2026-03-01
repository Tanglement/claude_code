# Agents package

from .base import BaseAgent, AgentResponse, LLMClient, PromptTemplate
from .news_analyst import NewsAnalyst
from .report_summarizer import ReportSummarizer
from .multi_agent import (
    MultiAgentCoordinator,
    analyze_stock,
    get_coordinator,
    # 所有智能体类
    MacroAnalyst,
    FundamentalAnalyst,
    TechnicalAnalyst,
    InsiderInfoAnalyst,
    ResearchReportAnalyst,
    GeopoliticalAnalyst,
    MarketNewsAnalyst,
    BullishAnalyst,
    BearishAnalyst,
    ContrarianAnalyst,
    IndustrySecretary,
    PortfolioTrader,
    AllocationSecretary,
    RiskScanner,
    PortfolioRiskAnalyst,
    RiskSecretary,
    StockScreener,
    FinancialDetective,
    ValuationExpert,
    AlphaResearcher,
    StockRiskAnalyst,
    TradeExecutor,
    FinalDecisionMaker
)
