"""Custom exception classes for better error handling and API responses."""

from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class BaseAPIException(HTTPException):
    """Base class for all API exceptions with enhanced error details."""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}


class APIKeyError(BaseAPIException):
    """Raised when API key related errors occur."""
    
    def __init__(self, detail: str = "Invalid or missing API key", **kwargs):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="API_KEY_ERROR",
            **kwargs
        )


class RateLimitError(BaseAPIException):
    """Raised when rate limits are exceeded."""
    
    def __init__(self, detail: str = "Rate limit exceeded", retry_after: Optional[int] = None, **kwargs):
        headers = kwargs.pop("headers", {})
        if retry_after:
            headers["Retry-After"] = str(retry_after)
        
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            error_code="RATE_LIMIT_ERROR",
            headers=headers,
            **kwargs
        )


class ProxyError(BaseAPIException):
    """Raised when proxy-related errors occur."""
    
    def __init__(self, detail: str = "Proxy connection failed", **kwargs):
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=detail,
            error_code="PROXY_ERROR",
            **kwargs
        )


class ModelNotFoundError(BaseAPIException):
    """Raised when requested model is not available."""
    
    def __init__(self, model_name: str, **kwargs):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model '{model_name}' not found or not supported",
            error_code="MODEL_NOT_FOUND",
            context={"model_name": model_name},
            **kwargs
        )


class ValidationError(BaseAPIException):
    """Raised when request validation fails."""
    
    def __init__(self, detail: str = "Request validation failed", field: Optional[str] = None, **kwargs):
        context = kwargs.pop("context", {})
        if field:
            context["field"] = field
            
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code="VALIDATION_ERROR",
            context=context,
            **kwargs
        )


class ConfigurationError(BaseAPIException):
    """Raised when configuration-related errors occur."""
    
    def __init__(self, detail: str = "Configuration error", **kwargs):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="CONFIGURATION_ERROR",
            **kwargs
        )


class ExternalAPIError(BaseAPIException):
    """Raised when external API calls fail."""
    
    def __init__(self, detail: str = "External API error", service: Optional[str] = None, **kwargs):
        context = kwargs.pop("context", {})
        if service:
            context["service"] = service
            
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=detail,
            error_code="EXTERNAL_API_ERROR",
            context=context,
            **kwargs
        )


class DatabaseError(BaseAPIException):
    """Raised when database operations fail."""
    
    def __init__(self, detail: str = "Database operation failed", **kwargs):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="DATABASE_ERROR",
            **kwargs
        )
