"""AI Chat Platform - FastAPI 主入口"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import structlog

from .core import settings, init_db, close_db
from .core.exceptions import (
    app_exception_handler,
    validation_exception_handler,
    pydantic_validation_handler,
    sqlalchemy_handler,
    http_status_error_handler,
    generic_exception_handler,
    AppException,
)
from .api import api_router

# 配置 structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# 限流器
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期"""
    logger.info("启动 AI Chat Platform...")
    
    # 初始化数据库
    await init_db()
    logger.info("数据库连接成功")
    
    yield
    
    # 关闭数据库
    await close_db()
    logger.info("数据库连接已关闭")


# 创建应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="企业级多功能 AI Chat 平台",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 限流
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 注册路由
app.include_router(api_router, prefix="/api")


# ===== 全局异常处理 =====
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from httpx import HTTPStatusError

# 注册自定义异常
app.add_exception_handler(AppException, app_exception_handler)

# 注册验证异常
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ValidationError, pydantic_validation_handler)

# 注册数据库异常
app.add_exception_handler(SQLAlchemyError, sqlalchemy_handler)

# 注册外部服务异常
app.add_exception_handler(HTTPStatusError, http_status_error_handler)

# 注册通用异常（最后兜底）
app.add_exception_handler(Exception, generic_exception_handler)


# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "ok", "version": settings.APP_VERSION}


# 根路径
@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }
