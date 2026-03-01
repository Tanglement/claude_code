"""News repository for data access layer."""

from typing import Optional, List
from datetime import datetime

from src.db.mongodb import get_mongodb
from src.models.news import News, Announcement, Comment, Log


class NewsRepository:
    """News data repository using MongoDB."""

    def __init__(self):
        """Initialize news repository."""
        self.db = get_mongodb()
        self.news_collection = 'news_collection'
        self.announcement_collection = 'announcement_collection'
        self.comment_collection = 'comment_collection'
        self.log_collection = 'log_collection'

    # ==================== News Operations ====================

    def insert_news(self, title: str, content: str, source: str,
                    url: str, publish_time: Optional[datetime] = None,
                    keywords: Optional[List[str]] = None,
                    sentiment: float = 0,
                    related_stocks: Optional[List[str]] = None) -> str:
        """Insert a news article.

        Args:
            title: News title
            content: News content
            source: News source
            url: Original URL
            publish_time: Publish time
            keywords: Related keywords
            sentiment: Sentiment score
            related_stocks: Related stock codes

        Returns:
            Inserted document ID
        """
        document = {
            'title': title,
            'content': content,
            'source': source,
            'url': url,
            'publish_time': publish_time or datetime.now(),
            'keywords': keywords or [],
            'sentiment': sentiment,
            'related_stocks': related_stocks or []
        }
        return self.db.insert_one(self.news_collection, document)

    def get_news_by_id(self, news_id: str) -> Optional[News]:
        """Get news by ID.

        Args:
            news_id: News ID

        Returns:
            News instance or None
        """
        from bson import ObjectId

        result = self.db.find_one(
            self.news_collection,
            {'_id': ObjectId(news_id)}
        )
        if not result:
            return None

        return News(
            id=str(result['_id']),
            title=result['title'],
            content=result['content'],
            publish_time=result.get('publish_time'),
            source=result['source'],
            url=result.get('url', ''),
            keywords=result.get('keywords', []),
            sentiment=result.get('sentiment', 0),
            related_stocks=result.get('related_stocks', [])
        )

    def get_latest_news(self, limit: int = 10) -> List[News]:
        """Get latest news.

        Args:
            limit: Maximum number of news

        Returns:
            List of News instances
        """
        results = self.db.find_many(
            self.news_collection,
            {},
            sort=[('publish_time', -1)],
            limit=limit
        )
        news_list = []
        for result in results:
            news_list.append(News(
                id=str(result['_id']),
                title=result['title'],
                content=result['content'],
                publish_time=result.get('publish_time'),
                source=result['source'],
                url=result.get('url', ''),
                keywords=result.get('keywords', []),
                sentiment=result.get('sentiment', 0),
                related_stocks=result.get('related_stocks', [])
            ))
        return news_list

    def get_news_by_stock(self, symbol: str, limit: int = 10) -> List[News]:
        """Get news related to a specific stock.

        Args:
            symbol: Stock code
            limit: Maximum number of news

        Returns:
            List of News instances
        """
        results = self.db.find_many(
            self.news_collection,
            {'related_stocks': symbol},
            sort=[('publish_time', -1)],
            limit=limit
        )
        news_list = []
        for result in results:
            news_list.append(News(
                id=str(result['_id']),
                title=result['title'],
                content=result['content'],
                publish_time=result.get('publish_time'),
                source=result['source'],
                url=result.get('url', ''),
                keywords=result.get('keywords', []),
                sentiment=result.get('sentiment', 0),
                related_stocks=result.get('related_stocks', [])
            ))
        return news_list

    def search_news(self, keyword: str, limit: int = 10) -> List[News]:
        """Search news by keyword.

        Args:
            keyword: Search keyword
            limit: Maximum number of news

        Returns:
            List of News instances
        """
        import re
        pattern = re.compile(keyword, re.IGNORECASE)
        results = self.db.find_many(
            self.news_collection,
            {'$or': [
                {'title': pattern},
                {'content': pattern}
            ]},
            sort=[('publish_time', -1)],
            limit=limit
        )
        news_list = []
        for result in results:
            news_list.append(News(
                id=str(result['_id']),
                title=result['title'],
                content=result['content'],
                publish_time=result.get('publish_time'),
                source=result['source'],
                url=result.get('url', ''),
                keywords=result.get('keywords', []),
                sentiment=result.get('sentiment', 0),
                related_stocks=result.get('related_stocks', [])
            ))
        return news_list

    # ==================== Announcement Operations ====================

    def insert_announcement(self, title: str, content: str,
                            company_code: str,
                            announcement_type: str,
                            publish_time: Optional[datetime] = None,
                            attachments: Optional[List[str]] = None) -> str:
        """Insert a company announcement.

        Args:
            title: Announcement title
            content: Announcement content
            company_code: Stock code
            announcement_type: Announcement type
            publish_time: Publish time
            attachments: List of attachment URLs

        Returns:
            Inserted document ID
        """
        document = {
            'title': title,
            'content': content,
            'company_code': company_code,
            'announcement_type': announcement_type,
            'publish_time': publish_time or datetime.now(),
            'attachments': attachments or []
        }
        return self.db.insert_one(self.announcement_collection, document)

    def get_announcements_by_stock(self, symbol: str,
                                   limit: int = 10) -> List[Announcement]:
        """Get announcements for a specific stock.

        Args:
            symbol: Stock code
            limit: Maximum number of announcements

        Returns:
            List of Announcement instances
        """
        results = self.db.find_many(
            self.announcement_collection,
            {'company_code': symbol},
            sort=[('publish_time', -1)],
            limit=limit
        )
        announcements = []
        for result in results:
            announcements.append(Announcement(
                id=str(result['_id']),
                title=result['title'],
                content=result['content'],
                publish_time=result.get('publish_time'),
                announcement_type=result['announcement_type'],
                company_code=result['company_code'],
                attachments=result.get('attachments', [])
            ))
        return announcements

    def get_latest_announcements(self, limit: int = 10) -> List[Announcement]:
        """Get latest announcements.

        Args:
            limit: Maximum number of announcements

        Returns:
            List of Announcement instances
        """
        results = self.db.find_many(
            self.announcement_collection,
            {},
            sort=[('publish_time', -1)],
            limit=limit
        )
        announcements = []
        for result in results:
            announcements.append(Announcement(
                id=str(result['_id']),
                title=result['title'],
                content=result['content'],
                publish_time=result.get('publish_time'),
                announcement_type=result['announcement_type'],
                company_code=result['company_code'],
                attachments=result.get('attachments', [])
            ))
        return announcements

    # ==================== Comment Operations ====================

    def insert_comment(self, user_id: int, username: str, content: str,
                       target_stock: str) -> str:
        """Insert a user comment.

        Args:
            user_id: User ID
            username: Username
            content: Comment content
            target_stock: Target stock code

        Returns:
            Inserted document ID
        """
        document = {
            'user_id': user_id,
            'username': username,
            'content': content,
            'target_stock': target_stock,
            'create_time': datetime.now(),
            'likes': 0,
            'dislikes': 0
        }
        return self.db.insert_one(self.comment_collection, document)

    def get_comments_by_stock(self, symbol: str,
                              limit: int = 20) -> List[Comment]:
        """Get comments for a specific stock.

        Args:
            symbol: Stock code
            limit: Maximum number of comments

        Returns:
            List of Comment instances
        """
        results = self.db.find_many(
            self.comment_collection,
            {'target_stock': symbol},
            sort=[('create_time', -1)],
            limit=limit
        )
        comments = []
        for result in results:
            comments.append(Comment(
                id=str(result['_id']),
                user_id=result['user_id'],
                username=result['username'],
                content=result['content'],
                target_stock=result['target_stock'],
                create_time=result.get('create_time'),
                likes=result.get('likes', 0),
                dislikes=result.get('dislikes', 0)
            ))
        return comments

    # ==================== Log Operations ====================

    def insert_log(self, level: str, message: str, source: str,
                    details: Optional[dict] = None) -> str:
        """Insert a system log.

        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            message: Log message
            source: Log source
            details: Additional details

        Returns:
            Inserted document ID
        """
        document = {
            'level': level,
            'message': message,
            'timestamp': datetime.now(),
            'source': source,
            'details': details or {}
        }
        return self.db.insert_one(self.log_collection, document)

    def get_logs(self, level: Optional[str] = None,
                 source: Optional[str] = None,
                 limit: int = 100) -> List[Log]:
        """Get system logs.

        Args:
            level: Filter by log level
            source: Filter by source
            limit: Maximum number of logs

        Returns:
            List of Log instances
        """
        query = {}
        if level:
            query['level'] = level
        if source:
            query['source'] = source

        results = self.db.find_many(
            self.log_collection,
            query,
            sort=[('timestamp', -1)],
            limit=limit
        )
        logs = []
        for result in results:
            logs.append(Log(
                id=str(result['_id']),
                level=result['level'],
                message=result['message'],
                timestamp=result.get('timestamp'),
                source=result['source'],
                details=result.get('details', {})
            ))
        return logs
