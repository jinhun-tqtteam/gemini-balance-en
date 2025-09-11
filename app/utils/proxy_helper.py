"""
Proxy helper utilities for converting proxy formats
"""
from typing import Optional, Tuple
from app.log.logger import get_config_routes_logger

logger = get_config_routes_logger()


def parse_proxy_format(proxy: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Parse proxy format from IP:PORT:USER:PASS to httpx compatible format
    
    Args:
        proxy: Proxy string in format IP:PORT:USER:PASS
        
    Returns:
        Tuple of (httpx_proxy_url, original_proxy_string) or (None, None) if invalid
    """
    try:
        parts = proxy.strip().split(':')
        if len(parts) != 4:
            return None, None
            
        ip, port, username, password = parts
        
        # Validate IP and port
        if not ip or not port:
            return None, None
            
        try:
            port_int = int(port)
            if not (1 <= port_int <= 65535):
                return None, None
        except ValueError:
            return None, None
            
        # Create httpx compatible proxy URL with authentication
        if username and password:
            httpx_proxy = f"http://{username}:{password}@{ip}:{port}"
        else:
            httpx_proxy = f"http://{ip}:{port}"
            
        return httpx_proxy, proxy
        
    except Exception as e:
        logger.debug(f"Failed to parse proxy format '{proxy}': {e}")
        return None, None


def is_valid_proxy_format(proxy: str) -> bool:
    """
    Validate proxy format IP:PORT:USER:PASS
    
    Args:
        proxy: Proxy string to validate
        
    Returns:
        True if valid format, False otherwise
    """
    httpx_proxy, _ = parse_proxy_format(proxy)
    return httpx_proxy is not None


def convert_proxy_for_httpx(proxy: str) -> Optional[str]:
    """
    Convert proxy from IP:PORT:USER:PASS format to httpx compatible format
    
    Args:
        proxy: Proxy string in format IP:PORT:USER:PASS
        
    Returns:
        httpx compatible proxy URL or None if invalid
    """
    httpx_proxy, _ = parse_proxy_format(proxy)
    return httpx_proxy