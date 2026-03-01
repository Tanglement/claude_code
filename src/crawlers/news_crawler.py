"""News crawler."""

import re
from typing import Optional, Dict, List
from datetime import datetime

from .base import BaseCrawler
from src.utils.logger import get_logger

logger = get_logger(__name__)


class NewsCrawler(BaseCrawler):
    """Crawler for financial news."""

    def __init__(self):
        """Initialize news crawler."""
        super().__init__(timeout=15)

    def get_latest_news_sina(self, limit: int = 20) -> List[Dict]:
        """Get latest news from Sina Finance.

        Args:
            limit: Maximum number of news

        Returns:
            List of news dictionaries
        """
        url = "https://finance.sina.com.cn/stock/"
        response = self.get(url, delay=1)
        if not response:
            return []

        try:
            soup = self.parse_html(response.text)

            news_list = []
            # Find news articles
            for item in soup.select('.news-item, .topic-list li, .grid-4x1 li')[:limit]:
                try:
                    link = item.select_one('a')
                    if not link:
                        continue

                    title = link.get_text(strip=True)
                    href = link.get('href', '')

                    if not title or not href:
                        continue

                    # Extract stock codes from title
                    related_stocks = self._extract_stock_codes(title)

                    news = {
                        'title': title,
                        'url': href,
                        'source': '新浪财经',
                        'publish_time': datetime.now(),
                        'related_stocks': related_stocks,
                        'keywords': []
                    }

                    news_list.append(news)

                except Exception as e:
                    logger.warning(f"Failed to parse news item: {e}")
                    continue

            return news_list

        except Exception as e:
            logger.error(f"Failed to parse news page: {e}")
            return []

    def get_latest_news_eastmoney(self, limit: int = 20) -> List[Dict]:
        """Get latest news from East Money.

        Args:
            limit: Maximum number of news

        Returns:
            List of news dictionaries
        """
        url = "https://finance.eastmoney.com/a/index.html"
        response = self.get(url, delay=1)
        if not response:
            return []

        try:
            soup = self.parse_html(response.text)

            news_list = []
            for item in soup.select('.news_list li, .artical-list li')[:limit]:
                try:
                    link = item.select_one('a')
                    if not link:
                        continue

                    title = link.get_text(strip=True)
                    href = link.get('href', '')

                    if not title or not href:
                        continue

                    related_stocks = self._extract_stock_codes(title)

                    news = {
                        'title': title,
                        'url': href,
                        'source': '东方财富',
                        'publish_time': datetime.now(),
                        'related_stocks': related_stocks,
                        'keywords': []
                    }

                    news_list.append(news)

                except Exception as e:
                    logger.warning(f"Failed to parse news item: {e}")
                    continue

            return news_list

        except Exception as e:
            logger.error(f"Failed to parse East Money news: {e}")
            return []

    def get_stock_news(self, symbol: str, limit: int = 10) -> List[Dict]:
        """Get news related to a specific stock.

        Args:
            symbol: Stock code
            limit: Maximum number of news

        Returns:
            List of news dictionaries
        """
        # Sina stock news
        url = f"https://finance.sina.com.cn/stock/{symbol}.shtml"
        response = self.get(url, delay=0.5)

        if not response:
            return []

        try:
            soup = self.parse_html(response.text)

            news_list = []
            for item in soup.select('.blk_container li, .artical-list li')[:limit]:
                try:
                    link = item.select_one('a')
                    if not link:
                        continue

                    title = link.get_text(strip=True)
                    href = link.get('href', '')

                    if not title or not href:
                        continue

                    news = {
                        'title': title,
                        'url': href,
                        'source': '新浪财经',
                        'publish_time': datetime.now(),
                        'related_stocks': [symbol],
                        'keywords': []
                    }

                    news_list.append(news)

                except Exception as e:
                    continue

            return news_list

        except Exception as e:
            logger.error(f"Failed to parse stock news: {e}")
            return []

    def get_news_content(self, url: str) -> Optional[Dict]:
        """Get full news content.

        Args:
            url: News URL

        Returns:
            News content dictionary
        """
        response = self.get(url, delay=0.5)
        if not response:
            return None

        try:
            soup = self.parse_html(response.text)

            # Extract content (simplified)
            content = ''
            article = soup.select_one('.article, .artical-main, .WB_editor_iframe')
            if article:
                content = article.get_text(strip=True)

            # Extract date
            date_str = ''
            date_elem = soup.select_one('.date, .time, .publish_time')
            if date_elem:
                date_str = date_elem.get_text(strip=True)

            return {
                'content': content,
                'date_str': date_str
            }

        except Exception as e:
            logger.error(f"Failed to parse news content: {e}")
            return None

    def _extract_stock_codes(self, text: str) -> List[str]:
        """Extract stock codes from text.

        Args:
            text: Text content

        Returns:
            List of stock codes
        """
        # Pattern for A-share codes (6 digits)
        pattern = r'\b[0-9]{6}\b'
        matches = re.findall(pattern, text)

        # Filter valid codes
        codes = []
        for code in matches:
            if code[0] in ['0', '3', '6']:
                codes.append(code)

        return list(set(codes))
