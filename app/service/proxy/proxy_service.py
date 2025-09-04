"""
代理服务模块
"""
import datetime
from typing import List, Dict, Any

from sqlalchemy import insert, delete, select

from app.database.connection import database
from app.database.models import Proxy
from app.log.logger import get_proxy_logger
from app.service.proxy.proxy_check_service import get_proxy_check_service

logger = get_proxy_logger()


class ProxyService:
    """
    代理服务类
    """

    @staticmethod
    async def get_all_proxies() -> List[Dict[str, Any]]:
        """获取所有代理"""
        query = select(Proxy)
        proxies = await database.fetch_all(query)
        return [dict(proxy) for proxy in proxies]

    @staticmethod
    async def add_proxies(proxies: List[str]) -> Dict[str, Any]:
        """批量添加代理"""
        async with database.transaction():
            existing_proxies_query = select(Proxy.url).where(Proxy.url.in_(proxies))
            existing_proxies = await database.fetch_all(existing_proxies_query)
            existing_urls = {proxy.url for proxy in existing_proxies}

            new_proxies = []
            for proxy_url in proxies:
                if proxy_url not in existing_urls:
                    new_proxies.append({"url": proxy_url, "created_at": datetime.datetime.now()})

            if new_proxies:
                query = insert(Proxy).values(new_proxies)
                await database.execute(query)

            return {"success": True, "message": f"Added {len(new_proxies)} new proxies."}

    @staticmethod
    async def delete_proxy(proxy_id: int) -> Dict[str, Any]:
        """删除代理"""
        query = delete(Proxy).where(Proxy.id == proxy_id)
        await database.execute(query)
        return {"success": True, "message": "Proxy deleted."}

    @staticmethod
    async def test_proxy(proxy_url: str) -> Dict[str, Any]:
        """测试代理连接"""
        proxy_service = get_proxy_check_service()
        result = await proxy_service.check_single_proxy(proxy_url, use_cache=False)
        return result.dict()
