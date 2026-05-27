import os
from typing import AsyncGenerator
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool

from .config import settings

# 根据数据库类型决定是否使用连接池
is_sqlite = settings.DATABASE_URL.startswith('sqlite')

# 异步引擎配置
engine_kwargs = {
    "echo": settings.DEBUG,
}
if not is_sqlite:
    engine_kwargs.update({
        "pool_size": 5,
        "max_overflow": 10,
        "pool_pre_ping": True,
    })

async_engine = create_async_engine(settings.DATABASE_URL, **engine_kwargs)
async_session_maker = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# 同步引擎 (用于 Alembic)
sync_engine_kwargs = {"echo": settings.DEBUG}
if is_sqlite:
    sync_engine_kwargs["poolclass"] = NullPool
else:
    sync_engine_kwargs.update({
        "pool_size": 5,
        "max_overflow": 10,
    })

engine = create_engine(settings.DATABASE_URL_SYNC, **sync_engine_kwargs)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """初始化数据库表"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """关闭数据库连接"""
    await async_engine.dispose()


def get_sync_db():
    """获取同步数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()