from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from enum import Enum


# === 通用 ===
class SuccessResponse(BaseModel):
    message: str
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    detail: str


class MessageResponse(BaseModel):
    message: str


# === 用户 ===
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)


UserRegister = UserCreate


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    id: str
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse | None = None


class TokenRefresh(BaseModel):
    refresh_token: str


# === 模型配置 ===
class ModelProvider(str, Enum):
    DEEPSEEK = "deepseek"
    OPENAI = "openai"
    OLLAMA = "ollama"
    ANTHROPIC = "anthropic"
    CUSTOM = "custom"


class ModelConfigCreate(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    name: str = Field(..., min_length=1, max_length=100)
    provider: ModelProvider
    api_base: str
    api_key: str
    model_name: str = Field(..., alias="model_name")
    params: Optional[dict] = {}
    is_default: bool = False


class ModelConfigUpdate(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    name: Optional[str] = None
    provider: Optional[ModelProvider] = None
    api_base: Optional[str] = None
    api_key: Optional[str] = None
    model_name: Optional[str] = Field(None, alias="model_name")
    params: Optional[dict] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None


class ModelConfigResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    id: str
    user_id: str
    name: str
    provider: str
    api_base: str
    api_key_masked: str
    model_name: str = Field(..., alias="model_name")
    params: dict
    is_default: bool
    is_active: bool
    created_at: datetime


# === 对话 ===
class ConversationCreate(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    title: Optional[str] = None
    model_id: Optional[str] = Field(None, alias="model_id")
    agent_id: Optional[str] = None


class ConversationUpdate(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    title: Optional[str] = None
    model_id: Optional[str] = Field(None, alias="model_id")
    agent_id: Optional[str] = None


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    id: str
    user_id: str
    title: Optional[str]
    model_id: Optional[str] = Field(None, alias="model_id")
    agent_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class ConversationListResponse(BaseModel):
    items: List[ConversationResponse]
    total: int


class MessageCreate(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    content: str = Field(..., min_length=1)
    file_ids: Optional[List[str]] = []
    model_id: Optional[str] = Field(None, alias="model_id")


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    id: str
    conversation_id: str
    role: str
    content: str
    file_ids: List[str]
    token_count: int
    created_at: datetime


class MessageListResponse(BaseModel):
    items: List[MessageResponse]
    total: int


class ChatRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    content: str = Field(..., min_length=1)
    file_ids: Optional[List[str]] = []
    model_id: Optional[str] = Field(None, alias="model_id")
    stream: bool = False


class ChatResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    id: str
    conversation_id: str
    role: str
    content: str
    created_at: datetime


# === 文件 ===
class FileStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class FileCreate(BaseModel):
    filename: str
    file_ext: Optional[str] = None
    file_size: Optional[int] = None


class FileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    id: str
    user_id: str
    filename: str
    file_ext: Optional[str]
    file_size: Optional[int]
    parse_status: str
    parse_error: Optional[str]
    content_text: Optional[str]
    created_at: datetime


class FileListResponse(BaseModel):
    items: List[FileResponse]
    total: int


class FileStatusResponse(BaseModel):
    id: str
    filename: str
    parse_status: str
    parse_error: Optional[str]


# === Agent ===
class AgentCreate(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    system_prompt: str
    model_id: Optional[str] = Field(None, alias="model_id")
    tools: Optional[List[str]] = []


class AgentUpdate(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    name: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    model_id: Optional[str] = Field(None, alias="model_id")
    tools: Optional[List[str]] = None
    is_active: Optional[bool] = None


class AgentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    id: str
    user_id: str
    name: str
    description: Optional[str]
    system_prompt: str
    model_id: Optional[str] = Field(None, alias="model_id")
    tools: List[str]
    is_active: bool
    created_at: datetime


class AgentListResponse(BaseModel):
    items: List[AgentResponse]
    total: int


# === 使用统计 ===
class UsageStatsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    id: str
    user_id: str
    model_id: Optional[str] = Field(None, alias="model_id")
    conversation_id: Optional[str] = None
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost: float
    created_at: datetime
