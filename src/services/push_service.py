"""Push Notification Service

定时推送服务：
1. 收集用户自选股数据
2. 检查价格预警
3. 检查新闻/公告
4. 生成推送报告
"""

from typing import List, Dict, Optional
from datetime import datetime, date
import pandas as pd

from src.services.data_provider import (
    StockQuoteClient,
    MarketDataProvider,
    FundamentalProvider,
    TushareProvider
)
from src.repositories.user_repo import UserRepository
from src.models.user import UserWatchlist, UserPreference
from src.utils.logger import get_logger

logger = get_logger(__name__)


class PushService:
    """Push notification service for user watchlist."""

    def __init__(self):
        """Initialize push service."""
        self.user_repo = UserRepository()

    def get_all_users_with_push_enabled(self) -> List[Dict]:
        """Get all users with push enabled.

        Returns:
            List of user dictionaries with preferences
        """
        # In a real system, you'd query users with push_enabled=True
        # For now, return empty list - this would be called by scheduler
        return []

    def collect_watchlist_data(self, user_id: int) -> Dict:
        """Collect data for user's watchlist stocks.

        Args:
            user_id: User ID

        Returns:
            Dictionary with watchlist data and current prices
        """
        watchlist = self.user_repo.get_watchlist(user_id)
        if not watchlist:
            return {
                'stocks': [],
                'summary': 'No stocks in watchlist'
            }

        # Get stock symbols
        symbols = [w.symbol for w in watchlist]

        # Get current prices
        quotes_df = StockQuoteClient.get_quote(symbols)

        # Build result
        stocks_data = []
        for item in watchlist:
            stock_info = {
                'symbol': item.symbol,
                'stock_name': item.stock_name,
                'notes': item.notes,
                'alert_price': item.alert_price,
                'alert_pct': item.alert_pct,
                'current_price': None,
                'change_pct': None,
                'alert_triggered': False,
                'alert_reason': None
            }

            # Find quote
            if not quotes_df.empty:
                quote = quotes_df[quotes_df['symbol'] == item.symbol]
                if not quote.empty:
                    q = quote.iloc[0]
                    stock_info['current_price'] = q.get('close') or q.get('price')
                    stock_info['change_pct'] = q.get('change_pct')

                    # Check alerts
                    if item.alert_price and stock_info['current_price']:
                        if abs(stock_info['current_price'] - item.alert_price) < 0.01:
                            stock_info['alert_triggered'] = True
                            stock_info['alert_reason'] = f"Price reached {stock_info['current_price']}"

                    if item.alert_pct and stock_info['change_pct']:
                        if abs(stock_info['change_pct']) >= item.alert_pct:
                            stock_info['alert_triggered'] = True
                            stock_info['alert_reason'] = f"Change {stock_info['change_pct']}%"

            stocks_data.append(stock_info)

        return {
            'stocks': stocks_data,
            'count': len(stocks_data),
            'timestamp': datetime.now().isoformat()
        }

    def check_news_for_symbols(self, symbols: List[str], limit: int = 3) -> Dict:
        """Check latest news for given symbols.

        Args:
            symbols: List of stock symbols
            limit: Number of news per stock

        Returns:
            Dictionary with news for each symbol
        """
        news_dict = {}

        for symbol in symbols:
            try:
                news_df = FundamentalProvider.get_stock_news(symbol)
                if not news_df.empty:
                    # Get top news
                    news_dict[symbol] = []
                    for _, row in news_df.head(limit).iterrows():
                        news_dict[symbol].append({
                            'title': row.get('title', ''),
                            'time': row.get('time', ''),
                            'url': row.get('url', '')
                        })
            except Exception as e:
                logger.warning(f"Failed to get news for {symbol}: {e}")
                news_dict[symbol] = []

        return news_dict

    def check_announcements_for_symbols(self, symbols: List[str], limit: int = 2) -> Dict:
        """Check latest announcements for given symbols.

        Args:
            symbols: List of stock symbols
            limit: Number of announcements per stock

        Returns:
            Dictionary with announcements for each symbol
        """
        # Use akshare disclosure interface
        import akshare as ak

        ann_dict = {}

        for symbol in symbols:
            try:
                df = ak.stock_zh_a_disclosure_report_cninfo(symbol=symbol)
                if not df.empty:
                    ann_dict[symbol] = []
                    for _, row in df.head(limit).iterrows():
                        ann_dict[symbol].append({
                            'title': row.get('公告标题', ''),
                            'time': row.get('公告时间', ''),
                            'url': row.get('公告链接', '')
                        })
            except Exception as e:
                logger.warning(f"Failed to get announcements for {symbol}: {e}")
                ann_dict[symbol] = []

        return ann_dict

    def generate_push_report(self, user_id: int) -> Optional[Dict]:
        """Generate push report for user.

        Args:
            user_id: User ID

        Returns:
            Push report dictionary or None
        """
        # Get user preference
        pref = self.user_repo.get_user_preference(user_id)
        if not pref or not pref.push_enabled:
            return None

        # Get watchlist data
        watchlist_data = self.collect_watchlist_data(user_id)

        report = {
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'stocks': watchlist_data['stocks'],
            'alerts': [],
            'news': {},
            'announcements': {}
        }

        # Collect alerts
        for stock in watchlist_data['stocks']:
            if stock.get('alert_triggered'):
                report['alerts'].append({
                    'symbol': stock['symbol'],
                    'reason': stock.get('alert_reason'),
                    'current_price': stock.get('current_price')
                })

        # Collect news if enabled
        if pref.news_alert:
            symbols = [s['symbol'] for s in watchlist_data['stocks']]
            report['news'] = self.check_news_for_symbols(symbols)

        # Collect announcements if enabled
        if pref.announcement_alert:
            symbols = [s['symbol'] for s in watchlist_data['stocks']]
            report['announcements'] = self.check_announcements_for_symbols(symbols)

        return report

    def send_push_notification(self, user_id: int, report: Dict) -> bool:
        """Send push notification to user.

        In production, this would integrate with:
        - Email service
        - SMS service
        - Webhook
        - Push notification service (FCM, APNs, etc.)

        Args:
            user_id: User ID
            report: Push report

        Returns:
            True if sent successfully
        """
        # Log the report (in production, send via email/webhook)
        logger.info(f"Push report for user {user_id}:")
        logger.info(f"  - Stocks tracked: {len(report.get('stocks', []))}")
        logger.info(f"  - Alerts: {len(report.get('alerts', []))}")

        # Check for alerts
        if report.get('alerts'):
            logger.warning(f"  Alert details: {report['alerts']}")

        # In production, implement actual push:
        # - Email: send_email(user.email, subject, body)
        # - SMS: send_sms(user.phone, message)
        # - Webhook: post_to_webhook(user.webhook_url, data)

        return True


# Service singleton
_push_service: Optional[PushService] = None


def get_push_service() -> PushService:
    """Get push service instance."""
    global _push_service
    if _push_service is None:
        _push_service = PushService()
    return _push_service


def run_daily_push():
    """Run daily push notification job.

    This function should be called by scheduler (APScheduler).
    """
    service = get_push_service()

    # Get all users with push enabled
    users = service.get_all_users_with_push_enabled()

    for user in users:
        try:
            report = service.generate_push_report(user['user_id'])
            if report:
                service.send_push_notification(user['user_id'], report)
                logger.info(f"Daily push sent to user {user['user_id']}")
        except Exception as e:
            logger.error(f"Failed to send push to user {user['user_id']}: {e}")


def test_watchlist_push(user_id: int) -> Dict:
    """Test push for a specific user.

    Args:
        user_id: User ID

    Returns:
        Push report dictionary
    """
    service = get_push_service()
    report = service.generate_push_report(user_id)
    if report:
        service.send_push_notification(user_id, report)
    return report or {'message': 'No push data'}
