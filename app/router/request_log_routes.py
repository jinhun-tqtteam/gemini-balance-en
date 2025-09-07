from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.database.services import get_request_logs, get_request_logs_count, get_request_log_details
from app.core.security import verify_auth_token as verify_token_in_cookie
from datetime import datetime, timedelta

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Dependency to verify token from cookie for API calls
async def get_verified_token(request: Request):
    auth_token = request.cookies.get("auth_token")
    if not auth_token or not verify_token_in_cookie(auth_token):
        raise HTTPException(status_code=401, detail="Not authenticated")
    return auth_token

@router.get("/request-logs", response_class=HTMLResponse)
async def get_request_logs_page(request: Request):
    """Serve the request logs page."""
    auth_token = request.cookies.get("auth_token")
    if not auth_token or not verify_token_in_cookie(auth_token):
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse("request_logs.html", {"request": request})

@router.get("/api/request-logs")
async def api_get_request_logs(
    page: int = 1,
    limit: int = 15,
    api_type_search: str = None,
    model_name_search: str = None,
    key_search: str = None,
    status_code_search: str = None,
    sort_by: str = "id",
    sort_order: str = "desc",
    _=Depends(get_verified_token),
):
    """API endpoint to fetch request logs with pagination, searching, and sorting."""
    offset = (page - 1) * limit
    logs = await get_request_logs(
        limit=limit, 
        offset=offset, 
        api_type_search=api_type_search,
        model_name_search=model_name_search,
        key_search=key_search,
        status_code_search=status_code_search,
        sort_by=sort_by, 
        sort_order=sort_order
    )
    total_count = await get_request_logs_count(
        api_type_search=api_type_search,
        model_name_search=model_name_search,
        key_search=key_search,
        status_code_search=status_code_search
    )
    return {"logs": logs, "total_count": total_count}

@router.get("/api/request-logs/{log_id}")
async def api_get_request_log_details(
    log_id: int,
    _=Depends(get_verified_token),
):
    """API endpoint to fetch the details of a single request log."""
    details = await get_request_log_details(log_id)
    if not details:
        return JSONResponse(status_code=404, content={"message": "Log not found"})
    return details
