"""Agent API"""
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from ..core import get_db
from ..models import User, Agent
from ..schemas import AgentCreate, AgentUpdate, AgentResponse
from .auth import get_current_user

router = APIRouter(prefix="/agents", tags=["Agent"])


@router.get("", response_model=List[AgentResponse])
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
    return result.scalars().all()


@router.post("", response_model=AgentResponse, status_code=201)
async def create_agent(
    data: AgentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建 Agent"""
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
    return agent


@router.get("/{agent_id}", response_model=AgentResponse)
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
        raise HTTPException(status_code=404, detail="Agent 不存在")
    return agent


@router.put("/{agent_id}", response_model=AgentResponse)
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
        raise HTTPException(status_code=404, detail="Agent 不存在或无权限修改")

    # 更新字段
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(agent, field, value)

    await db.commit()
    await db.refresh(agent)
    return agent


@router.delete("/{agent_id}", status_code=204)
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
        raise HTTPException(status_code=404, detail="Agent 不存在或无权限删除")

    await db.delete(agent)
    await db.commit()


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
        raise HTTPException(status_code=404, detail="Agent 不存在")

    return {
        "status": "ok",
        "message": "Agent 测试功能待实现",
        "agent_name": agent.name,
    }
