"""Announcement crawler."""

import re
from typing import Optional, Dict, List
from datetime import datetime

from .base import BaseCrawler
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AnnouncementCrawler(BaseCrawler):
    """Crawler for company announcements."""

    def __init__(self):
        """Initialize announcement crawler."""
        super().__init__(timeout=15)

    def get_latest_announcements(self, limit: int = 20) -> List[Dict]:
        """Get latest announcements from cninfo.

        Args:
            limit: Maximum number of announcements

        Returns:
            List of announcement dictionaries
        """
        url = "http://www.cninfo.com.cn/new/disclosure/stock"
        params = {
            'pageSize': limit,
            'pageNo': 1,
            'tab1': 'fulltext',
            'plate': '',
            'stock': '',
            'searchkey': '',
            'category': '',
            'trade': '',
            'orgid': ''
        }

        response = self.post(url, data=params, delay=1)
        if not response:
            return []

        try:
            data = response.json()
            announcements = data.get('announcements', [])

            result = []
            for item in announcements:
                try:
                    # Extract stock code from announcementId
                    sec_id = str(item.get('secId', ''))
                    stock_code = sec_id.split('.')[-1] if '.' in sec_id else ''

                    announcement = {
                        'title': item.get('announcementTitle', ''),
                        'company_code': stock_code,
                        'announcement_type': item.get('categoryName', ''),
                        'publish_time': self._parse_datetime(item.get('announcementTime')),
                        'url': f"http://www.cninfo.com.cn/new/disclosure/detail?plate=szse&orgId={sec_id}&announcementId={item.get('announcementId', '')}",
                        'attachments': self._extract_attachments(item),
                        'content': ''
                    }

                    result.append(announcement)

                except Exception as e:
                    logger.warning(f"Failed to parse announcement: {e}")
                    continue

            return result

        except Exception as e:
            logger.error(f"Failed to parse announcements: {e}")
            return []

    def get_stock_announcements(self, symbol: str, limit: int = 10) -> List[Dict]:
        """Get announcements for a specific stock.

        Args:
            symbol: Stock code
            limit: Maximum number of announcements

        Returns:
            List of announcement dictionaries
        """
        # Convert to Shenzhen/Shanghai market code
        if symbol.startswith('0') or symbol.startswith('3'):
            plate = 'szse'
        else:
            plate = 'sse'

        url = "http://www.cninfo.com.cn/new/disclosure/stock"
        params = {
            'pageSize': limit,
            'pageNo': 1,
            'tab1': 'fulltext',
            'plate': plate,
            'stock': symbol,
            'searchkey': '',
            'category': '',
            'trade': '',
            'orgid': ''
        }

        response = self.post(url, data=params, delay=0.5)
        if not response:
            return []

        try:
            data = response.json()
            announcements = data.get('announcements', [])

            result = []
            for item in announcements:
                try:
                    sec_id = str(item.get('secId', ''))

                    announcement = {
                        'title': item.get('announcementTitle', ''),
                        'company_code': symbol,
                        'announcement_type': item.get('categoryName', ''),
                        'publish_time': self._parse_datetime(item.get('announcementTime')),
                        'url': f"http://www.cninfo.com.cn/new/disclosure/detail?plate={plate}&orgId={sec_id}&announcementId={item.get('announcementId', '')}",
                        'attachments': self._extract_attachments(item),
                        'content': ''
                    }

                    result.append(announcement)

                except Exception as e:
                    logger.warning(f"Failed to parse announcement: {e}")
                    continue

            return result

        except Exception as e:
            logger.error(f"Failed to parse stock announcements: {e}")
            return []

    def get_announcement_content(self, url: str) -> Optional[Dict]:
        """Get full announcement content.

        Args:
            url: Announcement URL

        Returns:
            Announcement content dictionary
        """
        response = self.get(url, delay=0.5)
        if not response:
            return None

        try:
            soup = self.parse_html(response.text)

            # Extract content
            content = ''
            article = soup.select_one('.content, .detail-cont, .announcement-content')
            if article:
                content = article.get_text(strip=True)

            return {
                'content': content
            }

        except Exception as e:
            logger.error(f"Failed to parse announcement content: {e}")
            return None

    def _parse_datetime(self, timestamp: int) -> Optional[datetime]:
        """Parse timestamp to datetime.

        Args:
            timestamp: Unix timestamp in milliseconds

        Returns:
            Datetime object
        """
        if not timestamp:
            return None

        try:
            return datetime.fromtimestamp(timestamp / 1000)
        except:
            return None

    def _extract_attachments(self, item: Dict) -> List[str]:
        """Extract attachment URLs from announcement.

        Args:
            item: Announcement item

        Returns:
            List of attachment URLs
        """
        attachments = []
        accessory = item.get('accessory', [])

        if isinstance(accessory, list):
            for att in accessory:
                if isinstance(att, dict):
                    url = att.get('url', '')
                    if url:
                        attachments.append(f"http://www.cninfo.com.cn{url}")

        return attachments
