"""News and announcement data models."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class News:
    """News model."""
    id: Optional[str] = None
    title: str = ''
    content: str = ''
    publish_time: Optional[datetime] = None
    source: str = ''
    url: str = ''
    keywords: List[str] = field(default_factory=list)
    sentiment: float = 0  # 情感倾向(-1到1)
    related_stocks: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'publish_time': self.publish_time.isoformat() if self.publish_time else None,
            'source': self.source,
            'url': self.url,
            'keywords': self.keywords,
            'sentiment': self.sentiment,
            'related_stocks': self.related_stocks
        }


@dataclass
class Announcement:
    """Company announcement model."""
    id: Optional[str] = None
    title: str = ''
    content: str = ''
    publish_time: Optional[datetime] = None
    announcement_type: str = ''  # 公告类型
    company_code: str = ''  # 股票代码
    attachments: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'publish_time': self.publish_time.isoformat() if self.publish_time else None,
            'announcement_type': self.announcement_type,
            'company_code': self.company_code,
            'attachments': self.attachments
        }


@dataclass
class Comment:
    """User comment model."""
    id: Optional[str] = None
    user_id: int = 0
    username: str = ''
    content: str = ''
    target_stock: str = ''  # 目标股票代码
    create_time: Optional[datetime] = None
    likes: int = 0
    dislikes: int = 0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.username,
            'content': self.content,
            'target_stock': self.target_stock,
            'create_time': self.create_time.isoformat() if self.create_time else None,
            'likes': self.likes,
            'dislikes': self.dislikes
        }


@dataclass
class Log:
    """System log model."""
    id: Optional[str] = None
    level: str = 'INFO'  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    message: str = ''
    timestamp: Optional[datetime] = None
    source: str = ''  # 日志来源
    details: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'level': self.level,
            'message': self.message,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'source': self.source,
            'details': self.details
        }
