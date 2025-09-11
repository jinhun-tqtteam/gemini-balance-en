# Gemini Balance API Project

## Overview
This is a FastAPI-based proxy service for Gemini AI APIs with OpenAI compatibility, load balancing, and proxy support.

## Key Components
- **FastAPI Application**: Main web framework for API endpoints
- **Proxy Support**: Custom proxy format IP:PORT:USER:PASS for routing requests
- **Multi-API Support**: Gemini, OpenAI, and Vertex Express APIs
- **Database**: SQLAlchemy with MySQL/SQLite support
- **Web UI**: Configuration editor and monitoring dashboard

## Development
- **Main Entry**: `app/main.py` starts uvicorn server on port 8001
- **Configuration**: Environment variables loaded from `.env` file
- **Proxy Format**: Uses IP:PORT:USER:PASS instead of standard HTTP proxy URLs
- **Database Models**: Located in `app/database/models.py`
- **API Routes**: Organized in `app/router/` directory

## Architecture
- **Service Layer**: Business logic in `app/service/`
- **Database Layer**: Connection and models in `app/database/`
- **Middleware**: Request logging and smart routing
- **Static Files**: Web UI assets in `app/static/`
- **Templates**: Jinja2 templates in `app/templates/`

## Recent Changes
- Implemented custom proxy helper for IP:PORT:USER:PASS format
- Updated proxy validation and conversion for httpx compatibility
- Enhanced proxy checking service with proper format validation

## Modern Improvements (2024)
- **Enhanced Error Handling**: Custom exception classes with detailed error context
- **Rate Limiting**: Token bucket algorithm for API protection
- **Async Database**: Improved connection pool management and error handling
- **Testing Infrastructure**: Comprehensive pytest setup with fixtures
- **Performance Monitoring**: System metrics and health checks
- **Modern UI**: Glass morphism design with improved UX
- **Development Tools**: Code formatting, linting, and pre-commit hooks

## Best Practices Implemented
- Async-first architecture with proper error handling
- Structured logging with context-aware messages
- Database connection pooling with automatic cleanup
- Rate limiting with multiple strategies (per-minute, per-hour)
- Comprehensive health checks for system monitoring
- Modern FastAPI patterns with dependency injection