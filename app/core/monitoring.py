"""Monitoring and health check system for application observability."""

import asyncio
import time
import psutil
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

from fastapi import FastAPI, APIRouter, Depends
from fastapi.responses import JSONResponse

from app.database.async_services import db_service
from app.log.logger import get_monitoring_logger
from app.config.config import settings

logger = get_monitoring_logger()


class HealthStatus(Enum):
    """Health check status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Result of a health check."""
    name: str
    status: HealthStatus
    message: str
    duration_ms: float
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None


@dataclass
class SystemMetrics:
    """System performance metrics."""
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_total_mb: float
    disk_percent: float
    disk_free_gb: float
    disk_total_gb: float
    uptime_seconds: float
    load_average: Optional[List[float]] = None


class HealthChecker:
    """Comprehensive health checking system."""
    
    def __init__(self):
        self.checks: Dict[str, callable] = {}
        self.startup_time = time.time()
        self.last_metrics_update = 0
        self.cached_metrics: Optional[SystemMetrics] = None
        self.metrics_cache_duration = 10  # seconds
    
    def register_check(self, name: str, check_func: callable):
        """Register a health check function."""
        self.checks[name] = check_func
        logger.info(f"Registered health check: {name}")
    
    async def run_check(self, name: str) -> HealthCheckResult:
        """Run a single health check."""
        start_time = time.time()
        
        try:
            if name not in self.checks:
                return HealthCheckResult(
                    name=name,
                    status=HealthStatus.UNKNOWN,
                    message=f"Check '{name}' not found",
                    duration_ms=0,
                    timestamp=datetime.now()
                )
            
            check_func = self.checks[name]
            
            # Run check with timeout
            try:
                result = await asyncio.wait_for(check_func(), timeout=30.0)
                if isinstance(result, bool):
                    status = HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY
                    message = "OK" if result else "Check failed"
                    details = None
                elif isinstance(result, dict):
                    status = HealthStatus(result.get("status", "unknown"))
                    message = result.get("message", "")
                    details = result.get("details")
                else:
                    status = HealthStatus.HEALTHY
                    message = str(result)
                    details = None
                    
            except asyncio.TimeoutError:
                status = HealthStatus.UNHEALTHY
                message = "Check timed out after 30 seconds"
                details = None
            
        except Exception as e:
            status = HealthStatus.UNHEALTHY
            message = f"Check failed: {str(e)}"
            details = {"error_type": type(e).__name__}
            logger.error(f"Health check '{name}' failed: {e}")
        
        duration_ms = (time.time() - start_time) * 1000
        
        return HealthCheckResult(
            name=name,
            status=status,
            message=message,
            duration_ms=duration_ms,
            timestamp=datetime.now(),
            details=details
        )
    
    async def run_all_checks(self) -> Dict[str, HealthCheckResult]:
        """Run all registered health checks."""
        tasks = [
            self.run_check(name) for name in self.checks.keys()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        check_results = {}
        for i, result in enumerate(results):
            check_name = list(self.checks.keys())[i]
            if isinstance(result, Exception):
                check_results[check_name] = HealthCheckResult(
                    name=check_name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Check execution failed: {str(result)}",
                    duration_ms=0,
                    timestamp=datetime.now()
                )
            else:
                check_results[check_name] = result
        
        return check_results
    
    def get_system_metrics(self) -> SystemMetrics:
        """Get current system performance metrics."""
        now = time.time()
        
        # Use cached metrics if they're fresh
        if (self.cached_metrics and 
            now - self.last_metrics_update < self.metrics_cache_duration):
            return self.cached_metrics
        
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_mb = memory.used / (1024 * 1024)
            memory_total_mb = memory.total / (1024 * 1024)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            disk_free_gb = disk.free / (1024 * 1024 * 1024)
            disk_total_gb = disk.total / (1024 * 1024 * 1024)
            
            # Uptime
            uptime_seconds = now - self.startup_time
            
            # Load average (Unix-like systems only)
            load_average = None
            try:
                load_average = list(psutil.getloadavg())
            except (AttributeError, OSError):
                pass  # Windows doesn't have load average
            
            metrics = SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_used_mb=memory_used_mb,
                memory_total_mb=memory_total_mb,
                disk_percent=disk_percent,
                disk_free_gb=disk_free_gb,
                disk_total_gb=disk_total_gb,
                uptime_seconds=uptime_seconds,
                load_average=load_average
            )
            
            # Cache the metrics
            self.cached_metrics = metrics
            self.last_metrics_update = now
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get system metrics: {e}")
            # Return default metrics on error
            return SystemMetrics(
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_used_mb=0.0,
                memory_total_mb=0.0,
                disk_percent=0.0,
                disk_free_gb=0.0,
                disk_total_gb=0.0,
                uptime_seconds=now - self.startup_time
            )
    
    def get_overall_status(self, check_results: Dict[str, HealthCheckResult]) -> HealthStatus:
        """Determine overall system health status."""
        if not check_results:
            return HealthStatus.UNKNOWN
        
        statuses = [result.status for result in check_results.values()]
        
        # If any check is unhealthy, overall is unhealthy
        if HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY
        
        # If any check is degraded, overall is degraded
        if HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED
        
        # If all checks are healthy, overall is healthy
        if all(status == HealthStatus.HEALTHY for status in statuses):
            return HealthStatus.HEALTHY
        
        return HealthStatus.UNKNOWN


# Global health checker instance
health_checker = HealthChecker()


# Built-in health checks

async def database_health_check() -> Dict[str, Any]:
    """Check database connectivity and performance."""
    start_time = time.time()
    
    try:
        is_healthy = await db_service.health_check()
        duration = (time.time() - start_time) * 1000
        
        if is_healthy:
            return {
                "status": "healthy",
                "message": "Database connection OK",
                "details": {"response_time_ms": duration}
            }
        else:
            return {
                "status": "unhealthy",
                "message": "Database connection failed",
                "details": {"response_time_ms": duration}
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Database check failed: {str(e)}",
            "details": {"error": str(e)}
        }


async def api_keys_health_check() -> Dict[str, Any]:
    """Check if API keys are configured and potentially valid."""
    try:
        if not settings.API_KEYS or len(settings.API_KEYS) == 0:
            return {
                "status": "unhealthy",
                "message": "No API keys configured"
            }
        
        # Filter out empty/placeholder keys
        valid_keys = [
            key for key in settings.API_KEYS 
            if key and key.strip() and "please enter" not in key.lower()
        ]
        
        if not valid_keys:
            return {
                "status": "degraded",
                "message": "API keys appear to be placeholders",
                "details": {"total_keys": len(settings.API_KEYS)}
            }
        
        return {
            "status": "healthy",
            "message": "API keys configured",
            "details": {"total_keys": len(valid_keys)}
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"API key check failed: {str(e)}"
        }


async def system_resources_health_check() -> Dict[str, Any]:
    """Check system resource usage."""
    try:
        metrics = health_checker.get_system_metrics()
        
        # Define thresholds
        cpu_warning_threshold = 80.0
        cpu_critical_threshold = 95.0
        memory_warning_threshold = 80.0
        memory_critical_threshold = 90.0
        disk_warning_threshold = 80.0
        disk_critical_threshold = 95.0
        
        issues = []
        status = "healthy"
        
        # Check CPU
        if metrics.cpu_percent > cpu_critical_threshold:
            issues.append(f"Critical CPU usage: {metrics.cpu_percent:.1f}%")
            status = "unhealthy"
        elif metrics.cpu_percent > cpu_warning_threshold:
            issues.append(f"High CPU usage: {metrics.cpu_percent:.1f}%")
            if status == "healthy":
                status = "degraded"
        
        # Check Memory
        if metrics.memory_percent > memory_critical_threshold:
            issues.append(f"Critical memory usage: {metrics.memory_percent:.1f}%")
            status = "unhealthy"
        elif metrics.memory_percent > memory_warning_threshold:
            issues.append(f"High memory usage: {metrics.memory_percent:.1f}%")
            if status == "healthy":
                status = "degraded"
        
        # Check Disk
        if metrics.disk_percent > disk_critical_threshold:
            issues.append(f"Critical disk usage: {metrics.disk_percent:.1f}%")
            status = "unhealthy"
        elif metrics.disk_percent > disk_warning_threshold:
            issues.append(f"High disk usage: {metrics.disk_percent:.1f}%")
            if status == "healthy":
                status = "degraded"
        
        message = "System resources OK" if not issues else "; ".join(issues)
        
        return {
            "status": status,
            "message": message,
            "details": asdict(metrics)
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"System resource check failed: {str(e)}"
        }


# Register built-in health checks
health_checker.register_check("database", database_health_check)
health_checker.register_check("api_keys", api_keys_health_check)
health_checker.register_check("system_resources", system_resources_health_check)


# Health check routes

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def basic_health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": time.time() - health_checker.startup_time
    }


@router.get("/detailed")
async def detailed_health_check():
    """Detailed health check with all registered checks."""
    start_time = time.time()
    
    check_results = await health_checker.run_all_checks()
    overall_status = health_checker.get_overall_status(check_results)
    
    total_duration = (time.time() - start_time) * 1000
    
    return {
        "status": overall_status.value,
        "timestamp": datetime.now().isoformat(),
        "duration_ms": total_duration,
        "checks": {
            name: {
                "status": result.status.value,
                "message": result.message,
                "duration_ms": result.duration_ms,
                "details": result.details
            }
            for name, result in check_results.items()
        }
    }


@router.get("/metrics")
async def system_metrics():
    """Get current system performance metrics."""
    metrics = health_checker.get_system_metrics()
    return {
        "timestamp": datetime.now().isoformat(),
        "metrics": asdict(metrics)
    }


@router.get("/check/{check_name}")
async def individual_health_check(check_name: str):
    """Run a specific health check."""
    result = await health_checker.run_check(check_name)
    
    return {
        "status": result.status.value,
        "message": result.message,
        "duration_ms": result.duration_ms,
        "timestamp": result.timestamp.isoformat(),
        "details": result.details
    }


def setup_monitoring_routes(app: FastAPI):
    """Setup monitoring and health check routes."""
    app.include_router(router)
    logger.info("Monitoring routes configured")
