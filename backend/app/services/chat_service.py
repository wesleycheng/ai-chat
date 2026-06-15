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
            logger.info(f"[ChatService] 检测到用户上传了 {len(file_contents)} 个文件，开始整合到系统提示词")
            
            # 构建更结构化的文件内容部分
            file_section = "\n\n" + "="*60 + "\n"
            file_section += "📎 【用户上传的文件内容】\n"
            file_section += "="*60 + "\n\n"
            file_section += "你必须仔细阅读以下文件内容，并结合它们来回答用户的问题。\n"
            file_section += "如果文件内容与问题相关，请引用具体的文字和数据。\n\n"
            
            for idx, (filename, content) in enumerate(file_contents, 1):
                # 截断过长的文件内容（保留前8000个字符）
                truncated_content = content[:8000] + "...（内容已截断）" if len(content) > 8000 else content
                
                file_section += f"\n【文件 {idx}】{filename}\n"
                file_section += "-" * 40 + "\n"
                file_section += f"{truncated_content}\n"
                file_section += "-" * 40 + "\n\n"
            
            file_section += "="*60 + "\n"
            file_section += "📌 重要提示：\n"
            file_section += "- 请结合以上文件内容准确回答用户的问题\n"
            file_section += "- 如果文件中有相关数据或信息，请引用它们\n"
            file_section += "- 如果文件中没有相关信息，请基于通用知识回答\n"
            file_section += "="*60 + "\n"
            
            system_prompt += file_section
            logger.info(f"[ChatService] 成功添加 {len(file_contents)} 个文件内容到上下文，总长度: {len(file_section)} 字符")
        
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
            logger.debug("[ChatService] 未提供file_ids，跳过文件处理")
            return []
        
        logger.info(f"[ChatService] 开始处理 {len(file_ids)} 个文件")
        
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
                logger.warning(f"[ChatService] 文件未找到，file_id: {fid_str}")
                continue
            
            logger.info(f"[ChatService] 加载文件: {db_file.filename} ({db_file.file_ext})")
            
            if db_file.file_path:
                # 如果已有解析内容直接用
                if db_file.content_text:
                    content_length = len(db_file.content_text)
                    logger.info(f"[ChatService] 使用已缓存的文件内容，长度: {content_length} 字符")
                    results.append((db_file.filename, db_file.content_text))
                elif db_file.parse_status == FileStatus.PENDING:
                    # 实时解析
                    logger.info(f"[ChatService] 实时解析文件: {db_file.filename}")
                    content = await parse_file_content(db_file.file_path, db_file.file_ext)
                    if content:
                        db_file.content_text = content
                        db_file.parse_status = FileStatus.COMPLETED
                        await self.db.commit()
                        results.append((db_file.filename, content))
                        logger.info(f"[ChatService] 文件解析成功: {db_file.filename}, 内容长度: {len(content)} 字符")
        
        if results:
            logger.info(f"[ChatService] 文件处理完成，共 {len(results)} 个文件加载到上下文")
        else:
            logger.warning("[ChatService] 文件处理完成，但未能加载任何文件内容")
        
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
