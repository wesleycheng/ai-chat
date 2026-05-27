# AI Chat Platform

企业级多功能 AI Chat 平台

## 功能特性

- **多模型对话**：支持 DeepSeek、OpenAI、Ollama 等多种模型
- **文件分析**：上传 PDF/Word/Excel/图片，AI 自动解析
- **自定义 Agent**：可视化创建和管理 AI Agent
- **配置管理**：统一管理模型参数、系统提示词

## 技术栈

### 后端
- FastAPI + Python 3.12
- LangChain / LangGraph
- PostgreSQL + Redis + ChromaDB
- SSE 流式输出

### 前端
- React 18 + TypeScript
- Vite + Tailwind CSS v4
- Zustand + TanStack Query

## 快速开始

### 1. 克隆项目

```bash
git clone git@github.com:wesleycheng/ai-chat.git
cd ai-chat
```

### 2. 启动服务

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f backend
```

### 3. 访问应用

- API 文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

### 4. 配置模型

1. 访问 `/docs`
2. 使用 `/api/auth/register` 注册用户
3. 使用 `/api/config/models` 添加模型配置

## 项目结构

```
ai-chat-platform/
├── backend/
│   ├── app/
│   │   ├── api/          # API 路由
│   │   ├── core/         # 核心配置
│   │   ├── models/       # ORM 模型
│   │   ├── schemas/      # Pydantic 模式
│   │   ├── services/     # 业务逻辑
│   │   └── main.py       # 应用入口
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/             # React 前端（待实现）
├── docker-compose.yml
└── README.md
```

## API 接口

### 认证
- `POST /api/auth/register` - 注册
- `POST /api/auth/login` - 登录
- `POST /api/auth/refresh` - 刷新令牌

### 对话
- `GET /api/conversations` - 会话列表
- `POST /api/conversations` - 创建会话
- `POST /api/conversations/{id}/chat` - 发送消息（SSE）

### 文件
- `POST /api/files/upload` - 上传文件
- `GET /api/files` - 文件列表
- `GET /api/files/{id}/status` - 解析状态

### Agent
- `GET /api/agents` - Agent 列表
- `POST /api/agents` - 创建 Agent
- `PUT /api/agents/{id}` - 更新 Agent

### 配置
- `GET /api/config/models` - 模型列表
- `POST /api/config/models` - 添加模型

## 开发

```bash
# 安装依赖
cd backend
pip install -r requirements.txt

# 运行开发服务器
uvicorn app.main:app --reload

# 数据库迁移
alembic revision --autogenerate -m "init"
alembic upgrade head
```

## 许可证

MIT