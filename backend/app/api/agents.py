"""Agent API"""
import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from ..core import get_db
from ..core.exceptions import NotFoundException, ForbiddenException, ValidationException, APIResponse
from ..models import User, Agent
from ..schemas import AgentCreate, AgentUpdate, AgentResponse
from .auth import get_current_user

router = APIRouter(prefix="/agents", tags=["Agent"])


@router.get("")
async def list_agents(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取 Agent 列表"""
    result = await db.execute(
        select(Agent)
        .where(Agent.user_id == current_user.id)
        .order_by(Agent.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    agents = result.scalars().all()
    
    return APIResponse.success(
        data={
            "items": [
                {
                    "id": a.id,
                    "name": a.name,
                    "description": a.description,
                    "model_id": a.model_id,
                    "is_active": a.is_active,
                    "created_at": a.created_at.isoformat() if a.created_at else None,
                }
                for a in agents
            ]
        }
    )


@router.post("", status_code=201)
async def create_agent(
    data: AgentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建 Agent"""
    if not data.name or len(data.name.strip()) < 2:
        raise ValidationException(
            message="Agent 名称不能少于2个字符",
            details={"field": "name", "min_length": 2}
        )
    
    agent = Agent(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        name=data.name,
        description=data.description,
        system_prompt=data.system_prompt,
        model_id=data.model_id or None,
        tools=data.tools or [],
        is_active=True,
    )
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    
    return APIResponse.success(
        data={
            "id": agent.id,
            "name": agent.name,
            "description": agent.description,
            "system_prompt": agent.system_prompt,
            "model_id": agent.model_id,
            "tools": agent.tools,
            "is_active": agent.is_active,
        },
        message="Agent 创建成功"
    )


@router.get("/{agent_id}")
async def get_agent(
    agent_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取 Agent 详情"""
    result = await db.execute(
        select(Agent).where(
            Agent.id == agent_id,
            Agent.user_id == current_user.id,
        )
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise NotFoundException(
            message="Agent 不存在",
            details={"agent_id": agent_id}
        )
    
    return APIResponse.success(
        data={
            "id": agent.id,
            "name": agent.name,
            "description": agent.description,
            "system_prompt": agent.system_prompt,
            "model_id": agent.model_id,
            "tools": agent.tools,
            "is_active": agent.is_active,
        }
    )


@router.put("/{agent_id}")
async def update_agent(
    agent_id: str,
    data: AgentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新 Agent"""
    result = await db.execute(
        select(Agent).where(
            Agent.id == agent_id,
            Agent.user_id == current_user.id,
        )
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise NotFoundException(
            message="Agent 不存在或无权限修改",
            details={"agent_id": agent_id}
        )

    # 更新字段
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(agent, field, value)

    await db.commit()
    await db.refresh(agent)
    
    return APIResponse.success(
        data={
            "id": agent.id,
            "name": agent.name,
            "description": agent.description,
            "system_prompt": agent.system_prompt,
            "model_id": agent.model_id,
            "tools": agent.tools,
            "is_active": agent.is_active,
        },
        message="Agent 更新成功"
    )


@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除 Agent"""
    result = await db.execute(
        select(Agent).where(
            Agent.id == agent_id,
            Agent.user_id == current_user.id,
        )
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise NotFoundException(
            message="Agent 不存在或无权限删除",
            details={"agent_id": agent_id}
        )

    await db.delete(agent)
    await db.commit()
    
    return APIResponse.success(message="Agent 删除成功")


@router.post("/{agent_id}/test")
async def test_agent(
    agent_id: str,
    message: str = Query(..., min_length=1),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """测试 Agent"""
    result = await db.execute(
        select(Agent).where(
            Agent.id == agent_id,
            Agent.user_id == current_user.id,
        )
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise NotFoundException(
            message="Agent 不存在",
            details={"agent_id": agent_id}
        )

    return APIResponse.success(
        data={
            "agent_id": agent.id,
            "agent_name": agent.name,
            "status": "ready",
        },
        message="Agent 测试功能待实现"
    )
