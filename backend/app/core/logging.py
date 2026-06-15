"""
日志配置
"""
import logging
import sys
from datetime import datetime
from pathlib import Path

from app.core.config import settings


def setup_logging():
    """
    配置应用日志
    
    返回:
        logging.Logger: 配置好的 logger
    """
    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 日志文件路径
    log_file = log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
    
    # 根 logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # 格式化器
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # 静默一些第三方库的日志
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    return logger


# 获取 logger
logger = setup_logging()


def log_request(request, response_status):
    """
    记录请求日志
    
    参数:
        request: FastAPI 请求对象
        response_status: 响应状态码
    """
    logger.info(
        f"{request.method} {request.url.path} - {response_status}"
    )


def log_error(error_msg, exc_info=None):
    """
    记录错误日志
    
    参数:
        error_msg: 错误信息
        exc_info: 异常信息（可选）
    """
    logger.error(error_msg, exc_info=exc_info)


def log_debug(debug_msg):
    """
    记录调试日志
    
    参数:
        debug_msg: 调试信息
    """
    logger.debug(debug_msg)


def log_warning(warning_msg):
    """
    记录警告日志
    
    参数:
        warning_msg: 警告信息
    """
    logger.warning(warning_msg)


# 导出
__all__ = ["logger", "log_request", "log_error", "log_debug", "log_warning"]
