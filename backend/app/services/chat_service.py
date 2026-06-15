"""聊天服务 - LangChain 集成"""
from typing import List, Optional, AsyncGenerator, Tuple
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage


from ..models import ModelConfig, Agent, Message
from ..core import decrypt_api_key

logger = logging.getLogger(__name__)


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
        
        # 记录Agent加载情况
        if self.agent:
            logger.info(f"[ChatService] Agent已加载: {self.agent.name}, system_prompt长度: {len(self.agent.system_prompt)}")
            logger.debug(f"[ChatService] system_prompt内容: {self.agent.system_prompt[:200]}...")
        else:
            logger.info("[ChatService] 未加载Agent，使用默认提示词")
    
    def _get_llm(self) -> ChatOpenAI:
        """获取 LLM 实例"""
        if self._llm is None:
            api_key = decrypt_api_key(self.model.encrypted_api_key)
            
            self._llm = ChatOpenAI(
                model=self.model.model_name,
                api_key=api_key,
                base_url=self.model.api_base,
                temperature=self.model.params.get("temperature", 0.7),
                max_tokens=self.model.params.get("max_tokens", 4096),
                streaming=True,
            )
        return self._llm
    
    async def _build_messages(
        self,
        user_input: str,
        history: List[Message],
        file_ids: Optional[List[UUID]] = None,
    ) -> List[BaseMessage]:
        """构建消息列表 - Agent角色和规则在这里被应用"""
        messages = []
        
        # ============================================
        # 核心修复：构建Agent系统提示词
        # ============================================
        
        # 基础系统提示词
        if self.agent:
            # Agent已定义的角色和规则
            system_prompt = self.agent.system_prompt
            
            # 强化Agent的角色定位（防止被用户引导偏离）
            role_enforcement = f"\n\n【重要】你是 {self.agent.name}，必须严格遵循上述角色定义和行为规则。"
            system_prompt += role_enforcement
            
            logger.info(f"[ChatService] 应用Agent [{self.agent.name}] 的system_prompt")
        else:
            system_prompt = "你是一个有帮助的AI助手。请根据用户的问题提供准确、有用的回答。"
        
        # ============================================
        # 添加文件内容（如果用户上传了文件）
        # ============================================
        file_contents = await self._get_file_contents(file_ids)
        
        if file_contents:
            file_section = "\n\n---\n\n【文件参考】以下是用户提供的文件内容，请结合这些内容准确回答用户的问题：\n\n"
            for filename, content in file_contents:
                file_section += f"### 📄 文件：{filename}\n```\n{content}\n```\n\n"
            system_prompt += file_section
            logger.info(f"[ChatService] 添加了 {len(file_contents)} 个文件内容到上下文")
        
        # ============================================
        # 将系统提示词作为第一条消息
        # ============================================
        messages.append(SystemMessage(content=system_prompt))
        
        # ============================================
        # 添加历史消息（最近20轮对话）
        # ============================================
        for msg in history[-20:]:
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                messages.append(AIMessage(content=msg.content))
            elif msg.role == "system":
                messages.append(SystemMessage(content=msg.content))
        
        # ============================================
        # 添加当前用户输入
        # ============================================
        messages.append(HumanMessage(content=user_input))
        
        logger.info(f"[ChatService] 构建消息完成，共 {len(messages)} 条消息（1条系统消息 + {len(history[-20:])} 条历史 + 1条用户输入）")
        
        return messages

    async def _get_file_contents(
        self,
        file_ids: Optional[List[UUID]] = None,
    ) -> List[Tuple[str, str]]:
        """获取文件内容"""
        if not file_ids:
            return []
        
        from ..models.models import File as DBFile, FileStatus
        from ..api.files import parse_file_content
        
        results = []
        for fid in file_ids:
            fid_str = str(fid)
            result = await self.db.execute(
                select(DBFile).where(DBFile.id == fid_str)
            )
            db_file = result.scalar_one_or_none()
            
            if not db_file:
                continue
            
            if db_file.file_path:
                # 如果已有解析内容直接用
                if db_file.content_text:
                    results.append((db_file.filename, db_file.content_text))
                elif db_file.parse_status == FileStatus.PENDING:
                    # 实时解析
                    content = await parse_file_content(db_file.file_path, db_file.file_ext)
                    if content:
                        db_file.content_text = content
                        db_file.parse_status = FileStatus.COMPLETED
                        await self.db.commit()
                        results.append((db_file.filename, content))
        
        return results
    
    async def stream_chat(
        self,
        user_input: str,
        history: List[Message],
        file_ids: Optional[List[UUID]] = None,
    ) -> AsyncGenerator[str, None]:
        """流式聊天"""
        agent_name = self.agent.name if self.agent else "默认助手"
        logger.info(f"[ChatService] 开始流式聊天，Agent: {agent_name}, 用户输入长度: {len(user_input)}")
        
        llm = self._get_llm()
        messages = await self._build_messages(user_input, history, file_ids)
        
        # 记录最终的系统提示词（用于调试）
        if messages and isinstance(messages[0], SystemMessage):
            logger.debug(f"[ChatService] 系统提示词（前200字符）: {messages[0].content[:200]}...")
        
        chunk_count = 0
        async for chunk in llm.astream(messages):
            if chunk.content:
                chunk_count += 1
                yield chunk.content
        
        logger.info(f"[ChatService] 流式聊天完成，Agent: {agent_name}，共返回 {chunk_count} 个文本块")
    
    async def chat(
        self,
        user_input: str,
        history: List[Message],
        file_ids: Optional[List[UUID]] = None,
    ) -> str:
        """非流式聊天"""
        agent_name = self.agent.name if self.agent else "默认助手"
        logger.info(f"[ChatService] 开始非流式聊天，Agent: {agent_name}, 用户输入长度: {len(user_input)}")
        
        llm = self._get_llm()
        messages = await self._build_messages(user_input, history, file_ids)
        
        response = await llm.ainvoke(messages)
        logger.info(f"[ChatService] 非流式聊天完成，Agent: {agent_name}，回复长度: {len(response.content)}")
        
        return response.content
