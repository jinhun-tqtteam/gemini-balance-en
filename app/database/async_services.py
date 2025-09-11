"""Enhanced async database services with improved error handling and connection management."""

import asyncio
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta

from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.database.connection import async_session_factory
from app.database.models import ErrorLog, RequestLog, FileRecord, Settings
from app.exception.custom_exceptions import DatabaseError
from app.log.logger import get_database_logger

logger = get_database_logger()


class AsyncDatabaseService:
    """Enhanced async database service with connection pool management."""
    
    def __init__(self):
        self._session_factory = async_session_factory
    
    @asynccontextmanager
    async def get_session(self) -> AsyncSession:
        """Get database session with automatic cleanup and error handling."""
        session = self._session_factory()
        try:
            yield session
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Database error: {e}")
            raise DatabaseError(f"Database operation failed: {str(e)}")
        except Exception as e:
            await session.rollback()
            logger.error(f"Unexpected error in database session: {e}")
            raise
        finally:
            await session.close()
    
    async def add_error_log(
        self,
        gemini_key: str,
        model_name: str,
        error_type: str,
        error_log: str,
        error_code: Optional[int] = None,
        request_msg: Optional[Dict[str, Any]] = None
    ) -> Optional[int]:
        """Add error log with enhanced error handling."""
        try:
            async with self.get_session() as session:
                error_record = ErrorLog(
                    gemini_key=gemini_key,
                    model_name=model_name,
                    error_type=error_type,
                    error_log=error_log,
                    error_code=error_code,
                    request_msg=request_msg,
                    request_time=datetime.now()
                )
                session.add(error_record)
                await session.flush()
                return error_record.id
        except Exception as e:
            logger.error(f"Failed to add error log: {e}")
            # Don't re-raise here to avoid recursive errors
            return None
    
    async def add_request_log(
        self,
        ip_address: str,
        api_type: str,
        model_name: str,
        api_key: str,
        request_body: str,
        response_body: str,
        is_success: bool,
        status_code: Optional[int] = None,
        latency_ms: Optional[int] = None
    ) -> Optional[int]:
        """Add request log with enhanced validation."""
        try:
            # Truncate large payloads to prevent database issues
            max_body_size = 50000  # 50KB limit
            if len(request_body) > max_body_size:
                request_body = request_body[:max_body_size] + "... [truncated]"
            if len(response_body) > max_body_size:
                response_body = response_body[:max_body_size] + "... [truncated]"
            
            async with self.get_session() as session:
                request_record = RequestLog(
                    ip_address=ip_address[:50] if ip_address else None,  # Ensure IP fits
                    api_type=api_type,
                    model_name=model_name,
                    api_key=api_key,
                    request_body=request_body,
                    response_body=response_body,
                    is_success=is_success,
                    status_code=status_code,
                    latency_ms=latency_ms,
                    created_at=datetime.now()
                )
                session.add(request_record)
                await session.flush()
                return request_record.id
        except Exception as e:
            logger.error(f"Failed to add request log: {e}")
            return None
    
    async def get_error_logs(
        self,
        limit: int = 100,
        offset: int = 0,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        error_type: Optional[str] = None
    ) -> List[ErrorLog]:
        """Get error logs with filtering and pagination."""
        async with self.get_session() as session:
            query = select(ErrorLog).order_by(ErrorLog.request_time.desc())
            
            if start_date:
                query = query.where(ErrorLog.request_time >= start_date)
            if end_date:
                query = query.where(ErrorLog.request_time <= end_date)
            if error_type:
                query = query.where(ErrorLog.error_type == error_type)
            
            query = query.offset(offset).limit(limit)
            result = await session.execute(query)
            return result.scalars().all()
    
    async def cleanup_old_logs(
        self,
        days_to_keep: int = 30,
        log_type: str = "both"  # "error", "request", or "both"
    ) -> Dict[str, int]:
        """Clean up old logs with configurable retention period."""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        deleted_counts = {"error_logs": 0, "request_logs": 0}
        
        async with self.get_session() as session:
            if log_type in ("error", "both"):
                error_delete_query = delete(ErrorLog).where(
                    ErrorLog.request_time < cutoff_date
                )
                error_result = await session.execute(error_delete_query)
                deleted_counts["error_logs"] = error_result.rowcount
            
            if log_type in ("request", "both"):
                request_delete_query = delete(RequestLog).where(
                    RequestLog.created_at < cutoff_date
                )
                request_result = await session.execute(request_delete_query)
                deleted_counts["request_logs"] = request_result.rowcount
        
        logger.info(f"Cleaned up old logs: {deleted_counts}")
        return deleted_counts
    
    async def get_stats(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get comprehensive API usage statistics."""
        if not start_date:
            start_date = datetime.now() - timedelta(days=7)
        if not end_date:
            end_date = datetime.now()
        
        async with self.get_session() as session:
            # Request statistics
            request_stats_query = select(
                func.count(RequestLog.id).label("total_requests"),
                func.sum(func.case([(RequestLog.is_success == True, 1)], else_=0)).label("successful_requests"),
                func.avg(RequestLog.latency_ms).label("avg_latency_ms"),
                func.count(func.distinct(RequestLog.api_key)).label("unique_api_keys")
            ).where(
                RequestLog.created_at >= start_date,
                RequestLog.created_at <= end_date
            )
            
            request_result = await session.execute(request_stats_query)
            request_stats = request_result.first()
            
            # Error statistics
            error_stats_query = select(
                func.count(ErrorLog.id).label("total_errors"),
                ErrorLog.error_type,
                func.count(ErrorLog.id).label("error_count")
            ).where(
                ErrorLog.request_time >= start_date,
                ErrorLog.request_time <= end_date
            ).group_by(ErrorLog.error_type)
            
            error_result = await session.execute(error_stats_query)
            error_breakdown = {row.error_type: row.error_count for row in error_result}
            
            return {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "requests": {
                    "total": request_stats.total_requests or 0,
                    "successful": request_stats.successful_requests or 0,
                    "success_rate": (
                        (request_stats.successful_requests or 0) / max(request_stats.total_requests or 1, 1) * 100
                    ),
                    "avg_latency_ms": float(request_stats.avg_latency_ms or 0),
                    "unique_api_keys": request_stats.unique_api_keys or 0
                },
                "errors": {
                    "total": sum(error_breakdown.values()),
                    "breakdown": error_breakdown
                }
            }
    
    async def health_check(self) -> bool:
        """Perform database health check."""
        try:
            async with self.get_session() as session:
                await session.execute(select(func.count()).select_from(Settings))
                return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


# Global instance
db_service = AsyncDatabaseService()
