"""聊天 API - SSE 流式输出"""
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional
import json
from uuid import UUID, uuid4
import structlog

from ..core import get_db
from ..core.exceptions import (
    NotFoundException,
    ValidationException,
    APIResponse,
)
from ..models import User, Conversation, Message, ModelConfig, Agent
from ..schemas import (
    ConversationCreate, ConversationUpdate, ConversationResponse,
    MessageResponse, ChatRequest
)
from .auth import get_current_user
from ..services.chat_service import ChatService

router = APIRouter(prefix="/conversations", tags=["对话"])
logger = structlog.get_logger()


@router.get("")
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
    conversations = result.scalars().all()
    return APIResponse.success(
        data={
            "items": [
                {
                    "id": c.id,
                    "title": c.title,
                    "model_id": c.model_id,
                    "agent_id": c.agent_id,
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                }
                for c in conversations
            ]
        }
    )


@router.post("", status_code=201)
async def create_conversation(
    data: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建新会话"""
    conversation = Conversation(
        id=str(uuid4()),
        user_id=current_user.id,
        title=data.title or "新对话",
        model_id=data.model_id,
        agent_id=data.agent_id,
    )
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    return APIResponse.success(
        data={
            "id": conversation.id,
            "title": conversation.title,
            "model_id": conversation.model_id,
            "agent_id": conversation.agent_id,
        },
        message="会话创建成功"
    )


@router.get("/{conversation_id}")
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
        raise NotFoundException(message="会话不存在", details={"conversation_id": conversation_id})
    return APIResponse.success(
        data={
            "id": conversation.id,
            "title": conversation.title,
            "model_id": conversation.model_id,
            "agent_id": conversation.agent_id,
        }
    )


@router.delete("/{conversation_id}")
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
        raise NotFoundException(message="会话不存在", details={"conversation_id": conversation_id})

    await db.delete(conversation)
    await db.commit()
    return APIResponse.success(message="会话已删除")


@router.get("/{conversation_id}/messages")
async def get_messages(
    conversation_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取会话消息历史"""
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
    )
    if not result.scalar_one_or_none():
        raise NotFoundException(message="会话不存在", details={"conversation_id": conversation_id})

    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
        .offset(skip)
        .limit(limit)
    )
    messages = result.scalars().all()
    return APIResponse.success(
        data={
            "items": [
                {
                    "id": m.id,
                    "role": m.role,
                    "content": m.content,
                    "created_at": m.created_at.isoformat() if m.created_at else None,
                }
                for m in messages
            ]
        }
    )


@router.post("/{conversation_id}/chat")
async def chat(
    conversation_id: str,
    data: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """发送消息（SSE 流式 / 非流式）"""
    # 验证会话所有权
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise NotFoundException(message="会话不存在", details={"conversation_id": conversation_id})

    # 获取模型配置
    model_id = data.model_id or conversation.model_id
    if not model_id:
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
        raise ValidationException(
            message="没有可用的模型配置",
            details={"hint": "请在设置中配置模型或设置默认模型"}
        )

    # 获取 Agent（优先使用请求中的 agent_id，其次使用会话的 agent_id）
    agent = None
    agent_id = data.agent_id or conversation.agent_id
    if agent_id:
        logger.info("[Chat] 查找Agent", agent_id=agent_id)
        result = await db.execute(
            select(Agent).where(
                Agent.id == agent_id,
                Agent.is_active == True,
            )
        )
        agent = result.scalar_one_or_none()
        if agent:
            logger.info("[Chat] Agent加载成功", name=agent.name)
        else:
            logger.warning("[Chat] Agent未找到或已禁用", agent_id=agent_id)
    else:
        logger.info("[Chat] 未指定Agent，使用默认行为")

    # 保存用户消息
    user_message = Message(
        id=str(uuid4()),
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
        .limit(50)
    )
    history = list(result.scalars().all())

    # 创建聊天服务
    chat_service = ChatService(db=db, model=model, agent=agent)

    # 转换 file_ids 为 UUID 列表
    file_uuids = None
    if data.file_ids:
        try:
            file_uuids = [UUID(fid) for fid in data.file_ids]
        except (ValueError, TypeError) as e:
            raise ValidationException(
                message="文件ID格式无效",
                details={"file_ids": data.file_ids, "error": str(e)}
            )

    if data.stream:
        # SSE 流式响应
        async def generate():
            full_content = ""
            try:
                async for chunk in chat_service.stream_chat(data.content, history, file_uuids):
                    full_content += chunk
                    yield "data: " + json.dumps({"content": chunk}, ensure_ascii=False) + "\n\n"

                # 保存助手消息（修复：role="assistant" 不是 "assitant"）
                assistant_message = Message(
                    id=str(uuid4()),
                    conversation_id=conversation_id,
                    role="assistant",
                    content=full_content,
                )
                db.add(assistant_message)
                await db.commit()

                yield "data: " + json.dumps({"done": True, "full_content": full_content}, ensure_ascii=False) + "\n\n"
            except Exception as e:
                logger.error("[Chat] 流式输出异常", exc_info=e)
                yield "data: " + json.dumps({"error": str(e)}, ensure_ascii=False) + "\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
        )
    else:
        # 非流式响应
        try:
            content = await chat_service.chat(data.content, history, file_uuids)
        except Exception as e:
            logger.error("[Chat] 聊天服务异常", exc_info=e)
            raise

        # 保存助手消息（修复：role="assistant"）
        assistant_message = Message(
            id=str(uuid4()),
            conversation_id=conversation_id,
            role="assistant",
            content=content,
        )
        db.add(assistant_message)
        await db.commit()

        return APIResponse.success(
            data={"content": content},
            message="回复完成"
        )
