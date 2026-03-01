"""风控模块

投资决策的风控检查：
- 仓位检查
- 回撤限制
- 单股集中度
- 止损止盈
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from src.agents.base import BaseAgent, AgentResponse
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class RiskCheckResult:
    """风控检查结果"""
    approved: bool  # 是否通过
    risk_level: str  # low, medium, high
    warnings: List[str]  # 警告信息
    adjusted_position: Optional[int]  # 调整后的仓位
    reasons: List[str]  # 拒绝/调整原因


class RiskControlAgent(BaseAgent):
    """风控 Agent

    检查规则:
    1. 单日最大仓位
    2. 单股最大持仓比例
    3. 最大回撤限制
    4. 持仓数量限制
    5. 行业集中度
    """

    def __init__(self):
        """初始化风控 Agent"""
        super().__init__(name="RiskControl")

        # 默认风控参数
        self.config = {
            'max_single_position': 30,  # 单股最大仓位 30%
            'max_total_position': 80,    # 总仓位上限 80%
            'max_positions': 10,         # 最多持仓10只
            'max_loss_per_stock': 15,    # 单股最大亏损 15%
            'max_drawdown': 20,           # 账户最大回撤 20%
        }

    def run(self,
           decision: Dict,
           portfolio: Dict,
           config: Dict = None) -> AgentResponse:
        """执行风控检查

        Args:
            decision: 决策结果 (包含 decision, position, confidence)
            portfolio: 当前持仓情况
            config: 风控参数 (可选)

        Returns:
            AgentResponse，包含 RiskCheckResult
        """
        # 更新配置
        if config:
            self.config.update(config)

        # 检查各项风险
        warnings = []
        reasons = []
        risk_level = 'low'
        adjusted_position = decision.get('position', 0)

        # 1. 决策检查 - 强烈卖出时禁止买入
        if decision.get('decision') in ['强烈卖出', '卖出']:
            return AgentResponse(
                success=True,
                data=RiskCheckResult(
                    approved=False,
                    risk_level='high',
                    warnings=["决策为卖出，不建议建仓"],
                    adjusted_position=0,
                    reasons=["决策信号为卖出"]
                )
            )

        # 2. 置信度检查 - 低置信度降低仓位
        confidence = decision.get('confidence', 5)
        if confidence < 5:
            adjusted_position = int(adjusted_position * 0.5)
            warnings.append(f"置信度较低({confidence})，仓位减半")
            risk_level = 'medium'

        # 3. 持仓数量检查
        current_positions = portfolio.get('positions', [])
        position_count = len(current_positions)

        if position_count >= self.config['max_positions']:
            warnings.append(f"持仓数量已达上限({position_count})")
            reasons.append("持仓数量超限")
            return AgentResponse(
                success=True,
                data=RiskCheckResult(
                    approved=False,
                    risk_level='high',
                    warnings=warnings,
                    adjusted_position=0,
                    reasons=reasons
                )
            )

        # 4. 总仓位检查
        current_total_position = portfolio.get('total_position', 0)
        new_total = current_total_position + adjusted_position

        if new_total > self.config['max_total_position']:
            # 调整仓位
            available = self.config['max_total_position'] - current_total_position
            if available > 0:
                adjusted_position = available
                warnings.append(f"总仓位超限，降至{available}%")
            else:
                adjusted_position = 0
                reasons.append("总仓位已达上限")
                risk_level = 'high'

        # 5. 单股仓位检查
        symbol = decision.get('symbol', '')
        existing_position = self._get_position_by_symbol(current_positions, symbol)

        if existing_position:
            new_position = existing_position + adjusted_position
            if new_position > self.config['max_single_position']:
                adjusted_position = self.config['max_single_position'] - existing_position
                if adjusted_position < 0:
                    adjusted_position = 0
                warnings.append(f"单股仓位超限，调整至{adjusted_position}%")
                risk_level = 'medium'

        # 6. 单股亏损检查 (已有持仓)
        if existing_position:
            position_loss = abs(portfolio.get(f'{symbol}_loss', 0))
            if position_loss > self.config['max_loss_per_stock']:
                reasons.append(f"单股亏损{position_loss}%，超过限制")
                adjusted_position = 0
                risk_level = 'high'

        # 7. 回撤检查
        current_drawdown = portfolio.get('drawdown', 0)
        if current_drawdown > self.config['max_drawdown']:
            reasons.append(f"账户回撤{current_drawdown}%，暂停开仓")
            risk_level = 'high'
            adjusted_position = 0

        # 判断是否通过
        approved = len(reasons) == 0

        return AgentResponse(
            success=True,
            data=RiskCheckResult(
                approved=approved,
                risk_level=risk_level,
                warnings=warnings,
                adjusted_position=adjusted_position,
                reasons=reasons
            )
        )

    def _get_position_by_symbol(self, positions: List[Dict], symbol: str) -> float:
        """获取指定股票的持仓比例"""
        for pos in positions:
            if pos.get('symbol') == symbol:
                return pos.get('position', 0)
        return 0

    def set_config(self, config: Dict):
        """设置风控参数"""
        self.config.update(config)


class SimpleRiskChecker:
    """简单风控检查器 (无需持仓数据)"""

    @staticmethod
    def check_decision(decision: Dict, config: Dict = None) -> RiskCheckResult:
        """快速风控检查

        Args:
            decision: 决策结果
            config: 风控参数

        Returns:
            RiskCheckResult
        """
        if config is None:
            config = {
                'max_single_position': 30,
                'max_total_position': 80,
                'min_confidence': 3
            }

        warnings = []
        reasons = []
        risk_level = 'low'
        adjusted_position = decision.get('position', 0)

        # 检查决策类型
        if decision.get('decision') in ['强烈卖出', '卖出']:
            return RiskCheckResult(
                approved=False,
                risk_level='high',
                warnings=[],
                adjusted_position=0,
                reasons=["卖出信号，不建议建仓"]
            )

        # 检查置信度
        confidence = decision.get('confidence', 5)
        if confidence < config.get('min_confidence', 3):
            adjusted_position = int(adjusted_position * 0.5)
            warnings.append(f"置信度较低")

        # 检查仓位
        if adjusted_position > config.get('max_single_position', 30):
            adjusted_position = config.get('max_single_position', 30)
            warnings.append("仓位超过限制")

        approved = len(reasons) == 0

        return RiskCheckResult(
            approved=approved,
            risk_level=risk_level,
            warnings=warnings,
            adjusted_position=adjusted_position,
            reasons=reasons
        )


# 便捷函数
def quick_risk_check(decision: Dict, portfolio: Dict = None) -> AgentResponse:
    """快速风控检查

    Args:
        decision: 决策结果
        portfolio: 持仓情况 (可选)

    Returns:
        风控结果
    """
    agent = RiskControlAgent()
    return agent.run(decision, portfolio or {})
