"""智能体基类模块

提供所有 Agent 的基类和通用功能：
- BaseAgent: 智能体基类
- LLMClient: LLM 客户端封装
- PromptTemplate: 提示词模板
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import os
import json

from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class AgentResponse:
    """Agent 响应数据结构"""
    success: bool
    data: Any
    error: Optional[str] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'success': self.success,
            'data': self.data,
            'error': self.error,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class LLMClient:
    """LLM 客户端封装

    支持多种 LLM 提供商: OpenAI, Claude, DeepSeek 等
    """

    def __init__(self, provider: str = 'openai', api_key: Optional[str] = None):
        """初始化 LLM 客户端

        Args:
            provider: LLM 提供商 (openai, claude, deepseek)
            api_key: API Key (可以从环境变量读取)
        """
        self.provider = provider
        self.api_key = api_key or self._get_api_key()
        self.client = None

    def _get_api_key(self) -> str:
        """从环境变量获取 API Key"""
        env_map = {
            'openai': 'OPENAI_API_KEY',
            'claude': 'CLAUDE_API_KEY',
            'deepseek': 'DEEPSEEK_API_KEY'
        }
        return os.getenv(env_map.get(self.provider, 'OPENAI_API_KEY'), '')

    def chat(self, messages: List[Dict[str, str]],
             model: str = 'gpt-3.5-turbo',
             temperature: float = 0.7,
             max_tokens: int = 2000) -> AgentResponse:
        """发送聊天请求

        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大 token 数

        Returns:
            AgentResponse 对象
        """
        try:
            if not self.api_key:
                return AgentResponse(
                    success=False,
                    data=None,
                    error=f"No API key found for {self.provider}"
                )

            # 根据不同提供商调用不同的 API
            if self.provider == 'openai':
                return self._chat_openai(messages, model, temperature, max_tokens)
            elif self.provider == 'claude':
                return self._chat_claude(messages, model, temperature, max_tokens)
            elif self.provider == 'deepseek':
                return self._chat_deepseek(messages, model, temperature, max_tokens)
            else:
                return AgentResponse(
                    success=False,
                    data=None,
                    error=f"Unsupported provider: {self.provider}"
                )

        except Exception as e:
            logger.error(f"LLM chat error: {e}")
            return AgentResponse(success=False, data=None, error=str(e))

    def _chat_openai(self, messages: List[Dict], model: str,
                    temperature: float, max_tokens: int) -> AgentResponse:
        """OpenAI API 调用"""
        try:
            from openai import OpenAI

            if self.client is None:
                self.client = OpenAI(api_key=self.api_key)

            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            return AgentResponse(
                success=True,
                data=response.choices[0].message.content
            )
        except ImportError:
            return AgentResponse(
                success=False,
                data=None,
                error="openai library not installed"
            )
        except Exception as e:
            return AgentResponse(success=False, data=None, error=str(e))

    def _chat_claude(self, messages: List[Dict], model: str,
                    temperature: float, max_tokens: int) -> AgentResponse:
        """Claude API 调用 (简化版)"""
        # TODO: 实现 Claude API 调用
        return AgentResponse(
            success=False,
            data=None,
            error="Claude API not implemented yet"
        )

    def _chat_deepseek(self, messages: List[Dict], model: str,
                      temperature: float, max_tokens: int) -> AgentResponse:
        """DeepSeek API 调用 (简化版)"""
        # TODO: 实现 DeepSeek API 调用
        return AgentResponse(
            success=False,
            data=None,
            error="DeepSeek API not implemented yet"
        )


class PromptTemplate:
    """提示词模板管理"""

    @staticmethod
    def render(template: str, **kwargs) -> str:
        """渲染提示词模板

        Args:
            template: 模板字符串
            **kwargs: 模板变量

        Returns:
            渲染后的字符串
        """
        try:
            return template.format(**kwargs)
        except KeyError as e:
            logger.error(f"Missing template variable: {e}")
            return template

    # 常用模板
    NEWS_ANALYST_PROMPT = """你是一位资深股票分析师。请分析以下新闻对股票 {symbol} ({name}) 的影响。

新闻标题: {title}
新闻来源: {source}
发布时间: {publish_time}
新闻内容: {content}

请从以下角度进行分析:
1. 新闻性质: 利好 / 利空 / 中性
2. 影响程度: 轻微(1-3) / 中等(4-6) / 重大(7-10)
3. 时间效应: 短期 / 中期 / 长期
4. 置信度: 0-10

请以 JSON 格式输出:
{{
    "sentiment": "bullish/bearish/neutral",
    "impact_score": 1-10,
    "time_horizon": "short/medium/long",
    "confidence": 0-10,
    "reason": "分析理由"
}}"""

    REPORT_SUMMARIZER_PROMPT = """你是一位专业的研究员。请精简以下研报内容。

研报标题: {title}
公司名称: {company}
发布时间: {publish_time}

研报内容:
{content}

请提取以下信息:
1. 核心观点 (不超过 50 字)
2. 主要逻辑 (不超过 100 字)
3. 投资建议: 买入/增持/持有/减持/卖出
4. 目标价位 (如有)
5. 风险提示

请以 JSON 格式输出:
{{
    "core_view": "核心观点",
    "main_logic": "主要逻辑",
    "recommendation": "买入/增持/持有/减持/卖出",
    "target_price": null 或数字,
    "risk_warning": "风险提示"
}}"""

    DECISION_MAKER_PROMPT = """你是量化投资决策系统。请综合以下信息做出投资决策。

股票: {symbol}
当前价格: {price}

技术指标:
- RSI: {rsi}
- MACD: {macd}
- KDJ: {kdj}
- 均线: {ma_status}

资金流向:
- 主力净流入: {main_flow}
- 资金流向趋势: {flow_trend}

新闻舆情:
- 新闻情感评分: {sentiment}
- 近期新闻数: {news_count}

综合评分: {composite_score}

请给出投资建议:
1. 决策: 强烈买入 / 买入 / 观望 / 卖出 / 强烈卖出
2. 仓位建议: 0-100%
3. 理由: 简要说明

请以 JSON 格式输出:
{{
    "decision": "强烈买入/买入/观望/卖出/强烈卖出",
    "position": 0-100,
    "reason": "理由"
}}"""


class BaseAgent(ABC):
    """智能体基类

    所有 Agent 都应继承此类
    """

    def __init__(self, name: str, llm_client: Optional[LLMClient] = None):
        """初始化 Agent

        Args:
            name: Agent 名称
            llm_client: LLM 客户端实例
        """
        self.name = name
        self.llm_client = llm_client or LLMClient()
        self.logger = get_logger(f"agent.{name}")

    @abstractmethod
    def run(self, **kwargs) -> AgentResponse:
        """执行 Agent 任务

        Args:
            **kwargs: 输入参数

        Returns:
            AgentResponse 对象
        """
        pass

    def _log(self, message: str, level: str = 'info'):
        """日志记录"""
        getattr(self.logger, level)(f"[{self.name}] {message}")

    def validate_input(self, required_fields: List[str], data: Dict) -> Optional[str]:
        """验证输入数据

        Args:
            required_fields: 必需字段列表
            data: 输入数据

        Returns:
            错误信息，如果验证通过返回 None
        """
        missing = [field for field in required_fields if field not in data]
        if missing:
            return f"Missing required fields: {missing}"
        return None


class MockLLMClient:
    """模拟 LLM 客户端 (用于测试)"""

    def __init__(self, response: str = "Mock response"):
        self.response = response

    def chat(self, messages: List[Dict], **kwargs) -> AgentResponse:
        return AgentResponse(success=True, data=self.response)
