"""
代理路由模块
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from app.core.security import verify_auth_token
from app.service.proxy.proxy_service import ProxyService

router = APIRouter(prefix="/api/proxies", tags=["proxies"])


class AddProxiesRequest(BaseModel):
    proxies: List[str]


@router.get("")
async def get_proxies(request: Request):
    if not verify_auth_token(request.cookies.get("auth_token")):
        raise HTTPException(status_code=401, detail="Not authenticated")
    return await ProxyService.get_all_proxies()


@router.post("")
async def add_proxies(request: Request, payload: AddProxiesRequest):
    if not verify_auth_token(request.cookies.get("auth_token")):
        raise HTTPException(status_code=401, detail="Not authenticated")
    return await ProxyService.add_proxies(payload.proxies)


@router.delete("/{proxy_id}")
async def delete_proxy(request: Request, proxy_id: int):
    if not verify_auth_token(request.cookies.get("auth_token")):
        raise HTTPException(status_code=401, detail="Not authenticated")
    return await ProxyService.delete_proxy(proxy_id)


class TestProxyRequest(BaseModel):
    proxy_url: str


@router.post("/test")
async def test_proxy(request: Request, payload: TestProxyRequest):
    if not verify_auth_token(request.cookies.get("auth_token")):
        raise HTTPException(status_code=401, detail="Not authenticated")
    return await ProxyService.test_proxy(payload.proxy_url)
