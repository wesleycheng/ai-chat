"""统一异常处理模块

提供：
- 自定义业务异常类
- 全局异常处理器
- 统一响应格式
"""
from typing import Any, Optional, Type
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from httpx import HTTPStatusError
import structlog

logger = structlog.get_logger()


# ==================== 统一响应格式 ====================

class APIResponse:
    """统一 API 响应格式"""
    
    @staticmethod
    def success(data: Any = None, message: str = "操作成功") -> dict:
        """成功响应"""
        return {
            "status": "success",
            "data": data,
            "message": message,
        }
    
    @staticmethod
    def error(
        message: str = "操作失败",
        code: int = 400,
        details: Any = None,
        request_id: Optional[str] = None
    ) -> dict:
        """错误响应"""
        response = {
            "status": "error",
            "message": message,
            "code": code,
        }
        if details is not None:
            response["details"] = details
        if request_id:
            response["request_id"] = request_id
        return response


# ==================== 自定义业务异常 ====================

class AppException(Exception):
    """应用基础异常"""
    
    def __init__(
        self,
        message: str = "应用异常",
        code: int = 500,
        details: Any = None
    ):
        self.message = message
        self.code = code
        self.details = details
        super().__init__(self.message)


class NotFoundException(AppException):
    """资源不存在"""
    
    def __init__(self, message: str = "资源不存在", details: Any = None):
        super().__init__(message=message, code=404, details=details)


class UnauthorizedException(AppException):
    """未授权"""
    
    def __init__(self, message: str = "未授权访问", details: Any = None):
        super().__init__(message=message, code=401, details=details)


class ForbiddenException(AppException):
    """禁止访问"""
    
    def __init__(self, message: str = "权限不足", details: Any = None):
        super().__init__(message=message, code=403, details=details)


class ValidationException(AppException):
    """验证失败"""
    
    def __init__(self, message: str = "数据验证失败", details: Any = None):
        super().__init__(message=message, code=422, details=details)


class ConflictException(AppException):
    """资源冲突"""
    
    def __init__(self, message: str = "资源冲突", details: Any = None):
        super().__init__(message=message, code=409, details=details)


class ExternalServiceException(AppException):
    """外部服务异常"""
    
    def __init__(self, message: str = "外部服务错误", details: Any = None):
        super().__init__(message=message, code=502, details=details)


class RateLimitException(AppException):
    """请求频率限制"""
    
    def __init__(self, message: str = "请求过于频繁", details: Any = None):
        super().__init__(message=message, code=429, details=details)


# ==================== 全局异常处理器 ====================

async def _get_request_id(request: Request) -> Optional[str]:
    """获取请求ID用于追踪"""
    return request.headers.get("X-Request-ID") or str(id(request))


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """处理自定义应用异常"""
    request_id = await _get_request_id(request)
    logger.warning(
        "业务异常",
        request_id=request_id,
        path=request.url.path,
        method=request.method,
        exc_message=exc.message,
        exc_code=exc.code,
        exc_details=exc.details,
    )
    
    return JSONResponse(
        status_code=exc.code,
        content=APIResponse.error(
            message=exc.message,
            code=exc.code,
            details=exc.details,
            request_id=request_id,
        ),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """处理请求验证错误"""
    request_id = await _get_request_id(request)
    
    # 提取字段错误详情
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"] if loc not in ("body", "query", "path"))
        errors.append({
            "field": field or "unknown",
            "message": error["msg"],
            "type": error["type"],
        })
    
    logger.warning(
        "请求验证失败",
        request_id=request_id,
        path=request.url.path,
        method=request.method,
        errors=errors,
    )
    
    return JSONResponse(
        status_code=422,
        content=APIResponse.error(
            message="请求参数验证失败",
            code=422,
            details=errors,
            request_id=request_id,
        ),
    )


async def pydantic_validation_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """处理 Pydantic 验证错误"""
    request_id = await _get_request_id(request)
    
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"] if isinstance(loc, str))
        errors.append({
            "field": field or "unknown",
            "message": error["msg"],
            "type": error["type"],
        })
    
    logger.warning(
        "数据验证失败",
        request_id=request_id,
        path=request.url.path,
        errors=errors,
    )
    
    return JSONResponse(
        status_code=422,
        content=APIResponse.error(
            message="数据验证失败",
            code=422,
            details=errors,
            request_id=request_id,
        ),
    )


async def sqlalchemy_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """处理 SQLAlchemy 数据库异常"""
    request_id = await _get_request_id(request)
    
    logger.error(
        "数据库异常",
        request_id=request_id,
        path=request.url.path,
        exc_info=str(exc),
    )
    
    message = "数据库操作失败"
    code = 500
    
    # 根据异常类型区分处理
    if isinstance(exc, IntegrityError):
        message = "数据冲突，可能违反唯一性约束"
        code = 409
    elif isinstance(exc, OperationalError):
        message = "数据库连接失败或超时"
        code = 503
    
    return JSONResponse(
        status_code=code,
        content=APIResponse.error(
            message=message,
            code=code,
            request_id=request_id,
        ),
    )


async def http_status_error_handler(request: Request, exc: HTTPStatusError) -> JSONResponse:
    """处理 HTTP 状态码错误（如外部 API 调用失败）"""
    request_id = await _get_request_id(request)
    
    logger.error(
        "外部 HTTP 请求失败",
        request_id=request_id,
        path=request.url.path,
        status_code=exc.response.status_code,
        response_body=getattr(exc.response, "text", None),
    )
    
    return JSONResponse(
        status_code=502,
        content=APIResponse.error(
            message="外部服务请求失败",
            code=502,
            details={"status": exc.response.status_code},
            request_id=request_id,
        ),
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """处理所有未捕获的异常"""
    request_id = await _get_request_id(request)
    
    # 记录完整堆栈
    logger.exception(
        "未处理的异常",
        request_id=request_id,
        path=request.url.path,
        method=request.method,
        exc_type=type(exc).__name__,
        exc_message=str(exc),
    )
    
    # 生产环境不暴露详细错误
    return JSONResponse(
        status_code=500,
        content=APIResponse.error(
            message="服务器内部错误，请稍后重试",
            code=500,
            request_id=request_id,
        ),
    )
