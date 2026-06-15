"""
pytest 配置文件和公共 fixtures
"""
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from app.core.database import Base
from app.main import app
from httpx import AsyncClient


# 使用 SQLite 内存数据库进行测试
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """创建测试数据库引擎"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
    )
    
    # 创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()


@pytest.fixture
async def test_db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """创建测试数据库会话"""
    async_session = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session() as session:
        # 开始事务
        transaction = await session.begin_nested()
        
        yield session
        
        # 回滚事务
        await transaction.rollback()


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """创建测试客户端"""
    async with AsyncClient(app=app, base_url="<INTERNAL_HOST_REMOVED>") as ac:
        yield ac


# ========== 辅助函数 ==========

def create_test_user_data() -> dict:
    """创建测试用户数据"""
    return {
        "username": "testuser",
        "email": "<EMAIL_REMOVED>",
        "password": "TestPass123!",
    }


def create_test_model_data() -> dict:
    """创建测试模型配置数据"""
    return {
        "name": "Test Model",
        "provider": "openai",
        "api_base": "https://api.openai.com/v1",
        "api_key": "sk-test-key-encrypted",
        "model_name": "gpt-3.5-turbo",
        "is_default": True,
        "is_active": True,
    }


def create_test_agent_data() -> dict:
    """创建测试 Agent 数据"""
    return {
        "name": "Test Agent",
        "description": "A test agent for unit testing",
        "system_prompt": "You are a helpful assistant for testing.",
        "model_config_id": None,
        "tools": [],
        "is_active": True,
    }


def create_test_conversation_data() -> dict:
    """创建测试会话数据"""
    return {
        "title": "Test Conversation",
        "model_id": None,
        "agent_id": None,
    }


def get_auth_headers(token: str) -> dict:
    """获取认证头"""
    return {"Authorization": f"Bearer {token}"}
