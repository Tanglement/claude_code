"""交易执行模块

交易指令生成和执行：
- 生成交易订单
- 记录交易日志
- 模拟撮合
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from src.agents.base import BaseAgent, AgentResponse
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class TradeOrder:
    """交易订单"""
    order_id: str
    symbol: str
    stock_name: str
    action: str  # buy, sell
    price: float
    quantity: int
    amount: float
    order_type: str  # market, limit
    status: str  # pending, filled, cancelled
    created_at: datetime


@dataclass
class TradeLog:
    """交易日志"""
    log_id: str
    order_id: str
    symbol: str
    action: str
    price: float
    quantity: int
    amount: float
    status: str
    reason: str
    timestamp: datetime


class TradeExecutor(BaseAgent):
    """交易执行 Agent

    功能:
    - 生成交易订单
    - 模拟撮合
    - 记录交易日志
    """

    def __init__(self):
        """初始化交易执行 Agent"""
        super().__init__(name="TradeExecutor")
        self.orders: Dict[str, TradeOrder] = {}
        self.logs: List[TradeLog] = []

    def run(self,
           symbol: str,
           stock_name: str,
           action: str,
           price: float,
           quantity: int,
           order_type: str = 'market') -> AgentResponse:
        """执行交易

        Args:
            symbol: 股票代码
            stock_name: 股票名称
            action: buy/sell
            price: 价格
            quantity: 数量
            order_type: 订单类型

        Returns:
            AgentResponse，包含 TradeOrder
        """
        try:
            # 生成订单 ID
            order_id = self._generate_order_id()

            # 创建订单
            order = TradeOrder(
                order_id=order_id,
                symbol=symbol,
                stock_name=stock_name,
                action=action,
                price=price,
                quantity=quantity,
                amount=price * quantity,
                order_type=order_type,
                status='pending',
                created_at=datetime.now()
            )

            # 模拟撮合 (这里只是简化版，实际应该对接券商API)
            filled_order = self._simulate_fill(order)

            # 记录日志
            self._log_trade(filled_order, "成交")

            return AgentResponse(
                success=True,
                data=filled_order
            )

        except Exception as e:
            logger.error(f"Trade execution error: {e}")
            return AgentResponse(
                success=False,
                data=None,
                error=str(e)
            )

    def run_with_decision(self,
                          symbol: str,
                          stock_name: str,
                          price: float,
                          decision: Dict,
                          risk_result: Dict) -> AgentResponse:
        """基于决策和风控结果执行交易

        Args:
            symbol: 股票代码
            stock_name: 股票名称
            price: 当前价格
            decision: 决策结果
            risk_result: 风控结果

        Returns:
            AgentResponse
        """
        # 检查风控是否通过
        if not risk_result.get('approved', False):
            reason = "; ".join(risk_result.get('reasons', []))
            return AgentResponse(
                success=False,
                data=None,
                error=f"Risk control rejected: {reason}"
            )

        # 获取调整后的仓位
        position = risk_result.get('adjusted_position', 0)

        if position == 0:
            return AgentResponse(
                success=False,
                data=None,
                error="Position is 0 after risk control"
            )

        # 计算买入数量 (假设账户100万)
        account_value = 1000000  # 100万
        amount = account_value * position / 100
        quantity = int(amount / price / 100) * 100  # 整手

        if quantity < 100:
            return AgentResponse(
                success=False,
                data=None,
                error="Quantity too small"
            )

        # 决定买卖方向
        action = 'buy'
        if decision.get('decision') in ['卖出', '强烈卖出']:
            action = 'sell'

        # 执行交易
        return self.run(
            symbol=symbol,
            stock_name=stock_name,
            action=action,
            price=price,
            quantity=quantity
        )

    def _generate_order_id(self) -> str:
        """生成订单 ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        import random
        return f"ORD{timestamp}{random.randint(1000, 9999)}"

    def _simulate_fill(self, order: TradeOrder) -> TradeOrder:
        """模拟订单成交 (简化版)

        Args:
            order: 订单

        Returns:
            成交后的订单
        """
        # 模拟滑点
        slippage = 0.001  # 0.1%
        if order.action == 'buy':
            filled_price = order.price * (1 + slippage)
        else:
            filled_price = order.price * (1 - slippage)

        order.price = filled_price
        order.amount = filled_price * order.quantity
        order.status = 'filled'

        return order

    def _log_trade(self, order: TradeOrder, reason: str):
        """记录交易日志

        Args:
            order: 订单
            reason: 成交原因/备注
        """
        log = TradeLog(
            log_id=self._generate_log_id(),
            order_id=order.order_id,
            symbol=order.symbol,
            action=order.action,
            price=order.price,
            quantity=order.quantity,
            amount=order.amount,
            status=order.status,
            reason=reason,
            timestamp=datetime.now()
        )
        self.logs.append(log)
        logger.info(f"Trade logged: {log}")

    def _generate_log_id(self) -> str:
        """生成日志 ID"""
        return f"LOG{datetime.now().strftime('%Y%m%d%H%M%S')}{len(self.logs)}"

    def get_order(self, order_id: str) -> Optional[TradeOrder]:
        """获取订单"""
        return self.orders.get(order_id)

    def get_orders(self, status: str = None) -> List[TradeOrder]:
        """获取订单列表"""
        if status:
            return [o for o in self.orders.values() if o.status == status]
        return list(self.orders.values())

    def get_trade_logs(self, limit: int = 100) -> List[TradeLog]:
        """获取交易日志"""
        return self.logs[-limit:]


class MockTradeExecutor:
    """模拟交易执行器 (用于回测)"""

    def __init__(self, initial_capital: float = 1000000):
        """初始化

        Args:
            initial_capital: 初始资金
        """
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions: Dict[str, Dict] = {}  # symbol -> {quantity, avg_cost}
        self.trade_history: List[Dict] = []

    def buy(self, symbol: str, price: float, quantity: int) -> bool:
        """买入

        Args:
            symbol: 股票代码
            price: 价格
            quantity: 数量

        Returns:
            是否成功
        """
        cost = price * quantity * 1.0003  # 考虑手续费

        if cost > self.cash:
            logger.warning(f"Insufficient cash: {self.cash} < {cost}")
            return False

        self.cash -= cost

        if symbol in self.positions:
            # 追加买入
            old_qty = self.positions[symbol]['quantity']
            old_cost = self.positions[symbol]['avg_cost']
            new_qty = old_qty + quantity
            new_cost = (old_cost * old_qty + price * quantity) / new_qty
            self.positions[symbol] = {
                'quantity': new_qty,
                'avg_cost': new_cost
            }
        else:
            self.positions[symbol] = {
                'quantity': quantity,
                'avg_cost': price
            }

        self._record_trade(symbol, 'buy', price, quantity, cost)
        return True

    def sell(self, symbol: str, price: float, quantity: int) -> bool:
        """卖出

        Args:
            symbol: 股票代码
            price: 价格
            quantity: 数量

        Returns:
            是否成功
        """
        if symbol not in self.positions:
            logger.warning(f"No position for {symbol}")
            return False

        if self.positions[symbol]['quantity'] < quantity:
            logger.warning(f"Insufficient shares")
            return False

        revenue = price * quantity * 0.9997  # 考虑手续费
        self.cash += revenue

        self.positions[symbol]['quantity'] -= quantity
        if self.positions[symbol]['quantity'] == 0:
            del self.positions[symbol]

        self._record_trade(symbol, 'sell', price, quantity, revenue)
        return True

    def get_portfolio_value(self, prices: Dict[str, float]) -> float:
        """获取组合市值

        Args:
            prices: 当前价格字典

        Returns:
            总市值
        """
        position_value = 0
        for symbol, pos in self.positions.items():
            if symbol in prices:
                position_value += pos['quantity'] * prices[symbol]

        return self.cash + position_value

    def get_returns(self, prices: Dict[str, float]) -> float:
        """获取收益率

        Args:
            prices: 当前价格字典

        Returns:
            收益率 (%)
        """
        current_value = self.get_portfolio_value(prices)
        return (current_value - self.initial_capital) / self.initial_capital * 100

    def _record_trade(self, symbol: str, action: str, price: float,
                     quantity: int, amount: float):
        """记录交易"""
        self.trade_history.append({
            'timestamp': datetime.now(),
            'symbol': symbol,
            'action': action,
            'price': price,
            'quantity': quantity,
            'amount': amount
        })


# 便捷函数
def execute_trade(symbol: str,
                 stock_name: str,
                 action: str,
                 price: float,
                 quantity: int) -> AgentResponse:
    """快速执行交易

    Args:
        symbol: 股票代码
        stock_name: 股票名称
        action: buy/sell
        price: 价格
        quantity: 数量

    Returns:
        交易结果
    """
    executor = TradeExecutor()
    return executor.run(symbol, stock_name, action, price, quantity)
