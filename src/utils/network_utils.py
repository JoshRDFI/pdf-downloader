"""Network utilities for the PDF Downloader application.

This module provides utility functions for network operations.
"""

import logging
import requests
from typing import Dict, Any, Optional
from urllib.parse import urlparse

from config import config


logger = logging.getLogger(__name__)


def get_proxy_settings() -> Optional[Dict[str, str]]:
    """Get the proxy settings from the configuration.
    
    Returns:
        Dictionary containing proxy settings or None if proxy is disabled
    """
    if not config.get("network", "proxy_enabled", False):
        return None
    
    proxy_url = config.get("network", "proxy_url", "")
    if not proxy_url:
        return None
    
    proxy_username = config.get("network", "proxy_username", "")
    proxy_password = config.get("network", "proxy_password", "")
    
    # Add authentication to the proxy URL if provided
    if proxy_username and proxy_password:
        # Parse the URL
        parsed_url = urlparse(proxy_url)
        
        # Reconstruct the URL with authentication
        netloc = f"{proxy_username}:{proxy_password}@{parsed_url.netloc}"
        proxy_url = parsed_url._replace(netloc=netloc).geturl()
    
    return {
        "http": proxy_url,
        "https": proxy_url
    }


def get_user_agent() -> str:
    """Get the user agent from the configuration.
    
    Returns:
        User agent string
    """
    return config.get("network", "user_agent", 
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")


def get_timeout() -> int:
    """Get the timeout from the configuration.
    
    Returns:
        Timeout in seconds
    """
    return config.get("network", "timeout", 30)


def create_session() -> requests.Session:
    """Create a requests session with the configured settings.
    
    Returns:
        Requests session
    """
    session = requests.Session()
    
    # Set the user agent
    session.headers.update({"User-Agent": get_user_agent()})
    
    # Set the proxy
    proxies = get_proxy_settings()
    if proxies:
        session.proxies.update(proxies)
    
    return session


def get(url: str, **kwargs) -> requests.Response:
    """Send a GET request with the configured settings.
    
    Args:
        url: URL to request
        **kwargs: Additional arguments to pass to requests.get
        
    Returns:
        Response object
    """
    # Set default timeout if not provided
    if "timeout" not in kwargs:
        kwargs["timeout"] = get_timeout()
    
    # Set default headers if not provided
    if "headers" not in kwargs:
        kwargs["headers"] = {"User-Agent": get_user_agent()}
    elif "User-Agent" not in kwargs["headers"]:
        kwargs["headers"]["User-Agent"] = get_user_agent()
    
    # Set default proxies if not provided
    if "proxies" not in kwargs:
        proxies = get_proxy_settings()
        if proxies:
            kwargs["proxies"] = proxies
    
    return requests.get(url, **kwargs)


def post(url: str, **kwargs) -> requests.Response:
    """Send a POST request with the configured settings.
    
    Args:
        url: URL to request
        **kwargs: Additional arguments to pass to requests.post
        
    Returns:
        Response object
    """
    # Set default timeout if not provided
    if "timeout" not in kwargs:
        kwargs["timeout"] = get_timeout()
    
    # Set default headers if not provided
    if "headers" not in kwargs:
        kwargs["headers"] = {"User-Agent": get_user_agent()}
    elif "User-Agent" not in kwargs["headers"]:
        kwargs["headers"]["User-Agent"] = get_user_agent()
    
    # Set default proxies if not provided
    if "proxies" not in kwargs:
        proxies = get_proxy_settings()
        if proxies:
            kwargs["proxies"] = proxies
    
    return requests.post(url, **kwargs)