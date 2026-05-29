"""聊天 API - SSE 流式输出"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional
import json
import uuid

from ..core import get_db
from ..models import User, Conversation, Message, ModelConfig, Agent
from ..schemas import (
    ConversationCreate, ConversationUpdate, ConversationResponse,
    MessageResponse, ChatRequest
)
from .auth import get_current_user
from ..services.chat_service import ChatService

router = APIRouter(prefix="/conversations", tags=["对话"])


@router.get("", response_model=List[ConversationResponse])
async def list_conversations(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取会话列表"""
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(desc(Conversation.updated_at))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.post("", response_model=ConversationResponse, status_code=201)
async def create_conversation(
    data: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建新会话"""
    conversation = Conversation(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        title=data.title or "新对话",
        model_id=data.model_id,
        agent_id=data.agent_id,
    )
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    return conversation


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取会话详情"""
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="会话不存在")
    return conversation


@router.delete("/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除会话"""
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="会话不存在")

    await db.delete(conversation)
    await db.commit()


@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    conversation_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取会话消息历史"""
    # 验证会话所有权
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="会话不存在")

    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.post("/{conversation_id}/chat")
async def chat(
    conversation_id: str,
    data: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """发送消息（SSE 流式响应）"""
    # 验证会话所有权
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="会话不存在")

    # 获取模型配置
    model_id = data.model_id or conversation.model_id
    if not model_id:
        # 使用默认模型
        result = await db.execute(
            select(ModelConfig).where(
                ModelConfig.user_id == current_user.id,
                ModelConfig.is_default == True,
                ModelConfig.is_active == True,
            )
        )
        model = result.scalar_one_or_none()
    else:
        result = await db.execute(
            select(ModelConfig).where(
                ModelConfig.id == model_id,
                ModelConfig.user_id == current_user.id,
                ModelConfig.is_active == True,
            )
        )
        model = result.scalar_one_or_none()

    if not model:
        raise HTTPException(status_code=400, detail="没有可用的模型配置")

    # 获取 Agent（如果有）
    agent = None
    if conversation.agent_id:
        result = await db.execute(
            select(Agent).where(
                Agent.id == conversation.agent_id,
                Agent.is_active == True,
            )
        )
        agent = result.scalar_one_or_none()

    # 保存用户消息
    user_message = Message(
        id=str(uuid.uuid4()),
        conversation_id=conversation_id,
        role="user",
        content=data.content,
        file_ids=data.file_ids or [],
    )
    db.add(user_message)
    await db.commit()

    # 获取历史消息
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
        .limit(50)  # 限制上下文长度
    )
    history = list(result.scalars().all())

    # 创建聊天服务
    chat_service = ChatService(db=db, model=model, agent=agent)

    # 转换 file_ids 为 UUID 列表
    file_uuids = None
    if data.file_ids:
        file_uuids = [UUID(fid) for fid in data.file_ids]

    if data.stream:
        # SSE 流式响应
        async def generate():
            full_content = ""
            async for chunk in chat_service.stream_chat(data.content, history, file_uuids):
                full_content += chunk
                yield "data: " + json.dumps({"content": chunk}) + "\n\n"

            # 保存助手消息
            assistant_message = Message(
                id=str(uuid.uuid4()),
                conversation_id=conversation_id,
                role="assistant",
                content=full_content,
            )
            db.add(assistant_message)
            await db.commit()

            yield "data: " + json.dumps({"done": True}) + "\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
        )
    else:
        # 非流式响应
        content = await chat_service.chat(data.content, history, file_uuids)

        # 保存助手消息
        assistant_message = Message(
            id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            role="assistant",
            content=content,
        )
        db.add(assistant_message)
        await db.commit()

        return {"content": content}
