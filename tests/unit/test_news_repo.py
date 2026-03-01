# News Repository Tests

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime


# Mock database connections
@pytest.fixture
def mock_mongodb():
    """Create mock MongoDB connection."""
    mock = MagicMock()
    mock.insert_one.return_value = 'test_id'
    mock.find_one.return_value = None
    mock.find_many.return_value = []
    return mock


@pytest.fixture
def news_repo(mock_mongodb):
    """Create NewsRepository with mock database."""
    with patch('src.repositories.news_repo.get_mongodb', return_value=mock_mongodb):
        from src.repositories.news_repo import NewsRepository
        return NewsRepository()


# ==================== News Tests ====================

class TestInsertNews:
    """Test insert news"""

    def test_insert_news_normal(self, news_repo, mock_mongodb):
        """Normal case: Insert news successfully"""
        result = news_repo.insert_news(
            title="A股三大指数集体上涨",
            content="今日A股市场整体表现良好...",
            source="新浪财经",
            url="http://finance.sina.com.cn/stock/1",
            publish_time=datetime(2021, 6, 25, 15, 30, 0),
            keywords=["A股", "上证指数"],
            sentiment=0.3,
            related_stocks=["600519", "000001"]
        )
        assert result == 'test_id'

    def test_insert_news_empty_title(self, news_repo, mock_mongodb):
        """Boundary case: Title is empty"""
        with pytest.raises(Exception):
            news_repo.insert_news(
                title="",
                content="内容",
                source="新浪财经"
            )

    def test_insert_news_invalid_sentiment(self, news_repo, mock_mongodb):
        """Error case: Sentiment value out of range"""
        with pytest.raises(Exception):
            news_repo.insert_news(
                title="标题",
                content="内容",
                source="新浪财经",
                sentiment=2.0
            )


class TestGetLatestNews:
    """Test get latest news"""

    def test_get_latest_news_normal(self, news_repo, mock_mongodb):
        """Normal case: Get latest news"""
        mock_mongodb.find_many.return_value = [
            {
                '_id': 'test_id',
                'title': 'Test News',
                'content': 'Test content',
                'publish_time': datetime.now(),
                'source': 'Test Source',
                'url': 'http://test.com',
                'keywords': [],
                'sentiment': 0,
                'related_stocks': []
            }
        ]

        news = news_repo.get_latest_news(limit=10)
        assert isinstance(news, list)
        assert len(news) == 1

    def test_get_latest_news_zero_limit(self, news_repo, mock_mongodb):
        """Boundary case: Limit is 0"""
        news = news_repo.get_latest_news(limit=0)
        assert isinstance(news, list)


class TestGetNewsByStock:
    """Test get news by stock"""

    def test_get_news_by_stock_normal(self, news_repo, mock_mongodb):
        """Normal case: Get news by stock"""
        mock_mongodb.find_many.return_value = []

        news = news_repo.get_news_by_stock("600519", limit=10)
        assert isinstance(news, list)

    def test_get_news_by_stock_empty_symbol(self, news_repo, mock_mongodb):
        """Boundary case: Empty stock symbol"""
        with pytest.raises(Exception):
            news_repo.get_news_by_stock("", limit=10)


# ==================== Announcement Tests ====================

class TestInsertAnnouncement:
    """Test insert announcement"""

    def test_insert_announcement_normal(self, news_repo, mock_mongodb):
        """Normal case: Insert announcement successfully"""
        result = news_repo.insert_announcement(
            title="贵州茅台关于2020年度利润分配方案的公告",
            content="本公司及董事会全体成员保证公告内容...",
            company_code="600519",
            announcement_type="利润分配",
            publish_time=datetime(2021, 6, 25, 16, 0, 0),
            attachments=["http://static.cninfo.com.cn/1.pdf"]
        )
        assert result == 'test_id'


class TestGetAnnouncementsByStock:
    """Test get announcements by stock"""

    def test_get_announcements_normal(self, news_repo, mock_mongodb):
        """Normal case: Get announcements"""
        mock_mongodb.find_many.return_value = []

        announcements = news_repo.get_announcements_by_stock("600519", limit=10)
        assert isinstance(announcements, list)


# ==================== Comment Tests ====================

class TestInsertComment:
    """Test insert comment"""

    def test_insert_comment_normal(self, news_repo, mock_mongodb):
        """Normal case: Insert comment successfully"""
        result = news_repo.insert_comment(
            user_id=1,
            username="user123",
            content="茅台股价创新高，长期看好",
            target_stock="600519"
        )
        assert result == 'test_id'

    def test_insert_comment_empty_content(self, news_repo, mock_mongodb):
        """Boundary case: Empty content"""
        with pytest.raises(Exception):
            news_repo.insert_comment(
                user_id=1,
                username="user123",
                content="",
                target_stock="600519"
            )


class TestGetCommentsByStock:
    """Test get comments by stock"""

    def test_get_comments_normal(self, news_repo, mock_mongodb):
        """Normal case: Get comments"""
        mock_mongodb.find_many.return_value = []

        comments = news_repo.get_comments_by_stock("600519", limit=10)
        assert isinstance(comments, list)


# ==================== Log Tests ====================

class TestInsertLog:
    """Test insert log"""

    def test_insert_log_normal(self, news_repo, mock_mongodb):
        """Normal case: Insert log successfully"""
        result = news_repo.insert_log(
            level="INFO",
            message="User logged in",
            source="user_service"
        )
        assert result == 'test_id'

    def test_insert_log_invalid_level(self, news_repo, mock_mongodb):
        """Error case: Invalid log level"""
        with pytest.raises(Exception):
            news_repo.insert_log(
                level="INVALID",
                message="message",
                source="module"
            )


class TestGetLogs:
    """Test get logs"""

    def test_get_logs_normal(self, news_repo, mock_mongodb):
        """Normal case: Get logs"""
        mock_mongodb.find_many.return_value = []

        logs = news_repo.get_logs(limit=100)
        assert isinstance(logs, list)

    def test_get_logs_zero_limit(self, news_repo, mock_mongodb):
        """Boundary case: Limit is 0"""
        logs = news_repo.get_logs(limit=0)
        assert isinstance(logs, list)
