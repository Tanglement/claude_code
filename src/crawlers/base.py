"""Base crawler class."""

import time
import random
from typing import Optional, Dict, List
from abc import ABC, abstractmethod

import requests
from bs4 import BeautifulSoup

from src.utils.logger import get_logger

logger = get_logger(__name__)


class BaseCrawler(ABC):
    """Base crawler class with common functionality."""

    def __init__(self, timeout: int = 30, retry_times: int = 3):
        """Initialize crawler.

        Args:
            timeout: Request timeout in seconds
            retry_times: Number of retry attempts
        """
        self.timeout = timeout
        self.retry_times = retry_times
        self.session = requests.Session()

        # Common headers
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }

    def get(self, url: str, params: Optional[Dict] = None,
            headers: Optional[Dict] = None, delay: float = 1) -> Optional[requests.Response]:
        """Send GET request with retry logic.

        Args:
            url: Request URL
            params: Query parameters
            headers: Additional headers
            delay: Delay before request in seconds

        Returns:
            Response object or None on failure
        """
        # Apply delay to avoid being blocked
        if delay > 0:
            time.sleep(delay + random.uniform(0, 0.5))

        # Merge headers
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)

        for attempt in range(self.retry_times):
            try:
                response = self.session.get(
                    url,
                    params=params,
                    headers=request_headers,
                    timeout=self.timeout
                )

                if response.status_code == 200:
                    return response
                elif response.status_code == 403:
                    logger.warning(f"Access forbidden: {url}")
                    # Try with different User-Agent
                    self._rotate_user_agent()
                elif response.status_code == 404:
                    logger.warning(f"Page not found: {url}")
                    return None
                else:
                    logger.warning(f"Request failed with status {response.status_code}: {url}")

            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout: {url}")
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error: {e}")

            # Wait before retry
            time.sleep(2 ** attempt)

        logger.error(f"All retry attempts failed: {url}")
        return None

    def post(self, url: str, data: Optional[Dict] = None,
             json: Optional[Dict] = None, delay: float = 1) -> Optional[requests.Response]:
        """Send POST request.

        Args:
            url: Request URL
            data: Form data
            json: JSON data
            delay: Delay before request

        Returns:
            Response object or None on failure
        """
        if delay > 0:
            time.sleep(delay + random.uniform(0, 0.5))

        for attempt in range(self.retry_times):
            try:
                response = self.session.post(
                    url,
                    data=data,
                    json=json,
                    headers=self.headers,
                    timeout=self.timeout
                )

                if response.status_code == 200:
                    return response

            except requests.exceptions.RequestException as e:
                logger.error(f"POST request error: {e}")

            time.sleep(2 ** attempt)

        return None

    def _rotate_user_agent(self):
        """Rotate User-Agent to avoid being blocked."""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15'
        ]
        self.headers['User-Agent'] = random.choice(user_agents)

    def parse_html(self, html: str) -> BeautifulSoup:
        """Parse HTML content.

        Args:
            html: HTML content

        Returns:
            BeautifulSoup object
        """
        return BeautifulSoup(html, 'html.parser')

    def close(self):
        """Close session."""
        self.session.close()
