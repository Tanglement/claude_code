# News Repository Tests

import pytest
from datetime import datetime
from src.repositories.news_repo import (
    insert_news,
    get_latest_news,
    get_news_by_stock,
    insert_announcement,
    get_announcements_by_stock,
    insert_comment,
    get_comments_by_stock,
    insert_log,
    get_logs
)
from src.models.exceptions import DatabaseError


# ==================== 新闻资讯测试 ====================

class TestInsertNews:
    """测试插入新闻资讯"""

    def test_insert_news_normal(self):
        """正常场景：插入新闻成功"""
        news_data = {
            "title": "A股三大指数集体上涨",
            "content": "今日A股市场整体表现良好...",
            "publish_time": "2021-06-25T15:30:00Z",
            "source": "新浪财经",
            "url": "http://finance.sina.com.cn/stock/1",
            "keywords": ["A股", "上证指数"],
            "sentiment": 0.3,
            "related_stocks": ["600519", "000001"]
        }
        result = insert_news(news_data)
        assert result is not None

    def test_insert_news_empty_title(self):
        """边界场景：标题为空"""
        with pytest.raises(ValueError, match="标题不能为空"):
            insert_news({
                "title": "",
                "content": "内容",
                "publish_time": "2021-06-25T15:30:00Z",
                "source": "新浪财经"
            })

    def test_insert_news_empty_content(self):
        """边界场景：内容为空"""
        with pytest.raises(ValueError, match="内容不能为空"):
            insert_news({
                "title": "标题",
                "content": "",
                "publish_time": "2021-06-25T15:30:00Z",
                "source": "新浪财经"
            })

    def test_insert_news_invalid_sentiment(self):
        """异常场景：情感值超出范围"""
        with pytest.raises(ValueError, match="情感值必须在-1到1之间"):
            insert_news({
                "title": "标题",
                "content": "内容",
                "publish_time": "2021-06-25T15:30:00Z",
                "source": "新浪财经",
                "sentiment": 2.0
            })

    def test_insert_news_invalid_publish_time(self):
        """异常场景：发布时间格式无效"""
        with pytest.raises(ValueError, match="时间格式无效"):
            insert_news({
                "title": "标题",
                "content": "内容",
                "publish_time": "invalid-time",
                "source": "新浪财经"
            })


class TestGetLatestNews:
    """测试获取最新新闻"""

    def test_get_latest_news_normal(self):
        """正常场景：获取最新新闻"""
        news = get_latest_news(limit=10)
        assert isinstance(news, list)

    def test_get_latest_news_zero_limit(self):
        """边界场景：limit为0"""
        news = get_latest_news(limit=0)
        assert len(news) == 0

    def test_get_latest_news_negative_limit(self):
        """异常场景：limit为负数"""
        with pytest.raises(ValueError, match="limit必须大于0"):
            get_latest_news(limit=-1)

    def test_get_latest_news_exceed_max(self):
        """边界场景：limit超过最大值"""
        news = get_latest_news(limit=1000)
        assert len(news) <= 100


class TestGetNewsByStock:
    """测试根据股票获取新闻"""

    def test_get_news_by_stock_normal(self):
        """正常场景：获取股票相关新闻"""
        news = get_news_by_stock("600519", limit=10)
        assert isinstance(news, list)

    def test_get_news_by_stock_empty_symbol(self):
        """边界场景：股票代码为空"""
        with pytest.raises(ValueError, match="股票代码不能为空"):
            get_news_by_stock("", limit=10)

    def test_get_news_by_stock_no_news(self):
        """边界场景：无相关新闻"""
        news = get_news_by_stock("999999", limit=10)
        assert len(news) == 0


# ==================== 公司公告测试 ====================

class TestInsertAnnouncement:
    """测试插入公司公告"""

    def test_insert_announcement_normal(self):
        """正常场景：插入公告成功"""
        announcement_data = {
            "title": "贵州茅台关于2020年度利润分配方案的公告",
            "content": "本公司及董事会全体成员保证公告内容...",
            "publish_time": "2021-06-25T16:00:00Z",
            "announcement_type": "利润分配",
            "company_code": "600519",
            "attachments": ["http://static.cninfo.com.cn/1.pdf"]
        }
        result = insert_announcement(announcement_data)
        assert result is not None

    def test_insert_announcement_empty_title(self):
        """边界场景：标题为空"""
        with pytest.raises(ValueError, match="标题不能为空"):
            insert_announcement({
                "title": "",
                "content": "内容",
                "publish_time": "2021-06-25T16:00:00Z",
                "announcement_type": "利润分配",
                "company_code": "600519"
            })

    def test_insert_announcement_invalid_type(self):
        """异常场景：公告类型无效"""
        with pytest.raises(ValueError, match="无效的公告类型"):
            insert_announcement({
                "title": "标题",
                "content": "内容",
                "publish_time": "2021-06-25T16:00:00Z",
                "announcement_type": "未知类型",
                "company_code": "600519"
            })


class TestGetAnnouncementsByStock:
    """测试查询公司公告"""

    def test_get_announcements_normal(self):
        """正常场景：查询公告"""
        announcements = get_announcements_by_stock("600519", limit=10)
        assert isinstance(announcements, list)

    def test_get_announcements_empty_symbol(self):
        """边界场景：股票代码为空"""
        with pytest.raises(ValueError, match="股票代码不能为空"):
            get_announcements_by_stock("", limit=10)


# ==================== 用户评论测试 ====================

class TestInsertComment:
    """测试插入用户评论"""

    def test_insert_comment_normal(self):
        """正常场景：插入评论成功"""
        result = insert_comment(
            user_id=1,
            username="user123",
            content="茅台股价创新高，长期看好",
            target_stock="600519"
        )
        assert result is not None

    def test_insert_comment_empty_content(self):
        """边界场景：评论内容为空"""
        with pytest.raises(ValueError, match="评论内容不能为空"):
            insert_comment(
                user_id=1,
                username="user123",
                content="",
                target_stock="600519"
            )

    def test_insert_comment_content_too_long(self):
        """边界场景：评论内容过长"""
        with pytest.raises(ValueError, match="评论内容超过最大长度"):
            insert_comment(
                user_id=1,
                username="user123",
                content="a" * 1001,
                target_stock="600519"
            )


class TestGetCommentsByStock:
    """测试查询用户评论"""

    def test_get_comments_normal(self):
        """正常场景：查询评论"""
        comments = get_comments_by_stock("600519", limit=10)
        assert isinstance(comments, list)

    def test_get_comments_empty_symbol(self):
        """边界场景：股票代码为空"""
        with pytest.raises(ValueError, match="股票代码不能为空"):
            get_comments_by_stock("", limit=10)


# ==================== 系统日志测试 ====================

class TestInsertLog:
    """测试插入系统日志"""

    def test_insert_log_normal(self):
        """正常场景：插入日志成功"""
        result = insert_log(
            level="INFO",
            message="User logged in",
            module="user_service"
        )
        assert result is not None

    def test_insert_log_invalid_level(self):
        """异常场景：日志级别无效"""
        with pytest.raises(ValueError, match="无效的日志级别"):
            insert_log(
                level="INVALID",
                message="message",
                module="module"
            )

    def test_insert_log_empty_message(self):
        """边界场景：日志消息为空"""
        with pytest.raises(ValueError, match="日志消息不能为空"):
            insert_log(
                level="INFO",
                message="",
                module="module"
            )


class TestGetLogs:
    """测试查询系统日志"""

    def test_get_logs_normal(self):
        """正常场景：查询日志"""
        logs = get_logs(limit=100)
        assert isinstance(logs, list)

    def test_get_logs_zero_limit(self):
        """边界场景：limit为0"""
        logs = get_logs(limit=0)
        assert len(logs) == 0
