"""API 路由"""
from fastapi import APIRouter
from .auth import router as auth_router
from .chat import router as chat_router
from .files import router as files_router
from .agents import router as agents_router
from .config import router as config_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(chat_router)
api_router.include_router(files_router)
api_router.include_router(agents_router)
api_router.include_router(config_router)