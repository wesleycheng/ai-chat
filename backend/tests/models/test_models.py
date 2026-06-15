"""
测试数据库模型
"""
import pytest
import uuid
from datetime import datetime


class TestUserModel:
    """User 模型测试"""

    def test_create_user(self, test_db):
        """测试创建用户"""
        from app.models import User
        
        user = User(
            id=str(uuid.uuid4()),
            username="testuser",
            email="<EMAIL_REMOVED>",
            password_hash="hashed_password",
        )
        
        test_db.add(user)
        test_db.commit()
        
        # 查询验证
        from sqlalchemy import select
        result = test_db.execute(select(User).where(User.username == "testuser"))
        saved_user = result.scalar_one()
        
        assert saved_user.id == user.id
        assert saved_user.username == "testuser"
        assert saved_user.email == "<EMAIL_REMOVED>"
        assert saved_user.is_active == True
        assert isinstance(saved_user.created_at, datetime)


class TestModelConfig:
    """ModelConfig 模型测试"""

    def test_create_model_config(self, test_db):
        """测试创建模型配置"""
        from app.models import ModelConfig, User
        
        # 先创建用户
        user = User(
            id=str(uuid.uuid4()),
            username="configuser",
            email="<EMAIL_REMOVED>",
            password_hash="hashed",
        )
        test_db.add(user)
        test_db.commit()
        
        # 创建模型配置
        model_config = ModelConfig(
            id=str(uuid.uuid4()),
            user_id=user.id,
            name="Test GPT-3.5",
            provider="openai",
            api_base="https://api.openai.com/v1",
            encrypted_api_key="encrypted_key",
            model_name="gpt-3.5-turbo",
            is_default=True,
            is_active=True,
        )
        test_db.add(model_config)
        test_db.commit()
        
        # 查询验证
        from sqlalchemy import select
        result = test_db.execute(
            select(ModelConfig).where(ModelConfig.name == "Test GPT-3.5")
        )
        saved_config = result.scalar_one()
        
        assert saved_config.user_id == user.id
        assert saved_config.provider == "openai"
        assert saved_config.is_default == True
        assert saved_config.is_active == True


class TestConversation:
    """Conversation 模型测试"""

    def test_create_conversation(self, test_db):
        """测试创建会话"""
        from app.models import Conversation, User
        
        # 先创建用户
        user = User(
            id=str(uuid.uuid4()),
            username="convuser",
            email="<EMAIL_REMOVED>",
            password_hash="hashed",
        )
        test_db.add(user)
        test_db.commit()
        
        # 创建会话
        conversation = Conversation(
            id=str(uuid.uuid4()),
            user_id=user.id,
            title="Test Conversation",
        )
        test_db.add(conversation)
        test_db.commit()
        
        # 查询验证
        from sqlalchemy import select
        result = test_db.execute(
            select(Conversation).where(Conversation.title == "Test Conversation")
        )
        saved_conv = result.scalar_one()
        
        assert saved_conv.user_id == user.id
        assert saved_conv.title == "Test Conversation"
        assert isinstance(saved_conv.created_at, datetime)
        assert isinstance(saved_conv.updated_at, datetime)


class TestMessage:
    """Message 模型测试"""

    def test_create_message(self, test_db):
        """测试创建消息"""
        from app.models import Message, Conversation, User
        
        # 创建用户和会话
        user = User(
            id=str(uuid.uuid4()),
            username="msguser",
            email="<EMAIL_REMOVED>",
            password_hash="hashed",
        )
        test_db.add(user)
        test_db.commit()
        
        conversation = Conversation(
            id=str(uuid.uuid4()),
            user_id=user.id,
            title="Message Test",
        )
        test_db.add(conversation)
        test_db.commit()
        
        # 创建消息
        message = Message(
            id=str(uuid.uuid4()),
            conversation_id=conversation.id,
            role="user",
            content="Hello, this is a test message!",
        )
        test_db.add(message)
        test_db.commit()
        
        # 查询验证
        from sqlalchemy import select
        result = test_db.execute(
            select(Message).where(Message.role == "user")
        )
        saved_msg = result.scalar_one()
        
        assert saved_msg.conversation_id == conversation.id
        assert saved_msg.role == "user"
        assert saved_msg.content == "Hello, this is a test message!"
        assert isinstance(saved_msg.created_at, datetime)


class TestAgent:
    """Agent 模型测试"""

    def test_create_agent(self, test_db):
        """测试创建 Agent"""
        from app.models import Agent, User
        
        # 先创建用户
        user = User(
            id=str(uuid.uuid4()),
            username="agentuser",
            email="<EMAIL_REMOVED>",
            password_hash="hashed",
        )
        test_db.add(user)
        test_db.commit()
        
        # 创建 Agent
        agent = Agent(
            id=str(uuid.uuid4()),
            user_id=user.id,
            name="Test Agent",
            description="A test agent",
            system_prompt="You are a helpful assistant.",
            is_active=True,
        )
        test_db.add(agent)
        test_db.commit()
        
        # 查询验证
        from sqlalchemy import select
        result = test_db.execute(
            select(Agent).where(Agent.name == "Test Agent")
        )
        saved_agent = result.scalar_one()
        
        assert saved_agent.user_id == user.id
        assert saved_agent.name == "Test Agent"
        assert saved_agent.is_active == True
        assert saved_agent.system_prompt == "You are a helpful assistant."


class TestFileRecord:
    """FileRecord 模型测试"""

    def test_create_file_record(self, test_db):
        """测试创建文件记录"""
        from app.models import FileRecord, User
        
        # 先创建用户
        user = User(
            id=str(uuid.uuid4()),
            username="fileuser",
            email="<EMAIL_REMOVED>",
            password_hash="hashed",
        )
        test_db.add(user)
        test_db.commit()
        
        # 创建文件记录
        file_record = FileRecord(
            id=str(uuid.uuid4()),
            user_id=user.id,
            filename="test.pdf",
            file_type="application/pdf",
            file_size=1024,
            file_path="/uploads/test.pdf",
            content_text="This is the extracted text content.",
            parse_status="completed",
        )
        test_db.add(file_record)
        test_db.commit()
        
        # 查询验证
        from sqlalchemy import select
        result = test_db.execute(
            select(FileRecord).where(FileRecord.filename == "test.pdf")
        )
        saved_file = result.scalar_one()
        
        assert saved_file.user_id == user.id
        assert saved_file.file_type == "application/pdf"
        assert saved_file.parse_status == "completed"
        assert saved_file.content_text == "This is the extracted text content."
