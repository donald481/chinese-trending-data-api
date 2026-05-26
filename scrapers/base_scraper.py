import httpx
import random
import time
from typing import Dict, Optional, Any
from loguru import logger
from bs4 import BeautifulSoup

class BaseScraper:
    def __init__(self, proxy: Optional[str] = None):
        self.proxy = proxy
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
        ]

    def get_headers(self) -> Dict[str, str]:
        return {
            "User-Agent": random.choice(self.user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
        }

    def get_client(self) -> httpx.Client:
        proxies = None
        if self.proxy:
            proxies = {
                "http://": self.proxy,
                "https://": self.proxy
            }
        return httpx.Client(proxies=proxies, http2=True, timeout=15.0, follow_redirects=True)

    def fetch_html(self, url: str, headers_override: Optional[Dict[str, str]] = None, retries: int = 3, delay: float = 1.0) -> Optional[str]:
        headers = headers_override or self.get_headers()
        for attempt in range(1, retries + 1):
            try:
                with self.get_client() as client:
                    response = client.get(url, headers=headers)
                    if response.status_code == 200:
                        return response.text
                    elif response.status_code in [429, 503]:
                        logger.warning(f"Received status {response.status_code} for {url}. Retrying ({attempt}/{retries})...")
                    else:
                        logger.error(f"Failed to fetch {url}, status code: {response.status_code}")
            except Exception as e:
                logger.error(f"Error fetching {url}: {e}. Retrying ({attempt}/{retries})...")
            
            if attempt < retries:
                time.sleep(delay * attempt)
        return None
