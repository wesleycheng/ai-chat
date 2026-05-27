"""Pydantic 数据模式"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


# ============ 认证 ============

class UserLogin(BaseModel):
    username: str
    password: str


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    email: EmailStr
    password: str = Field(..., min_length=6)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    refresh_token: str


# ============ 用户 ============

class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    role: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ 模型配置 ============

class ModelConfigCreate(BaseModel):
    name: str = Field(..., max_length=128)
    provider: str = Field(..., pattern="^(deepseek|openai|ollama|custom)$")
    api_base: str
    api_key: str
    model_name: str = Field(..., max_length=128)
    params: Dict[str, Any] = Field(default_factory=lambda: {"temperature": 0.7, "max_tokens": 4096})
    is_default: bool = False


class ModelConfigUpdate(BaseModel):
    name: Optional[str] = None
    api_base: Optional[str] = None
    api_key: Optional[str] = None
    model_name: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    is_default: Optional[bool] = None
    is_enabled: Optional[bool] = None


class ModelConfigResponse(BaseModel):
    id: UUID
    name: str
    provider: str
    api_base: str
    api_key_masked: str  # 脱敏显示
    model_name: str
    params: Dict[str, Any]
    is_default: bool
    is_enabled: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ 会话 ============

class ConversationCreate(BaseModel):
    title: Optional[str] = None
    model_id: Optional[UUID] = None
    agent_id: Optional[UUID] = None


class ConversationUpdate(BaseModel):
    title: Optional[str] = None


class ConversationResponse(BaseModel):
    id: UUID
    title: Optional[str]
    model_id: Optional[UUID]
    agent_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============ 消息 ============

class MessageCreate(BaseModel):
    content: str
    file_ids: Optional[List[UUID]] = None


class MessageResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    role: str
    content: str
    token_count: Optional[int]
    metadata: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ 聊天请求 ============

class ChatRequest(BaseModel):
    content: str
    model_id: Optional[UUID] = None
    agent_id: Optional[UUID] = None
    file_ids: Optional[List[UUID]] = None
    stream: bool = True


# ============ 文件 ============

class FileResponse(BaseModel):
    id: UUID
    filename: str
    file_size: Optional[int]
    mime_type: Optional[str]
    parse_status: str
    chunk_count: int
    error_message: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ Agent ============

class AgentCreate(BaseModel):
    name: str = Field(..., max_length=128)
    description: Optional[str] = None
    system_prompt: str
    model_id: Optional[UUID] = None
    tools: List[str] = Field(default_factory=list)
    kb_file_ids: List[UUID] = Field(default_factory=list)
    max_iterations: int = 10
    memory_type: str = "buffer"
    is_public: bool = False


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    model_id: Optional[UUID] = None
    tools: Optional[List[str]] = None
    kb_file_ids: Optional[List[UUID]] = None
    max_iterations: Optional[int] = None
    memory_type: Optional[str] = None
    is_public: Optional[bool] = None


class AgentResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    system_prompt: str
    model_id: Optional[UUID]
    tools: List[str]
    kb_file_ids: List[UUID]
    max_iterations: int
    memory_type: str
    is_public: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============ 通用响应 ============

class SuccessResponse(BaseModel):
    status: str = "ok"
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    detail: Optional[str] = None