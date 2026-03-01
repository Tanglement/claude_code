"""News business logic service."""

from typing import Optional, List, Dict
from datetime import datetime

from src.repositories.news_repo import NewsRepository
from src.models.news import News, Announcement, Comment, Log
from src.utils.logger import get_logger

logger = get_logger(__name__)


class NewsService:
    """News business logic service."""

    def __init__(self):
        """Initialize news service."""
        self.repo = NewsRepository()

    def get_latest_news(self, limit: int = 10) -> List[Dict]:
        """Get latest news.

        Args:
            limit: Maximum number of news

        Returns:
            List of news dictionaries
        """
        news_list = self.repo.get_latest_news(limit=limit)
        return [n.to_dict() for n in news_list]

    def get_news_by_stock(self, symbol: str, limit: int = 10) -> List[Dict]:
        """Get news related to a specific stock.

        Args:
            symbol: Stock code
            limit: Maximum number of news

        Returns:
            List of news dictionaries
        """
        news_list = self.repo.get_news_by_stock(symbol, limit=limit)
        return [n.to_dict() for n in news_list]

    def search_news(self, keyword: str, limit: int = 10) -> List[Dict]:
        """Search news by keyword.

        Args:
            keyword: Search keyword
            limit: Maximum number of results

        Returns:
            List of news dictionaries
        """
        news_list = self.repo.search_news(keyword, limit=limit)
        return [n.to_dict() for n in news_list]

    def get_news_by_id(self, news_id: str) -> Optional[Dict]:
        """Get news by ID.

        Args:
            news_id: News ID

        Returns:
            News dictionary or None
        """
        news = self.repo.get_news_by_id(news_id)
        return news.to_dict() if news else None

    def save_news(self, news_data: Dict) -> str:
        """Save news article.

        Args:
            news_data: News data dictionary

        Returns:
            News ID
        """
        news_id = self.repo.insert_news(
            title=news_data['title'],
            content=news_data.get('content', ''),
            source=news_data['source'],
            url=news_data.get('url', ''),
            publish_time=news_data.get('publish_time'),
            keywords=news_data.get('keywords', []),
            sentiment=news_data.get('sentiment', 0),
            related_stocks=news_data.get('related_stocks', [])
        )
        logger.info(f"News saved: {news_data.get('title', '')[:50]}")
        return news_id

    # ==================== Announcements ====================

    def get_latest_announcements(self, limit: int = 10) -> List[Dict]:
        """Get latest announcements.

        Args:
            limit: Maximum number of announcements

        Returns:
            List of announcement dictionaries
        """
        announcements = self.repo.get_latest_announcements(limit=limit)
        return [a.to_dict() for a in announcements]

    def get_announcements_by_stock(self, symbol: str, limit: int = 10) -> List[Dict]:
        """Get announcements for a specific stock.

        Args:
            symbol: Stock code
            limit: Maximum number of announcements

        Returns:
            List of announcement dictionaries
        """
        announcements = self.repo.get_announcements_by_stock(symbol, limit=limit)
        return [a.to_dict() for a in announcements]

    def save_announcement(self, announcement_data: Dict) -> str:
        """Save announcement.

        Args:
            announcement_data: Announcement data dictionary

        Returns:
            Announcement ID
        """
        announcement_id = self.repo.insert_announcement(
            title=announcement_data['title'],
            content=announcement_data.get('content', ''),
            company_code=announcement_data['company_code'],
            announcement_type=announcement_data.get('announcement_type', ''),
            publish_time=announcement_data.get('publish_time'),
            attachments=announcement_data.get('attachments', [])
        )
        logger.info(f"Announcement saved: {announcement_data.get('title', '')[:50]}")
        return announcement_id

    # ==================== Comments ====================

    def get_comments_by_stock(self, symbol: str, limit: int = 20) -> List[Dict]:
        """Get comments for a specific stock.

        Args:
            symbol: Stock code
            limit: Maximum number of comments

        Returns:
            List of comment dictionaries
        """
        comments = self.repo.get_comments_by_stock(symbol, limit=limit)
        return [c.to_dict() for c in comments]

    def add_comment(self, user_id: int, username: str, content: str,
                   target_stock: str) -> str:
        """Add a comment.

        Args:
            user_id: User ID
            username: Username
            content: Comment content
            target_stock: Target stock code

        Returns:
            Comment ID
        """
        if not content or len(content) > 1000:
            raise ValueError("Comment content must be between 1 and 1000 characters")

        comment_id = self.repo.insert_comment(
            user_id=user_id,
            username=username,
            content=content,
            target_stock=target_stock
        )
        logger.info(f"Comment added: user={username}, stock={target_stock}")
        return comment_id


# Service singleton
_news_service: Optional[NewsService] = None


def get_news_service() -> NewsService:
    """Get news service instance."""
    global _news_service
    if _news_service is None:
        _news_service = NewsService()
    return _news_service
