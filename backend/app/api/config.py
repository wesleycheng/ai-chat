"""配置管理 API"""
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from ..core import get_db, encrypt_api_key, mask_api_key
from ..models import User, ModelConfig
from ..schemas import (
    ModelConfigCreate, ModelConfigUpdate, ModelConfigResponse,
    SuccessResponse, ErrorResponse
)
from ..core.exceptions import APIResponse
from .auth import get_current_user

router = APIRouter(prefix="/config", tags=["配置"])


@router.get("/models")
async def list_models(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取模型配置列表"""
    result = await db.execute(
        select(ModelConfig)
        .where(ModelConfig.user_id == current_user.id)
        .order_by(ModelConfig.created_at.desc())
    )
    models = result.scalars().all()

    # 脱敏 API Key
    from ..core.security import decrypt_api_key
    response = []
    for model in models:
        response.append(ModelConfigResponse(
            id=model.id,
            user_id=model.user_id,
            name=model.name,
            provider=model.provider.value,
            api_base=model.api_base,
            api_key_masked=mask_api_key(decrypt_api_key(model.encrypted_api_key)),
            model_name=model.model_name,
            params=model.params or {},
            is_default=model.is_default,
            is_active=model.is_active,
            created_at=model.created_at,
        ))

    return APIResponse.success(data={"items": response, "total": len(response)})


@router.post("/models", status_code=201)
async def create_model(
    data: ModelConfigCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建模型配置"""
    # 如果设为默认，先取消其他默认
    if data.is_default:
        result = await db.execute(
            select(ModelConfig).where(
                ModelConfig.user_id == current_user.id,
                ModelConfig.is_default == True,
            )
        )
        for old_default in result.scalars().all():
            old_default.is_default = False
            old_default.is_active = True

    model = ModelConfig(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        name=data.name,
        provider=data.provider,
        api_base=data.api_base,
        encrypted_api_key=encrypt_api_key(data.api_key),
        model_name=data.model_name,
        params=data.params or {},
        is_default=data.is_default if hasattr(data, 'is_default') and data.is_default else False,
        is_active=True,
    )
    db.add(model)
    await db.commit()
    await db.refresh(model)

    from ..core.security import decrypt_api_key
    return APIResponse.success(data=ModelConfigResponse(
        id=model.id,
        user_id=model.user_id,
        name=model.name,
        provider=model.provider.value,
        api_base=model.api_base,
        api_key_masked=mask_api_key(decrypt_api_key(model.encrypted_api_key)),
        model_name=model.model_name,
        params=model.params or {},
        is_default=model.is_default,
        is_active=model.is_active,
        created_at=model.created_at,
    ).model_dump())


@router.put("/models/{model_id}")
async def update_model(
    model_id: str,
    data: ModelConfigUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新模型配置"""
    result = await db.execute(
        select(ModelConfig).where(
            ModelConfig.id == model_id,
            ModelConfig.user_id == current_user.id,
        )
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="模型配置不存在")

    from ..core.security import decrypt_api_key
    # 更新字段
    if data.name is not None:
        model.name = data.name
    if data.api_base is not None:
        model.api_base = data.api_base
    if data.api_key is not None:
        model.encrypted_api_key = encrypt_api_key(data.api_key)
    if data.model_name is not None:
        model.model_name = data.model_name
    if data.params is not None:
        model.params = data.params
    if data.is_default is not None:
        if data.is_default:
            # 取消其他默认
            result = await db.execute(
                select(ModelConfig).where(
                    ModelConfig.user_id == current_user.id,
                    ModelConfig.is_default == True,
                )
            )
            for old_default in result.scalars().all():
                old_default.is_default = False
        model.is_default = data.is_default
    if data.is_active is not None:
        model.is_active = data.is_active

    await db.commit()
    await db.refresh(model)

    return APIResponse.success(data=ModelConfigResponse(
        id=model.id,
        user_id=model.user_id,
        name=model.name,
        provider=model.provider.value,
        api_base=model.api_base,
        api_key_masked=mask_api_key(decrypt_api_key(model.encrypted_api_key)),
        model_name=model.model_name,
        params=model.params or {},
        is_default=model.is_default,
        is_active=model.is_active,
        created_at=model.created_at,
    ).model_dump())


@router.delete("/models/{model_id}", status_code=204)
async def delete_model(
    model_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除模型配置"""
    result = await db.execute(
        select(ModelConfig).where(
            ModelConfig.id == model_id,
            ModelConfig.user_id == current_user.id,
        )
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="模型配置不存在")

    await db.delete(model)
    await db.commit()
    return APIResponse.success(message="删除成功")


@router.post("/models/{model_id}/test")
async def test_model(
    model_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """测试模型连通性"""
    result = await db.execute(
        select(ModelConfig).where(
            ModelConfig.id == model_id,
            ModelConfig.user_id == current_user.id,
        )
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="模型配置不存在")

    try:
        from langchain_openai import ChatOpenAI
        from ..core.security import decrypt_api_key

        llm = ChatOpenAI(
            model=model.model_name,
            api_key=decrypt_api_key(model.encrypted_api_key),
            base_url=model.api_base,
            max_tokens=10,
        )

        # 发送测试请求
        response = await llm.ainvoke("Hi")

        return APIResponse.success(data={"status": "ok", "message": "连接成功"})

    except Exception as e:
        return APIResponse.error(message=f"连接失败: {str(e)}")
