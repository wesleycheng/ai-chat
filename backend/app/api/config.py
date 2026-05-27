"""配置管理 API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from ..core import get_db, encrypt_api_key, mask_api_key
from ..models import User, ModelConfig
from ..schemas import (
    ModelConfigCreate, ModelConfigUpdate, ModelConfigResponse,
    SuccessResponse, ErrorResponse
)
from .auth import get_current_user

router = APIRouter(prefix="/config", tags=["配置"])


@router.get("/models", response_model=List[ModelConfigResponse])
async def list_models(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取模型配置列表"""
    result = await db.execute(
        select(ModelConfig)
        .where(ModelConfig.created_by == current_user.id)
        .order_by(ModelConfig.created_at.desc())
    )
    models = result.scalars().all()
    
    # 脱敏 API Key
    response = []
    for model in models:
        model_dict = {
            "id": model.id,
            "name": model.name,
            "provider": model.provider,
            "api_base": model.api_base,
            "api_key_masked": mask_api_key(decrypt_api_key(model.api_key_enc)),
            "model_name": model.model_name,
            "params": model.params or {},
            "is_default": model.is_default,
            "is_enabled": model.is_enabled,
            "created_at": model.created_at,
        }
        response.append(ModelConfigResponse(**model_dict))
    
    return response


@router.post("/models", response_model=ModelConfigResponse, status_code=201)
async def create_model(
    data: ModelConfigCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建模型配置"""
    # 如果设为默认，先取消其他默认
    if data.is_default:
        result = await db.execute(
            select(ModelConfig).where(ModelConfig.is_default == True)
        )
        for old_default in result.scalars().all():
            old_default.is_default = False
    
    model = ModelConfig(
        name=data.name,
        provider=data.provider,
        api_base=data.api_base,
        api_key_enc=encrypt_api_key(data.api_key),
        model_name=data.model_name,
        params=data.params,
        is_default=data.is_default,
        is_enabled=True,
        created_by=current_user.id,
    )
    db.add(model)
    await db.commit()
    await db.refresh(model)
    
    return ModelConfigResponse(
        id=model.id,
        name=model.name,
        provider=model.provider,
        api_base=model.api_base,
        api_key_masked=mask_api_key(data.api_key),
        model_name=model.model_name,
        params=model.params,
        is_default=model.is_default,
        is_enabled=model.is_enabled,
        created_at=model.created_at,
    )


@router.put("/models/{model_id}", response_model=ModelConfigResponse)
async def update_model(
    model_id: UUID,
    data: ModelConfigUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新模型配置"""
    result = await db.execute(
        select(ModelConfig).where(
            ModelConfig.id == model_id,
            ModelConfig.created_by == current_user.id,
        )
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="模型配置不存在")
    
    # 更新字段
    if data.name is not None:
        model.name = data.name
    if data.api_base is not None:
        model.api_base = data.api_base
    if data.api_key is not None:
        model.api_key_enc = encrypt_api_key(data.api_key)
    if data.model_name is not None:
        model.model_name = data.model_name
    if data.params is not None:
        model.params = data.params
    if data.is_default is not None:
        if data.is_default:
            # 取消其他默认
            result = await db.execute(
                select(ModelConfig).where(ModelConfig.is_default == True)
            )
            for old_default in result.scalars().all():
                old_default.is_default = False
        model.is_default = data.is_default
    if data.is_enabled is not None:
        model.is_enabled = data.is_enabled
    
    await db.commit()
    await db.refresh(model)
    
    return ModelConfigResponse(
        id=model.id,
        name=model.name,
        provider=model.provider,
        api_base=model.api_base,
        api_key_masked=mask_api_key(decrypt_api_key(model.api_key_enc)),
        model_name=model.model_name,
        params=model.params or {},
        is_default=model.is_default,
        is_enabled=model.is_enabled,
        created_at=model.created_at,
    )


@router.delete("/models/{model_id}", status_code=204)
async def delete_model(
    model_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除模型配置"""
    result = await db.execute(
        select(ModelConfig).where(
            ModelConfig.id == model_id,
            ModelConfig.created_by == current_user.id,
        )
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="模型配置不存在")
    
    await db.delete(model)
    await db.commit()


@router.post("/models/{model_id}/test")
async def test_model(
    model_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """测试模型连通性"""
    result = await db.execute(
        select(ModelConfig).where(
            ModelConfig.id == model_id,
            ModelConfig.created_by == current_user.id,
        )
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="模型配置不存在")
    
    try:
        from langchain_openai import ChatOpenAI
        from ..core import decrypt_api_key
        
        llm = ChatOpenAI(
            model=model.model_name,
            api_key=decrypt_api_key(model.api_key_enc),
            base_url=model.api_base,
            max_tokens=10,
        )
        
        # 发送测试请求
        response = await llm.ainvoke("Hi")
        
        return {"status": "ok", "message": "连接成功"}
    
    except Exception as e:
        return {"status": "error", "message": f"连接失败: {str(e)}"}


# 导入解密函数
from ..core.security import decrypt_api_key