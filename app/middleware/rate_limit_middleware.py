"""Rate limiting middleware to protect against abuse and ensure fair usage."""

import time
from typing import Dict, Optional
from collections import defaultdict
from contextlib import asynccontextmanager

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.exception.custom_exceptions import RateLimitError
from app.log.logger import get_middleware_logger

logger = get_middleware_logger()


class TokenBucket:
    """Token bucket algorithm for rate limiting."""
    
    def __init__(self, capacity: int, refill_rate: float, refill_period: float = 1.0):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate  # tokens per refill_period
        self.refill_period = refill_period
        self.last_refill = time.time()
    
    def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens from the bucket."""
        now = time.time()
        
        # Refill tokens based on elapsed time
        time_passed = now - self.last_refill
        if time_passed >= self.refill_period:
            periods_passed = time_passed / self.refill_period
            tokens_to_add = int(periods_passed * self.refill_rate)
            self.tokens = min(self.capacity, self.tokens + tokens_to_add)
            self.last_refill = now
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
    
    def time_until_refill(self) -> float:
        """Get time until next token refill."""
        now = time.time()
        time_since_refill = now - self.last_refill
        return max(0, self.refill_period - time_since_refill)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware with multiple strategies."""
    
    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        burst_capacity: int = 10,
        cleanup_interval: int = 300  # 5 minutes
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.burst_capacity = burst_capacity
        self.cleanup_interval = cleanup_interval
        
        # Storage for rate limiting data
        self.minute_buckets: Dict[str, TokenBucket] = {}
        self.hour_buckets: Dict[str, TokenBucket] = {}
        self.last_cleanup = time.time()
        
        # Exempt paths (health checks, static files, etc.)
        self.exempt_paths = {
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/static"
        }
    
    def _get_client_identifier(self, request: Request) -> str:
        """Get unique identifier for the client."""
        # Try to get API key from headers
        api_key = request.headers.get("authorization")
        if api_key and api_key.startswith("Bearer "):
            return f"api_key:{api_key[7:15]}..."  # Use first 8 chars for privacy
        
        # Try to get from query params
        api_key = request.query_params.get("key")
        if api_key:
            return f"api_key:{api_key[:8]}..."
        
        # Fall back to IP address
        client_ip = request.client.host if request.client else "unknown"
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        return f"ip:{client_ip}"
    
    def _is_exempt_path(self, path: str) -> bool:
        """Check if path is exempt from rate limiting."""
        return any(path.startswith(exempt) for exempt in self.exempt_paths)
    
    def _cleanup_old_buckets(self):
        """Clean up old, unused buckets to prevent memory leaks."""
        now = time.time()
        if now - self.last_cleanup < self.cleanup_interval:
            return
        
        # Remove buckets that haven't been used recently
        cutoff_time = now - 3600  # 1 hour
        
        old_minute_keys = [
            key for key, bucket in self.minute_buckets.items()
            if bucket.last_refill < cutoff_time
        ]
        old_hour_keys = [
            key for key, bucket in self.hour_buckets.items()
            if bucket.last_refill < cutoff_time
        ]
        
        for key in old_minute_keys:
            del self.minute_buckets[key]
        for key in old_hour_keys:
            del self.hour_buckets[key]
        
        self.last_cleanup = now
        
        if old_minute_keys or old_hour_keys:
            logger.debug(f"Cleaned up {len(old_minute_keys + old_hour_keys)} old rate limit buckets")
    
    async def dispatch(self, request: Request, call_next):
        """Process the request with rate limiting."""
        # Skip rate limiting for exempt paths
        if self._is_exempt_path(request.url.path):
            return await call_next(request)
        
        # Clean up old buckets periodically
        self._cleanup_old_buckets()
        
        client_id = self._get_client_identifier(request)
        
        # Get or create token buckets for this client
        if client_id not in self.minute_buckets:
            self.minute_buckets[client_id] = TokenBucket(
                capacity=self.burst_capacity,
                refill_rate=self.requests_per_minute / 60.0,  # per second
                refill_period=1.0
            )
        
        if client_id not in self.hour_buckets:
            self.hour_buckets[client_id] = TokenBucket(
                capacity=self.requests_per_hour,
                refill_rate=self.requests_per_hour / 3600.0,  # per second
                refill_period=1.0
            )
        
        minute_bucket = self.minute_buckets[client_id]
        hour_bucket = self.hour_buckets[client_id]
        
        # Check rate limits
        if not minute_bucket.consume():
            retry_after = int(minute_bucket.time_until_refill()) + 1
            logger.warning(f"Rate limit exceeded (per-minute) for {client_id}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "detail": f"Too many requests per minute. Limit: {self.requests_per_minute}/min",
                    "retry_after": retry_after
                },
                headers={"Retry-After": str(retry_after)}
            )
        
        if not hour_bucket.consume():
            retry_after = int(hour_bucket.time_until_refill()) + 1
            logger.warning(f"Rate limit exceeded (per-hour) for {client_id}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "detail": f"Too many requests per hour. Limit: {self.requests_per_hour}/hour",
                    "retry_after": retry_after
                },
                headers={"Retry-After": str(retry_after)}
            )
        
        # Process the request
        start_time = time.time()
        try:
            response = await call_next(request)
            
            # Add rate limit headers to response
            response.headers["X-RateLimit-Limit-Minute"] = str(self.requests_per_minute)
            response.headers["X-RateLimit-Remaining-Minute"] = str(int(minute_bucket.tokens))
            response.headers["X-RateLimit-Limit-Hour"] = str(self.requests_per_hour)
            response.headers["X-RateLimit-Remaining-Hour"] = str(int(hour_bucket.tokens))
            
            return response
            
        except Exception as e:
            # If request processing fails, we might want to refund the token
            # depending on the error type and business logic
            processing_time = time.time() - start_time
            if processing_time < 0.1:  # Very quick failure, might be client error
                logger.debug(f"Quick failure for {client_id}, not refunding token")
            raise
