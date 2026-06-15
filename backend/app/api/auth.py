"""认证 API"""
import uuid
from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from ..core import (
    get_db, hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token, settings
)
from ..core.security import get_current_user
from ..core.exceptions import (
    ConflictException,
    UnauthorizedException,
    ValidationException,
    APIResponse,
)
from ..models import User
from ..schemas import UserLogin, UserRegister, TokenResponse, TokenRefresh, UserResponse

router = APIRouter(prefix="/auth", tags=["认证"])

security = HTTPBearer()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    """用户注册"""
    # 检查用户名是否存在
    result = await db.execute(select(User).where(User.username == data.username))
    if result.scalar_one_or_none():
        raise ConflictException(
            message="用户名已存在",
            details={"field": "username", "value": data.username}
        )
    
    # 检查邮箱是否存在
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise ConflictException(
            message="邮箱已被注册",
            details={"field": "email", "value": data.email}
        )
    
    # 创建用户
    user = User(
        id=str(uuid.uuid4()),
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password),
        role="user",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # 生成令牌
    token_data = {"sub": str(user.id)}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    return APIResponse.success(
        data={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
            }
        },
        message="注册成功"
    )


@router.post("/login")
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    """用户登录"""
    result = await db.execute(select(User).where(User.username == data.username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(data.password, user.hashed_password):
        raise UnauthorizedException(
            message="用户名或密码错误",
            details={"hint": "请检查用户名和密码是否正确"}
        )
    
    token_data = {"sub": str(user.id)}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    return APIResponse.success(
        data={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
            }
        },
        message="登录成功"
    )


@router.post("/refresh")
async def refresh_token(data: TokenRefresh):
    """刷新令牌"""
    payload = decode_token(data.refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise UnauthorizedException(
            message="无效的刷新令牌",
            details={"hint": "请重新登录获取新的令牌"}
        )
    
    user_id = payload.get("sub")
    token_data = {"sub": user_id}
    
    return APIResponse.success(
        data={
            "access_token": create_access_token(token_data),
            "refresh_token": create_refresh_token(token_data),
            "token_type": "bearer",
        },
        message="令牌刷新成功"
    )


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return APIResponse.success(
        data={
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "role": current_user.role,
        }
    )
