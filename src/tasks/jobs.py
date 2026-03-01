"""Job definitions for scheduled tasks."""

import os
import json
from datetime import datetime, date, timedelta

from src.utils.logger import get_logger
from src.services.stock_service import get_stock_service
from src.services.news_service import get_news_service

logger = get_logger(__name__)


def collect_realtime_quotes():
    """Collect realtime quotes for watchlist stocks.

    This job runs every 3 seconds to collect realtime quotes.
    """
    try:
        # Get watchlist from config or database
        watchlist = get_watchlist()

        if not watchlist:
            logger.debug("No stocks in watchlist")
            return

        from src.crawlers.quote_crawler import QuoteCrawler
        crawler = QuoteCrawler()

        quotes = crawler.get_quotes_batch(watchlist)

        # Save to database
        service = get_stock_service()
        for symbol, quote in quotes.items():
            service.save_realtime_data(quote)

        crawler.close()

        logger.info(f"Collected {len(quotes)} realtime quotes")

    except Exception as e:
        logger.error(f"Failed to collect realtime quotes: {e}")


def collect_news():
    """Collect latest news.

    This job runs every hour.
    """
    try:
        from src.crawlers.news_crawler import NewsCrawler
        crawler = NewsCrawler()

        # Get news from Sina
        news_list = crawler.get_latest_news_sina(limit=20)

        # Save to database
        service = get_news_service()
        for news in news_list:
            service.save_news(news)

        crawler.close()

        logger.info(f"Collected {len(news_list)} news articles")

    except Exception as e:
        logger.error(f"Failed to collect news: {e}")


def collect_announcements():
    """Collect latest announcements.

    This job runs every hour.
    """
    try:
        from src.crawlers.announcement_crawler import AnnouncementCrawler
        crawler = AnnouncementCrawler()

        # Get announcements
        announcements = crawler.get_latest_announcements(limit=20)

        # Save to database
        service = get_news_service()
        for announcement in announcements:
            service.save_announcement(announcement)

        crawler.close()

        logger.info(f"Collected {len(announcements)} announcements")

    except Exception as e:
        logger.error(f"Failed to collect announcements: {e}")


def update_history_data():
    """Update history data.

    This job runs daily at 17:00 (after market close).
    """
    try:
        # Get list of all stocks
        service = get_stock_service()
        stocks = service.get_all_stocks(limit=5000)

        # Get yesterday's date
        yesterday = date.today() - timedelta(days=1)

        from src.crawlers.quote_crawler import QuoteCrawler
        crawler = QuoteCrawler()

        # For each stock, get history for yesterday
        success_count = 0
        for stock in stocks:
            symbol = stock['symbol']

            # TODO: Implement history data collection
            # For now, we just log
            logger.debug(f"Would collect history for {symbol} on {yesterday}")

            success_count += 1

        crawler.close()

        logger.info(f"Updated history data for {success_count} stocks")

    except Exception as e:
        logger.error(f"Failed to update history data: {e}")


def backup_data():
    """Backup database data.

    This job runs daily at 23:00.
    """
    try:
        backup_dir = os.getenv('BACKUP_DIR', './backups')

        # Create backup directory if not exists
        os.makedirs(backup_dir, exist_ok=True)

        # Generate backup filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backup_dir, f'stock_backup_{timestamp}.json')

        # TODO: Implement actual backup logic
        # For now, just log
        logger.info(f"Would create backup: {backup_file}")

        # Example backup data structure
        backup_data = {
            'timestamp': datetime.now().isoformat(),
            'stocks': [],  # Stock basic info
            'quotes': [],  # Latest quotes
            'users': []    # User data (excluding passwords)
        }

        # Save backup metadata
        with open(backup_file, 'w') as f:
            json.dump(backup_data, f, indent=2)

        logger.info(f"Backup created: {backup_file}")

        # Cleanup old backups (keep last 7 days)
        cleanup_old_backups(backup_dir, days=7)

    except Exception as e:
        logger.error(f"Failed to backup data: {e}")


def get_watchlist():
    """Get stock watchlist.

    Returns:
        List of stock symbols
    """
    # TODO: Load from database or config
    # For now, return some default stocks
    return ['600519', '000001', '600036', '601318']


def cleanup_old_backups(backup_dir: str, days: int = 7):
    """Clean up old backup files.

    Args:
        backup_dir: Backup directory path
        days: Number of days to keep
    """
    try:
        cutoff = datetime.now() - timedelta(days=days)

        for filename in os.listdir(backup_dir):
            if not filename.endswith('.json'):
                continue

            filepath = os.path.join(backup_dir, filename)
            mtime = datetime.fromtimestamp(os.path.getmtime(filepath))

            if mtime < cutoff:
                os.remove(filepath)
                logger.info(f"Removed old backup: {filename}")

    except Exception as e:
        logger.error(f"Failed to cleanup old backups: {e}")
