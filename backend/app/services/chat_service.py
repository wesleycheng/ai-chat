"""聊天服务 - LangChain 集成"""
from typing import List, Optional, AsyncGenerator
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage

from ..models import ModelConfig, Agent, Message
from ..core import decrypt_api_key


class ChatService:
    """聊天服务"""
    
    def __init__(
        self,
        db: AsyncSession,
        model: ModelConfig,
        agent: Optional[Agent] = None,
    ):
        self.db = db
        self.model = model
        self.agent = agent
        self._llm = None
    
    def _get_llm(self) -> ChatOpenAI:
        """获取 LLM 实例"""
        if self._llm is None:
            api_key = decrypt_api_key(self.model.api_key_enc)
            
            self._llm = ChatOpenAI(
                model=self.model.model_name,
                api_key=api_key,
                base_url=self.model.api_base,
                temperature=self.model.params.get("temperature", 0.7),
                max_tokens=self.model.params.get("max_tokens", 4096),
                streaming=True,
            )
        return self._llm
    
    def _build_messages(
        self,
        user_input: str,
        history: List[Message],
        file_ids: Optional[List[UUID]] = None,
    ) -> List[BaseMessage]:
        """构建消息列表"""
        messages = []
        
        # 系统提示词
        if self.agent:
            system_prompt = self.agent.system_prompt
        else:
            system_prompt = "你是一个有帮助的AI助手。"
        
        messages.append(SystemMessage(content=system_prompt))
        
        # 历史消息
        for msg in history[-20:]:  # 最近20轮
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                messages.append(AIMessage(content=msg.content))
            elif msg.role == "system":
                messages.append(SystemMessage(content=msg.content))
        
        # 当前用户输入
        messages.append(HumanMessage(content=user_input))
        
        return messages
    
    async def stream_chat(
        self,
        user_input: str,
        history: List[Message],
        file_ids: Optional[List[UUID]] = None,
    ) -> AsyncGenerator[str, None]:
        """流式聊天"""
        llm = self._get_llm()
        messages = self._build_messages(user_input, history, file_ids)
        
        async for chunk in llm.astream(messages):
            if chunk.content:
                yield chunk.content
    
    async def chat(
        self,
        user_input: str,
        history: List[Message],
        file_ids: Optional[List[UUID]] = None,
    ) -> str:
        """非流式聊天"""
        llm = self._get_llm()
        messages = self._build_messages(user_input, history, file_ids)
        
        response = await llm.ainvoke(messages)
        return response.content