"""数据库 ORM 模型"""
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import Column, String, Text, Boolean, Integer, BigInteger, Numeric, DateTime, ForeignKey, ARRAY, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from ..core.database import Base


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    username = Column(String(64), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(Text, nullable=False)
    role = Column(String(20), default="user")  # admin | user
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    files = relationship("File", back_populates="user", cascade="all, delete-orphan")
    agents = relationship("Agent", back_populates="creator", cascade="all, delete-orphan")
    model_configs = relationship("ModelConfig", back_populates="creator", cascade="all, delete-orphan")


class ModelConfig(Base):
    """模型配置表"""
    __tablename__ = "model_configs"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(128), nullable=False)
    provider = Column(String(32), nullable=False)  # deepseek | openai | ollama | custom
    api_base = Column(Text, nullable=False)
    api_key_enc = Column(Text, nullable=False)  # 加密存储
    model_name = Column(String(128), nullable=False)
    params = Column(JSON, default=dict)  # temperature, max_tokens 等
    is_default = Column(Boolean, default=False)
    is_enabled = Column(Boolean, default=True)
    created_by = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    creator = relationship("User", back_populates="model_configs")
    conversations = relationship("Conversation", back_populates="model")
    agents = relationship("Agent", back_populates="model")


class Conversation(Base):
    """会话表"""
    __tablename__ = "conversations"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_id = Column(PG_UUID(as_uuid=True), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(256), nullable=True)
    model_id = Column(PG_UUID(as_uuid=True), ForeignKey("model_configs.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="conversations")
    agent = relationship("Agent", back_populates="conversations")
    model = relationship("ModelConfig", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.created_at")


class Message(Base):
    """消息表"""
    __tablename__ = "messages"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    conversation_id = Column(PG_UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(16), nullable=False)  # user | assistant | system | tool
    content = Column(Text, nullable=False)
    token_count = Column(Integer, nullable=True)
    metadata = Column(JSON, default=dict)  # tool_calls, file_refs 等
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # 关系
    conversation = relationship("Conversation", back_populates="messages")


class File(Base):
    """文件表"""
    __tablename__ = "files"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(Text, nullable=False)
    file_path = Column(Text, nullable=False)
    file_size = Column(BigInteger, nullable=True)
    mime_type = Column(String(128), nullable=True)
    parse_status = Column(String(16), default="pending")  # pending | ready | failed
    chunk_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="files")


class Agent(Base):
    """Agent 表"""
    __tablename__ = "agents"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    system_prompt = Column(Text, nullable=False)
    model_id = Column(PG_UUID(as_uuid=True), ForeignKey("model_configs.id", ondelete="SET NULL"), nullable=True)
    tools = Column(ARRAY(Text), default=list)  # 启用的工具列表
    kb_file_ids = Column(ARRAY(PG_UUID(as_uuid=True)), default=list)  # 关联的知识库文件
    max_iterations = Column(Integer, default=10)
    memory_type = Column(String(32), default="buffer")  # buffer | summary | none
    is_public = Column(Boolean, default=False)
    created_by = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    creator = relationship("User", back_populates="agents")
    model = relationship("ModelConfig", back_populates="agents")
    conversations = relationship("Conversation", back_populates="agent")


class UsageStats(Base):
    """Token 用量统计表"""
    __tablename__ = "usage_stats"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    conversation_id = Column(PG_UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True)
    model_id = Column(PG_UUID(as_uuid=True), ForeignKey("model_configs.id", ondelete="SET NULL"), nullable=True)
    agent_id = Column(PG_UUID(as_uuid=True), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True)
    prompt_tokens = Column(Integer, nullable=False, default=0)
    completion_tokens = Column(Integer, nullable=False, default=0)
    total_tokens = Column(Integer, nullable=False, default=0)  # 生成列在应用层计算
    cost_cents = Column(Numeric(10, 4), default=0)  # 成本（分）
    created_at = Column(DateTime, default=datetime.utcnow, index=True)