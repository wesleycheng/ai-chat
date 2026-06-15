# AI Chat 技术方案文档

> 版本：v1.0 · 日期：2026-05-27

---

## 1. 项目概述

构建一个企业级多功能 AI Chat 平台，核心能力包括：

- **多模型对话**：切换 DeepSeek、OpenAI、Ollama 本地模型等
- **文件分析**：上传 PDF / Word / Excel / 图片，AI 解析提取内容
- **自定义 Agent**：可视化创建、编排、管理 AI Agent
- **配置管理**：模型参数、Agent 配置、系统提示词统一管理

---

## 2. 技术栈选型

### 2.1 后端

| 层次 | 技术 | 理由 |
|---|---|---|
| 运行时 | **Python 3.12** | 生态最丰富，AI/ML 库原生支持 |
| Web 框架 | **FastAPI** | 异步、自带 OpenAPI 文档、类型安全 |
| AI 集成 | **LangChain / LangGraph** | 统一多模型调用、Agent 编排、RAG |
| 流式输出 | **SSE + WebSocket** | SSE 用于流式 token 输出；WebSocket 用于双向通信（取消生成、Agent 中间状态推送） |
| 异步任务 | **arq (轻量) 或 Celery** | 文件解析异步处理；arq 基于 asyncio + Redis，比 Celery 轻量且与 FastAPI 异步模型一致 |
| 文件解析 | **PyMuPDF, python-docx, openpyxl, Pillow** | 多格式文件内容提取 |
| 向量检索 | **ChromaDB (本地 / 免费)** | 文件内容 Embedding 存储与语义检索 |
| 认证 | **python-jose + passlib** | JWT 无状态认证 |
| 限流 | **slowapi** | 基于 IP / 用户的 Rate Limiting，防止 AI API 调用滥用 |
| 可观测性 | **structlog + OpenTelemetry** | 结构化日志、请求链路追踪、指标采集 |

### 2.2 前端

| 层次 | 技术 | 理由 |
|---|---|---|
| 框架 | **React 18 + TypeScript** | 生态成熟，类型安全 |
| 构建 | **Vite** | 极速 HMR，开发体验好 |
| 样式 | **Tailwind CSS v4 + shadcn/ui** | 设计系统一致，组件丰富 |
| 状态管理 | **Zustand** | 轻量，适合中型应用 |
| 数据请求 | **TanStack Query v5** | 缓存、重试、loading 状态管理 |
| 流式渲染 | **自定义 SSE hook** | 逐 token 渲染 AI 回复 |
| Markdown | **streamdown** | 流式 Markdown 渲染 |
| 路由 | **React Router v6** | 标准 SPA 路由 |
| 国际化 | **react-i18next** | 中英文切换 |

### 2.3 数据库（免费方案）

| 用途 | 技术 | 理由 |
|---|---|---|
| 主数据库 | **PostgreSQL 16 (Docker)** | 开源免费，关系型，事务可靠 |
| 缓存 / 消息队列 | **Redis 7 (Docker)** | Session 缓存、Celery Broker |
| 向量数据库 | **ChromaDB** | 纯 Python，本地运行，免费 |
| 本地开发备选 | **SQLite** | 零配置，开发调试用 |

> **云端免费备选**：Supabase (PostgreSQL) 免费套餐 500MB；Upstash Redis 免费套餐 10K req/day。

---

## 3. 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                      React 前端                          │
│   Chat UI │ File Upload │ Agent Builder │ Config Center  │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTPS / SSE
┌──────────────────────▼──────────────────────────────────┐
│                   FastAPI 网关层                          │
│  /api/chat  /api/files  /api/agents  /api/config        │
│                  JWT 认证 · 请求校验                      │
└─────┬────────────┬──────────────┬───────────────────────┘
      │            │              │
┌─────▼──┐  ┌──────▼──────┐  ┌───▼──────────────────────┐
│ Chat   │  │  File       │  │  Agent                    │
│ Service│  │  Service    │  │  Service (LangGraph)       │
│        │  │  (Celery)   │  │                           │
└─────┬──┘  └──────┬──────┘  └───┬──────────────────────┘
      │            │              │
┌─────▼────────────▼──────────────▼──────────────────────┐
│              LangChain / LangGraph 核心层                 │
│   Model Router │ Tool Registry │ Memory │ RAG Chain     │
└────┬───────────────────────────┬────────────────────────┘
     │                           │
┌────▼───────┐           ┌───────▼──────────────────────┐
│  AI 模型层  │           │          数据层               │
│ DeepSeek   │           │  PostgreSQL (主数据)           │
│ OpenAI     │           │  ChromaDB   (向量)             │
│ Ollama     │           │  Redis      (缓存/队列)        │
└────────────┘           └──────────────────────────────┘
```

---

## 4. 核心模块详设

### 4.1 多模型对话

**模型路由设计**

```python
# 统一模型配置结构
class ModelConfig(BaseModel):
    id: str                    # 唯一标识，如 "deepseek-chat"
    provider: str              # "deepseek" | "openai" | "ollama" | "custom"
    api_base: str              # API 端点
    api_key: str               # 加密存储
    model_name: str            # 实际模型名
    max_tokens: int = 4096
    temperature: float = 0.7
    is_enabled: bool = True
```

**流式输出流程**

```
常规对话（SSE）:
  前端 EventSource 连接 → FastAPI EventSourceResponse
    → LangChain ChatModel.astream()
      → 逐 token yield → 前端 streamdown 渲染

Agent 交互（WebSocket）:
  前端 ws 连接 → FastAPI WebSocket endpoint
    → Agent 执行中推送工具调用状态、中间结果
    → 支持客户端发送 cancel 指令中止生成
```

**上下文管理策略**

| 策略 | 适用场景 | 说明 |
|---|---|---|
| Sliding Window | 日常对话 | 保留最近 N 轮消息，token 超限时裁剪最早消息 |
| Summary Memory | 长会话 | 超过阈值后，用 LLM 将历史摘要为一段 summary |
| Token Budget | 全局 | 系统提示词 + 历史 + 用户输入不超过模型 max_context 的 85% |

**支持模型列表（开箱即用）**

| Provider | 模型 | 费用 |
|---|---|---|
| DeepSeek | deepseek-chat, deepseek-reasoner | 按 token 计费（价格极低） |
| OpenAI 兼容 | 任意 | 自配 API Key |
| Ollama | llama3, qwen2.5, mistral 等 | **完全免费** (本地) |

---

### 4.2 文件分析

**支持格式**：PDF · DOCX · XLSX · CSV · TXT · PNG/JPG（OCR）

**处理流程**

```
上传文件 → 存储到本地 /uploads 目录
  → Celery Task 异步处理
    → 按格式解析提取纯文本
    → 文本分块 (RecursiveCharacterTextSplitter)
    → Embedding (DeepSeek / OpenAI Embeddings)
    → 存入 ChromaDB (collection = file_id)
  → 对话时 RAG 检索相关段落注入 context
```

**API 设计**

```
POST /api/files/upload          → 上传文件，返回 file_id
GET  /api/files/{file_id}/status → 解析状态 (pending/ready/failed)
POST /api/chat                  → 携带 file_ids 发起文件对话
DELETE /api/files/{file_id}     → 删除文件及向量
```

---

### 4.3 自定义 Agent

**Agent 数据模型**

```python
class AgentConfig(BaseModel):
    id: str
    name: str
    description: str
    system_prompt: str         # 系统提示词
    model_id: str              # 绑定的模型
    tools: list[str]           # 启用的工具列表
    knowledge_base_ids: list[str]  # 绑定的知识库
    max_iterations: int = 10
    memory_type: str = "buffer"  # buffer | summary | none
    is_public: bool = False
```

**内置工具箱**

| 工具 | 说明 |
|---|---|
| `web_search` | Tavily / DuckDuckGo 搜索（免费） |
| `code_executor` | Python 沙箱执行代码（Docker 容器隔离，限时 30s，禁网络/文件系统访问） |
| `file_reader` | 读取已上传文件 |
| `calculator` | 数学计算 |
| `http_request` | 调用自定义 API |
| `datetime` | 获取当前时间 |

**Agent 编排（LangGraph）**

```
用户输入 → Router Node
  ├─ 需要工具 → Tool Node → 结果回传 → Router
  └─ 直接回答 → LLM Node → 流式输出
```

**Agent 创建 UI 流程**

```
1. 填写名称 / 描述
2. 选择绑定模型
3. 编写系统提示词（支持变量插值 {{user_name}}）
4. 勾选启用工具
5. 关联知识库（已上传文件集合）
6. 保存 → 立即可在对话中选用
```

---

### 4.4 配置管理中心

**模型管理页面**
- 添加 / 编辑 / 删除模型配置
- API Key 脱敏显示，加密存储（AES-256）
- 连通性测试（发送 ping 请求验证）
- 设置默认模型

**Agent 管理页面**
- Agent 列表 / 创建 / 编辑 / 克隆 / 删除
- 可见性控制（私有 / 公开）
- 使用统计（对话次数、token 消耗）

**系统设置**
- 文件存储路径
- 最大上传文件大小
- Embedding 模型选择
- 日志级别

---

## 5. 数据库设计

### 主要表结构（PostgreSQL）

```sql
-- 用户表
CREATE TABLE users (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username    VARCHAR(64) UNIQUE NOT NULL,
    email       VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role        VARCHAR(20) DEFAULT 'user',  -- admin | user
    created_at  TIMESTAMPTZ DEFAULT now()
);

-- 模型配置表
CREATE TABLE model_configs (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(128) NOT NULL,
    provider    VARCHAR(32) NOT NULL,
    api_base    TEXT NOT NULL,
    api_key_enc TEXT NOT NULL,      -- AES-256 加密
    model_name  VARCHAR(128) NOT NULL,
    params      JSONB DEFAULT '{}', -- temperature, max_tokens 等
    is_default  BOOLEAN DEFAULT false,
    is_enabled  BOOLEAN DEFAULT true,
    created_by  UUID REFERENCES users(id),
    created_at  TIMESTAMPTZ DEFAULT now()
);

-- 会话表
CREATE TABLE conversations (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID REFERENCES users(id),
    agent_id    UUID REFERENCES agents(id),
    title       VARCHAR(256),
    model_id    UUID REFERENCES model_configs(id),
    created_at  TIMESTAMPTZ DEFAULT now(),
    updated_at  TIMESTAMPTZ DEFAULT now()
);

-- 消息表
CREATE TABLE messages (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    role            VARCHAR(16) NOT NULL,  -- user | assistant | system | tool
    content         TEXT NOT NULL,
    token_count     INTEGER,
    metadata        JSONB DEFAULT '{}',    -- tool_calls, file_refs 等
    created_at      TIMESTAMPTZ DEFAULT now()
);

-- 文件表
CREATE TABLE files (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID REFERENCES users(id),
    filename    TEXT NOT NULL,
    file_path   TEXT NOT NULL,
    file_size   BIGINT,
    mime_type   VARCHAR(128),
    parse_status VARCHAR(16) DEFAULT 'pending', -- pending | ready | failed
    chunk_count INTEGER DEFAULT 0,
    created_at  TIMESTAMPTZ DEFAULT now()
);

-- Agent 表
CREATE TABLE agents (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(128) NOT NULL,
    description     TEXT,
    system_prompt   TEXT NOT NULL,
    model_id        UUID REFERENCES model_configs(id),
    tools           TEXT[] DEFAULT '{}',
    kb_file_ids     UUID[] DEFAULT '{}',
    max_iterations  INTEGER DEFAULT 10,
    memory_type     VARCHAR(32) DEFAULT 'buffer',
    is_public       BOOLEAN DEFAULT false,
    created_by      UUID REFERENCES users(id),
    created_at      TIMESTAMPTZ DEFAULT now(),
    updated_at      TIMESTAMPTZ DEFAULT now()
);

-- Token 用量统计表
CREATE TABLE usage_stats (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID REFERENCES users(id),
    conversation_id UUID REFERENCES conversations(id),
    model_id        UUID REFERENCES model_configs(id),
    agent_id        UUID REFERENCES agents(id),
    prompt_tokens   INTEGER NOT NULL DEFAULT 0,
    completion_tokens INTEGER NOT NULL DEFAULT 0,
    total_tokens    INTEGER GENERATED ALWAYS AS (prompt_tokens + completion_tokens) STORED,
    cost_cents      NUMERIC(10,4) DEFAULT 0,  -- 成本（分）
    created_at      TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_usage_user_date ON usage_stats(user_id, created_at);
CREATE INDEX idx_usage_model ON usage_stats(model_id, created_at);
```

---

## 6. API 接口设计

### 认证

```
POST /api/auth/login         → { access_token, refresh_token }
POST /api/auth/refresh       → { access_token }
POST /api/auth/logout
```

### 对话

```
GET  /api/conversations              → 会话列表
POST /api/conversations              → 新建会话
DELETE /api/conversations/{id}       → 删除会话

GET  /api/conversations/{id}/messages → 消息历史
POST /api/conversations/{id}/chat     → 发送消息（SSE 流式）
  Body: { content, file_ids?, agent_id?, model_id? }
```

### 文件

```
POST /api/files/upload         → multipart/form-data
GET  /api/files                → 文件列表
GET  /api/files/{id}/status    → 解析状态
DELETE /api/files/{id}
```

### Agent

```
GET    /api/agents             → Agent 列表
POST   /api/agents             → 创建 Agent
GET    /api/agents/{id}        → Agent 详情
PUT    /api/agents/{id}        → 更新 Agent
DELETE /api/agents/{id}        → 删除 Agent
POST   /api/agents/{id}/test   → 测试 Agent
```

### 配置

```
GET    /api/config/models      → 模型列表
POST   /api/config/models      → 添加模型
PUT    /api/config/models/{id} → 更新模型
DELETE /api/config/models/{id} → 删除模型
POST   /api/config/models/{id}/test → 连通性测试
```

---

## 7. 前端页面结构

```
src/
├── pages/
│   ├── AiChat/             # 主对话页
│   │   ├── index.tsx       # 页面入口
│   │   ├── SessionsPanel/  # 左侧会话列表
│   │   ├── ChatWindow/     # 中间对话区
│   │   ├── ChatInput/      # 输入框（含文件上传）
│   │   └── ModelSelector/  # 模型/Agent 切换
│   ├── Files/              # 文件管理页
│   ├── Agents/             # Agent 管理页
│   │   ├── AgentList/
│   │   └── AgentEditor/    # Agent 创建/编辑
│   └── Settings/           # 配置管理页
│       ├── ModelsConfig/   # 模型配置
│       └── SystemConfig/   # 系统设置
├── components/
│   ├── MessageBubble/      # 消息气泡（支持 Markdown）
│   ├── FileAttachment/     # 文件附件组件
│   ├── ToolCallDisplay/    # Agent 工具调用展示
│   └── StreamingText/      # 流式文本渲染
├── hooks/
│   ├── useSSEChat.ts       # SSE 流式对话 hook
│   ├── useFileUpload.ts    # 文件上传 hook
│   └── useAgentConfig.ts   # Agent 配置 hook
└── stores/
    ├── chatStore.ts        # 对话状态
    ├── configStore.ts      # 配置状态
    └── fileStore.ts        # 文件状态
```

---

## 8. 目录结构（后端）

```
backend/
├── app/
│   ├── main.py             # FastAPI 入口
│   ├── api/
│   │   ├── auth.py
│   │   ├── chat.py         # SSE 流式接口
│   │   ├── files.py
│   │   ├── agents.py
│   │   └── config.py
│   ├── services/
│   │   ├── chat_service.py       # 对话逻辑
│   │   ├── file_service.py       # 文件解析
│   │   ├── agent_service.py      # Agent 编排
│   │   └── embedding_service.py  # 向量化
│   ├── models/             # SQLAlchemy ORM 模型
│   ├── schemas/            # Pydantic 数据模式
│   ├── core/
│   │   ├── config.py       # 环境变量配置
│   │   ├── security.py     # JWT / 加密
│   │   └── database.py     # DB 连接
│   └── tasks/
│       └── file_tasks.py   # Celery 异步任务
├── migrations/             # Alembic 数据库迁移
├── tests/
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## 9. 部署方案

### 开发环境（Docker Compose）

```yaml
# docker-compose.yml
services:
  backend:
    build: ./backend
    ports: ["8000:8000"]
    env_file: .env
    depends_on: [postgres, redis]

  frontend:
    build: ./frontend
    ports: ["5173:80"]

  postgres:
    image: postgres:16-alpine
    volumes: [pgdata:/var/lib/postgresql/data]
    environment:
      POSTGRES_DB: aichat
      POSTGRES_USER: aichat
      POSTGRES_PASSWORD: ${DB_PASSWORD}

  redis:
    image: redis:7-alpine

  arq-worker:
    build: ./backend
    command: arq app.tasks.WorkerSettings
    depends_on: [redis, postgres]

  chromadb:
    image: chromadb/chroma:latest
    ports: ["8001:8000"]
    volumes: [chromadata:/chroma/chroma]

volumes:
  pgdata:
  chromadata:
```

### 生产环境

| 组件 | 推荐方案 |
|---|---|
| 后端 | Gunicorn + Uvicorn workers, Nginx 反代 |
| 前端 | Vite build → Nginx 静态托管 |
| 数据库 | PostgreSQL on VM / Supabase 免费套餐 |
| 向量库 | ChromaDB 持久化 or Qdrant Cloud 免费套餐 |
| 文件存储 | 本地磁盘 / MinIO（免费自托管） |

---

## 10. 安全设计

| 风险点 | 措施 |
|---|---|
| API Key 泄露 | AES-256 加密存储，接口返回脱敏显示，禁止日志打印 Key |
| 文件上传攻击 | ① magic bytes 真实类型校验（非仅 MIME header）② 文件大小限制（默认 20MB）③ 随机化存储路径（UUID 命名）④ uploads 目录禁止 HTTP 直接访问 ⑤ 可选杀毒扫描 |
| Prompt Injection | ① 系统提示词与用户输入隔离（不拼接）② Agent 输出不作为代码直接执行 ③ 工具调用参数校验 |
| 代码执行 RCE | code_executor 工具使用 Docker 容器沙箱，限 CPU/内存/时间，禁用网络和宿主文件系统挂载 |
| 未授权访问 | JWT Bearer 认证，RBAC 角色权限，refresh token 轮换 |
| API 滥用 | slowapi 限流：匿名 10 req/min，认证用户 60 req/min，AI 对话 20 req/min |
| SQL 注入 | SQLAlchemy ORM 参数化查询 |
| XSS | Markdown 渲染白名单过滤（rehype-sanitize） |
| CORS | 严格配置 allow_origins，生产环境仅允许前端域名 |

---

## 11. 关键依赖版本

```txt
# requirements.txt
fastapi==0.115.0
uvicorn[standard]==0.30.0
sqlalchemy==2.0.36
alembic==1.13.3
pydantic==2.9.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
langchain==0.3.0
langgraph==0.2.0
langchain-openai==0.2.0         # 兼容 DeepSeek OpenAI 格式
chromadb==0.5.0
arq==0.26.1                     # 轻量异步任务队列
redis==5.1.0
pymupdf==1.24.0                 # PDF 解析
python-docx==1.1.2
openpyxl==3.1.5
pillow==10.4.0
python-multipart==0.0.12
asyncpg==0.29.0                 # PostgreSQL 异步驱动
slowapi==0.1.9                  # API 限流
structlog==24.4.0               # 结构化日志
python-magic==0.4.27            # 文件 magic bytes 校验
websockets==13.1                # WebSocket 支持
```

```json
// package.json 关键依赖
{
  "react": "^18.3.0",
  "react-router-dom": "^6.26.0",
  "@tanstack/react-query": "^5.56.0",
  "zustand": "^4.5.0",
  "streamdown": "^latest",
  "react-i18next": "^15.0.0",
  "tailwindcss": "^4.0.0"
}
```

---


## 附录：DeepSeek API 集成示例

```python
# DeepSeek 使用 OpenAI 兼容格式，直接用 langchain-openai
from langchain_openai import ChatOpenAI

deepseek_chat = ChatOpenAI(
    model="deepseek-chat",
    api_key="sk-...",
    base_url="https://api.deepseek.com/v1",
    streaming=True,
)

# 流式调用
async for chunk in deepseek_chat.astream("你好"):
    print(chunk.content, end="", flush=True)
```

```python
# Ollama 本地模型（完全免费）
from langchain_ollama import ChatOllama

ollama_model = ChatOllama(
    model="qwen2.5:7b",
    base_url="http://localhost:11434",
)
```
