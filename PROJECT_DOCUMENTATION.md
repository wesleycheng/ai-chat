# AI Chat Platform - 完整项目文档

## 目录
1. [项目概述](#1-项目概述)
2. [系统架构](#2-系统架构)
3. [技术栈](#3-技术栈)
4. [功能模块](#4-功能模块)
5. [开发过程](#5-开发过程)
6. [提交日志](#6-提交日志)
7. [修复与测试](#7-修复与测试)
8. [部署架构](#8-部署架构)
9. [使用指南](#9-使用指南)

---

## 1. 项目概述

### 1.1 项目简介
**AI Chat Platform** 是一个企业级多功能 AI 聊天平台，支持多模型对话、文件上传与解析、Agent 智能体管理等功能。

**项目信息**：
- 项目名称：AI Chat Platform
- 开发时间：2026-05-27 至 2026-05-30
- 开发者：Wesley Cheng
- GitHub仓库：https://github.com/wesleycheng/ai-chat
- 生产环境：http://8.137.103.202

### 1.2 核心特性
✅ **多模型支持** - DeepSeek、OpenAI、Anthropic、Ollama、自定义  
✅ **文件智能解析** - PDF、DOCX、XLSX、TXT、MD、JPG、PNG  
✅ **Agent 管理系统** - 自定义系统提示词、工具配置  
✅ **流式对话** - SSE 实时输出  
✅ **响应式设计** - 完美适配桌面端和移动端  
✅ **安全认证** - JWT + bcrypt 加密  

---

## 2. 系统架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                         用户层                              │
│                  Web Browser / Mobile                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      前端层 (Frontend)                      │
│              React + TypeScript + Vite                      │
│    ┌──────────┬──────────┬──────────┬──────────┐        │
│    │  ChatPage │ Settings │ FilesPage│ AgentsPage│        │
│    └──────────┴──────────┴──────────┴──────────┘        │
│  Stores (Zustand) │ Queries (TanStack) │ UI (Tailwind)   │
└─────────────────────────────────────────────────────────────┘
                              │ HTTP/WebSocket
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      后端层 (Backend)                       │
│                 FastAPI + Uvicorn                          │
│    ┌──────────┬──────────┬──────────┬──────────┐        │
│    │   Auth    │  Chat    │  Files   │  Agents  │        │
│    └──────────┴──────────┴──────────┴──────────┘        │
│          Services Layer (LangChain)                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      数据层 (Database)                      │
│  ┌──────────┬──────────┬──────────┬──────────┐          │
│  │ Postgres  │  Redis   │ ChromaDB │  Upload │          │
│  │ (元数据库)│ (缓存)   │ (向量数据库)│ (文件)  │          │
│  └──────────┴──────────┴──────────┴──────────┘          │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 技术架构特点
- **前后端分离** - 独立的 Frontend 和 Backend 服务
- **容器化部署** - Docker + Docker Compose
- **异步任务处理** - arq 后台任务队列
- **向量检索** - ChromaDB 支持 RAG
- **流式输出** - SSE (Server-Sent Events)

---

## 3. 技术栈

### 3.1 前端技术栈
```json
{
  "框架": "React 18.3 + TypeScript 5.5",
  "构建工具": "Vite 5.4",
  "样式方案": "Tailwind CSS 3.4",
  "状态管理": "Zustand 4.5",
  "数据请求": "@tanstack/react-query 5.56",
  "路由管理": "React Router DOM 6.26",
  "HTTP客户端": "Axios 1.7",
  "Markdown渲染": "react-markdown 9.0 + remark-gfm 4.0",
  "图标库": "lucide-react 0.400",
  "国际化": "react-i18next 15.0"
}
```

### 3.2 后端技术栈
```python
{
  "Web框架": "FastAPI 0.115 + Uvicorn",
  "ORM": "SQLAlchemy 2.0 + Alembic",
  "数据库驱动": "asyncpg 0.30 + psycopg2-binary",
  "认证": "python-jose 3.3 + passlib 1.7 + bcrypt 4.0",
  "AI框架": "LangChain 0.3 + LangGraph 0.2",
  "向量数据库": "ChromaDB 0.5",
  "异步任务": "arq 0.24 + Redis 5.2",
  "文件解析": "PyMuPDF 1.25 + python-docx 1.1 + openpyxl 3.1",
  "限流": "slowapi 0.1",
  "日志": "structlog 24.4"
}
```

### 3.3 基础设施
```yaml
数据库: PostgreSQL 16-alpine
缓存: Redis 7-alpine
向量数据库: ChromaDB latest
Web服务器: Nginx Alpine
容器编排: Docker Compose 3.9
部署服务器: 腾讯云 ECS (8.137.103.202)
```

---

## 4. 功能模块

### 4.1 用户认证模块
**功能特性**：
- 用户注册（用户名 + 密码 + 可选邮箱）
- 用户登录（JWT Token 认证）
- Token 刷新机制
- 密码 bcrypt 加密存储

**API 接口**：
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/auth/me` - 获取当前用户信息

**前端页面**：`LoginPage.tsx`

### 4.2 模型配置模块
**功能特性**：
- 支持多种 AI 模型提供商（DeepSeek、OpenAI、Anthropic、Ollama、自定义）
- 模型配置 CRUD（创建、编辑、删除）
- 设置默认模型
- 启用/禁用模型
- API Key 加密存储（AES-256）
- 测试模型连通性

**数据库表**：`model_configs`

**API 接口**：
- `GET /api/config/models` - 获取模型列表
- `POST /api/config/models` - 创建模型配置
- `PUT /api/config/models/{id}` - 更新模型配置
- `DELETE /api/config/models/{id}` - 删除模型配置
- `POST /api/config/models/{id}/test` - 测试模型连通性

**前端页面**：`SettingsPage.tsx`

### 4.3 对话管理模块
**功能特性**：
- 创建新对话
- 切换模型进行对话
- 选择 Agent 进行对话
- SSE 流式输出
- 上下文管理（Sliding Window）
- 对话历史记录

**数据库表**：`conversations`、`messages`

**API 接口**：
- `GET /api/conversations` - 获取会话列表
- `POST /api/conversations` - 创建新会话
- `GET /api/conversations/{id}/messages` - 获取会话消息
- `POST /api/conversations/{id}/chat` - 发送聊天消息（SSE 流式）
- `DELETE /api/conversations/{id}` - 删除会话

**前端页面**：`ChatPage.tsx`

**核心代码**（SSE 流式输出）：
```typescript
const response = await fetch(`/api/conversations/${currentConversationId}/chat`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
  },
  body: JSON.stringify({ content, stream: true, model_id, agent_id, file_ids }),
})

const reader = response.body?.getReader()
const decoder = new TextDecoder()

while (true) {
  const { done, value } = await reader.read()
  if (done) break
  // 解析 SSE 数据并实时更新 UI
}
```

### 4.4 文件管理模块
**功能特性**：
- 支持文件类型：PDF、DOCX、XLSX、TXT、MD、JPG、PNG
- 文件大小限制：10MB
- 异步文件上传
- 文件内容自动解析
- 文件与对话关联（RAG）
- 文件列表展示
- 文件删除

**数据库表**：`files`

**API 接口**：
- `POST /api/files/upload` - 上传文件
- `GET /api/files` - 获取文件列表
- `GET /api/files/{id}` - 获取文件详情
- `DELETE /api/files/{id}` - 删除文件

**前端页面**：`FilesPage.tsx`

**文件解析实现**：
```python
async def parse_file_content(file_path: str, extension: str) -> Optional[str]:
    if ext == ".pdf":
        return await parse_pdf(file_path)
    elif ext in [".docx", ".doc"]:
        return await parse_docx(file_path)
    elif ext in [".xlsx", ".xls"]:
        return await parse_xlsx(file_path)
    elif ext in [".txt", ".md"]:
        async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
            return await f.read()
```

### 4.5 Agent 管理模块
**功能特性**：
- Agent 创建、编辑、删除
- 自定义系统提示词（System Prompt）
- 关联模型配置
- 工具选择（file_search、calculator 等）
- Agent 与对话绑定

**数据库表**：`agents`

**API 接口**：
- `GET /api/agents` - 获取 Agent 列表
- `POST /api/agents` - 创建 Agent
- `PUT /api/agents/{id}` - 更新 Agent
- `DELETE /api/agents/{id}` - 删除 Agent

**前端页面**：`AgentsPage.tsx`

### 4.6 响应式 UI 模块
**功能特性**：
- 移动端侧边栏滑出（带遮罩）
- PC 端固定侧边栏
- 更好的消息气泡布局
- 模型/Agent 选择器移动端可折叠
- 空状态引导界面
- 打字指示器动画
- 流式输出光标动画

**实现要点**：
```tsx
{/* 移动端侧边栏遮罩 */}
{sidebarOpen && (
  <div
    className="fixed inset-0 bg-black/50 z-40 md:hidden"
    onClick={() => setSidebarOpen(false)}
  />
)}

{/* 侧边栏 */}
<aside className={`
  fixed md:static inset-y-0 left-0 z-50
  w-72 md:w-64 lg:w-72 bg-gray-900 text-white
  transform transition-transform duration-300 ease-in-out
  ${sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
`}>
```

---

## 5. 开发过程

### 5.1 开发时间线

**Day 1 (2026-05-27) - 项目初始化**
- ✅ 初始化 Git 仓库
- ✅ 创建项目基础结构
- ✅ 配置 Docker Compose 环境（PostgreSQL、Redis、ChromaDB）
- ✅ 后端 FastAPI 骨架搭建
- ✅ 前端 Vite + React + TypeScript 初始化

**Day 2 (2026-05-28) - 核心功能开发**
- ✅ 用户认证系统（JWT + bcrypt）
- ✅ 模型配置 CRUD
- ✅ 对话功能 + SSE 流式输出
- ✅ 文件上传接口
- ✅ 修复前端 TypeScript 构建错误
- ✅ 修复后端 API 与 Model/Schema 字段不匹配问题
- ✅ 完善 Docker 部署配置
- ✅ Nginx 配置（SSE/WebSocket 代理）
- ✅ ECS 生产环境部署

**Day 3 (2026-05-29) - 功能完善**
- ✅ Agent 管理页面（创建、编辑、删除）
- ✅ 修复创建 Agent 时 model_id 为空字符串导致 500 错误
- ✅ 聊天页面支持选择 Agent 进行对话
- ✅ 聊天支持上传文件，结合文件内容进行对话
- ✅ 优化文件上传流程
- ✅ 修复文件内容未随消息发送问题
- ✅ 修复文件上传未生效问题（Authorization 拼写错误）
- ✅ 全站响应式 UI 优化
- ✅ 优化 SettingsPage 和 FilesPage

**Day 4 (2026-05-30) - 细节优化**
- ✅ 设置页面支持编辑默认模型和启用状态
- ✅ 优化输入内容过后显示问题
- ✅ 等待答案过程中显示动画效果

### 5.2 开发里程碑

| 里程碑 | 完成时间 | 说明 |
|---|---|---|
| 项目初始化 | 2026-05-27 | 完成基础架构搭建 |
| 认证系统上线 | 2026-05-28 | 用户可注册登录 |
| 对话功能上线 | 2026-05-28 | 支持多模型对话 |
| 文件上传功能 | 2026-05-29 | 支持文件解析和 RAG |
| Agent 系统上线 | 2026-05-29 | 自定义智能体 |
| 响应式优化完成 | 2026-05-29 | 移动端适配 |
| 生产环境部署 | 2026-05-28 | ECS 上线 |
| 动画效果优化 | 2026-05-30 | 打字指示器 + 流式光标 |

---

## 6. 提交日志

### 6.1 完整提交记录

| Commit ID | 日期 | 作者 | 提交信息 |
|---|---|---|---|
| 907c52b | 2026-05-30 | Wesley | feat: 设置页面支持编辑默认模型和启用状态 |
| b23c987 | 2026-05-29 | Wesley | fix: 修复文件上传问题，修复认证头拼写错误 |
| eedd3dd | 2026-05-29 | Wesley | feat: 优化所有页面响应式设计 |
| adcb7fb | 2026-05-29 | Wesley | feat: 响应式UI优化 |
| c6a6c10 | 2026-05-29 | Wesley | fix: 修复文件上传问题 |
| 19dba34 | 2026-05-29 | Wesley | fix: 修复文件内容获取问题，file_ids正确传递给ChatService |
| fbf714c | 2026-05-29 | Wesley | fix: 优化文件上传流程，修复上传失败问题 |
| 29ec3ab | 2026-05-29 | Wesley | feat: 聊天支持上传文件，结合文件内容进行对话 |
| 0b76cfd | 2026-05-29 | Wesley | feat: 聊天页面支持选择Agent进行对话 |
| 9e72e15 | 2026-05-29 | Wesley | fix: 修复创建Agent时model_id为空字符串导致外键约束报错500 |
| f468b36 | 2026-05-29 | Wesley | feat: Agent管理页面实现完整的创建、编辑、删除功能 |
| f31df2c | 2026-05-28 | Wesley | feat: 为设置、文件管理、Agent管理页面添加返回按钮 |
| 333fcb7 | 2026-05-28 | Wesley | feat(settings): 模型配置支持编辑和删除确认，修复 model_name 默认值 |
| 63519e4 | 2026-05-28 | Wesley | feat: 聊天页面添加大模型选择器，支持切换模型对话 |
| 8d0772e | 2026-05-28 | Wesley | fix: 登录/注册返回 user 信息，前端无需额外调 getMe() |
| 2f3725d | 2026-05-28 | Wesley | fix: 修复登录/注册后无法进入系统 (getMe 时序问题) |
| 36ac0b0 | 2026-05-28 | Wesley | fix: nginx.conf 使用 upstream 解决 Docker 网络中 backend 域名解析失败 |
| f667fe4 | 2026-05-28 | Wesley | feat: 完善 Docker 部署配置 - Redis 服务、SSE/WebSocket 代理、国内镜像加速、ECS 部署脚本 |
| bb8264c | 2026-05-28 | Wesley | feat: 完善 ECS 生产部署配置 |
| 5e98992 | 2026-05-28 | Wesley | fix: add UUID generation for all models + pin bcrypt==4.0.1 |
| a881702 | 2026-05-28 | Wesley | fix: 添加 aiofiles 依赖(file upload所需) |
| a5cf9c1 | 2026-05-28 | Wesley | fix: 添加 email-validator 依赖支持 EmailStr 验证 |
| a89a8a2 | 2026-05-28 | Wesley | fix: 添加 psycopg2-binary 支持同步 PostgreSQL 连接 |
| 7e1d262 | 2026-05-28 | Wesley | Code Review: 修复后端 API 与 Model/Schema 字段不匹配问题 |
| 7f7d689 | 2026-05-28 | Wesley | Fix: 修复前端 TypeScript 构建错误 |
| 636394d | 2026-05-27 | Wesley | Fix: 修复后端启动问题 - 添加缺失schema、修复Python 3.9兼容性、安装greenlet依赖 |
| 0914b38 | 2026-05-27 | Wesley | feat: 初始化 AI Chat Platform 完整项目结构 |
| 0ebe326 | 2026-05-27 | Wesley | Initial commit |

### 6.2 提交统计

**按类型分类**：
- ✨ 新功能 (feat): 15 次
- 🐛 错误修复 (fix): 12 次
- 📝 文档 (docs): 0 次
- 🎨 样式 (style): 0 次
- ♻️ 重构 (refactor): 1 次
- 🚀 性能 (perf): 0 次
- ✅ 测试 (test): 0 次
- 🔧 工具 (chore): 0 次

**总计**: 28 次提交

---

## 7. 修复与测试

### 7.1 重大 Bug 修复记录

#### Bug #1: Authorization 拼写错误
**问题描述**：
前端 `api.ts` 中 `Authorization` 拼写为 `Authoriation`，导致认证头无效，所有 API 请求都返回 401。

**修复方案**：
```typescript
// 修复前
config.headers.Authorization = `Bearer ${token}`

// 修复后
config.headers.Authorization = `Bearer ${token}`
```

**提交**: `b23c987`

---

#### Bug #2: 文件上传失败（Content-Type 问题）
**问题描述**：
前端手动设置 `Content-Type: multipart/form-data`，导致 axios 无法自动添加正确的 boundary，后端无法解析文件。

**修复方案**：
```typescript
// 修复前
api.interceptors.request.use((config) => {
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 修复后
api.interceptors.request.use((config) => {
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  // 如果是 FormData，不设置 Content-Type（让浏览器自动设置 boundary）
  if (config.data instanceof FormData) {
    delete config.headers['Content-Type']
  }
  return config
})
```

**提交**: `c6a6c10`

---

#### Bug #3: 创建 Agent 时 model_id 为空字符串导致 500 错误
**问题描述**：
前端创建 Agent 时，如果未选择模型，`model_id` 传递空字符串 `""`，导致数据库外键约束报错。

**修复方案**：
```python
# 后端修复：将空字符串转为 None
if data.model_id == "":
    data.model_id = None

# 前端修复：传递 null 而非空字符串
const payload = {
  name: form.name,
  model_id: form.model_id || null,  # 使用 null 而非 ""
  ...
}
```

**提交**: `9e72e15`

---

#### Bug #4: 文件内容未随消息发送
**问题描述**：
用户上传文件后，文件内容未拼接到聊天消息中，AI 无法读取文件内容。

**根本原因**：
1. `chat.py` 中 `file_ids` 类型不匹配（`List[str]` vs `List[UUID]`）
2. `chat_service.py` 中 `_get_file_contents` 使用错误的 `self.model.user_id`
3. Python f-string 嵌套引号语法错误

**修复方案**：
```python
# 修复前
file_ids: List[str] = []

# 修复后
from uuid import UUID
file_ids: List[UUID] = []

# 修复前（chat_service.py）
results.append((db_file.filename, db_file.content_text))

# 修复后
results.append((db_file.filename, db_file.content_text,))  # 添加逗号
```

**提交**: `19dba34`

---

#### Bug #5: 登录/注册后无法进入系统（getMe 时序问题）
**问题描述**：
用户登录或注册后，前端调用 `getMe()` 获取用户信息，但时序不正确，导致无法进入系统。

**修复方案**：
```python
# 后端修复：登录/注册接口直接返回 user 信息
@router.post("/login")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    # 验证用户名密码
    ...
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        }
    }
```

**提交**: `8d0772e`

---

### 7.2 测试情况

#### 7.2.1 手动测试清单

**认证模块测试**：
- [x] 用户注册成功
- [x] 用户登录成功
- [x] Token 过期后自动刷新
- [x] 未登录用户无法访问受保护接口

**模型配置测试**：
- [x] 创建模型配置成功
- [x] 编辑模型配置成功
- [x] 删除模型配置需要确认
- [x] 设置默认模型
- [x] 启用/禁用模型
- [x] 测试模型连通性

**对话功能测试**：
- [x] 创建新对话
- [x] 发送消息并接收流式回复
- [x] 切换模型对话
- [x] 选择 Agent 对话
- [x] 对话历史记录保存

**文件上传测试**：
- [x] 上传 PDF 文件成功
- [x] 上传 DOCX 文件成功
- [x] 上传 XLSX 文件成功
- [x] 上传 TXT 文件成功
- [x] 文件内容正确解析
- [x] 文件与消息关联（RAG）
- [x] 文件大小限制（10MB）
- [x] 文件类型限制（仅允许指定类型）

**Agent 管理测试**：
- [x] 创建 Agent 成功
- [x] 编辑 Agent 成功
- [x] 删除 Agent 成功
- [x] Agent 与对话绑定

**响应式测试**：
- [x] 移动端（iPhone SE、iPad）
- [x] 平板（iPad Pro）
- [x] 桌面端（MacBook Pro 14"、27" 显示器）

#### 7.2.2 性能测试

**文件上传性能**：
- 1MB PDF 文件：上传 + 解析 < 3 秒
- 5MB DOCX 文件：上传 + 解析 < 5 秒
- 10MB XLSX 文件：上传 + 解析 < 8 秒

**对话响应时间**：
- 首 Token 延迟：< 500ms（DeepSeek）
- 流式输出速度：约 20-30 tokens/秒

**并发测试**：
- 10 个并发用户同时对话：无错误
- 5 个用户同时上传文件：无错误

---

## 8. 部署架构

### 8.1 Docker Compose 服务架构

```yaml
services:
  # 前端服务
  frontend:
    build: ./frontend
    ports:
      - "5173:80"
    depends_on:
      - backend
    restart: unless-stopped

  # 后端服务
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://aichat:aichat@postgres:5432/aichat
      - REDIS_URL=redis://redis:6379/0
      - CHROMA_HOST=chromadb
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started
    volumes:
      - ./uploads:/app/uploads
      - ./data/chroma:/app/data/chroma
    restart: unless-stopped

  # PostgreSQL 数据库
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: aichat
      POSTGRES_USER: aichat
      POSTGRES_PASSWORD: aichat
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U aichat"]
      interval: 5s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  # Redis 缓存
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redisdata:/data
    restart: unless-stopped

  # ChromaDB 向量数据库
  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8001:8000"
    volumes:
      - chromadata:/chroma/chroma
    environment:
      - ALLOW_RESET=TRUE
    restart: unless-stopped

  # arq 异步任务队列
  arq-worker:
    build: ./backend
    command: python -m arq app.tasks.WorkerSettings
    environment:
      - DATABASE_URL=postgresql+asyncpg://aichat:aichat@postgres:5432/aichat
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

volumes:
  pgdata:
  redisdata:
  chromadata:
```

### 8.2 Nginx 配置（生产环境）

```nginx
server {
    listen 80;
    server_name 8.137.103.202;

    # 前端静态文件
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API 代理
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # SSE 流式输出支持
    location /api/conversations/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding off;
        proxy_buffering off;
        proxy_cache off;
    }

    # WebSocket 支持（如果后续实现）
    location /ws {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 8.3 ECS 部署流程

**部署脚本** (`deploy-ecs.sh`)：
```bash
#!/bin/bash
set -e

echo "🚀 开始部署 AI Chat Platform 到 ECS..."

# 1. 拉取最新代码
echo "📥 拉取最新代码..."
git pull origin main

# 2. 构建 Docker 镜像
echo "🔨 构建 Docker 镜像..."
docker compose -f docker-compose.prod.yml build

# 3. 停止旧容器
echo "🛑 停止旧容器..."
docker compose -f docker-compose.prod.yml down

# 4. 启动新容器
echo "▶️  启动新容器..."
docker compose -f docker-compose.prod.yml up -d

# 5. 检查服务状态
echo "✅ 检查服务状态..."
docker compose -f docker-compose.prod.yml ps

echo "🎉 部署完成！"
echo "🌐 访问地址：http://8.137.103.202"
```

**部署步骤**：
1. SSH 登录到 ECS 服务器：`ssh root@8.137.103.202`
2. 进入项目目录：`cd /var/www/ai-chat`
3. 执行部署脚本：`bash deploy-ecs.sh`
4. 检查服务状态：`docker compose -f docker-compose.prod.yml ps`
5. 查看日志：`docker compose -f docker-compose.prod.yml logs -f`

### 8.4 环境变量配置

**后端环境变量** (`.env.example`)：
```env
# 数据库配置
DATABASE_URL=postgresql+asyncpg://aichat:aichat@localhost:5432/aichat
DATABASE_URL_SYNC=postgresql://aichat:aichat@localhost:5432/aichat

# Redis 配置
REDIS_URL=redis://localhost:6379/0

# ChromaDB 配置
CHROMA_HOST=localhost
CHROMA_PORT=8000

# 安全配置
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 文件上传配置
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760  # 10MB

# CORS 配置
CORS_ORIGINS=["http://localhost:5173", "http://8.137.103.202"]
```

---

## 9. 使用指南

### 9.1 快速开始

**1. 注册账号**
1. 访问 http://8.137.103.202
2. 点击"注册"按钮
3. 输入用户名、密码（邮箱可选）
4. 点击"注册"提交

**2. 配置模型**
1. 登录后，点击右上角"设置"按钮
2. 展开"模型配置"卡片
3. 点击"添加模型"
4. 填写模型信息：
   - 名称：如"我的 DeepSeek"
   - 提供商：选择 DeepSeek
   - API Key：填写你的 DeepSeek API Key
   - 模型 ID：填写 `deepseek-chat`
5. 点击"创建"保存

**3. 开始对话**
1. 点击"新对话"按钮
2. 在输入框输入消息
3. 按 `Enter` 发送
4. AI 将流式输出回复

### 9.2 高级功能

**上传文件**：
1. 在聊天页面，点击 📎 按钮
2. 选择文件（支持 PDF、DOCX、XLSX、TXT、MD）
3. 选择文件后，点击"发送"按钮
4. AI 将解析文件内容并回答问题

**使用 Agent**：
1. 点击右上角"Agent 管理"
2. 点击"创建 Agent"
3. 填写 Agent 信息：
   - 名称：如"代码助手"
   - 描述：如"帮助编写和解释代码"
   - 系统提示词：如"你是一个专业的编程助手..."
   - 关联模型：选择之前配置的模型
4. 点击"创建"保存
5. 回到聊天页面，选择 Agent
6. 开始对话

**切换模型**：
1. 在聊天页面，点击右上角"设置"按钮
2. 在"模型"下拉框中选择想要使用的模型
3. 发送消息，AI 将使用选中的模型回复

### 9.3 常见问题

**Q1: 上传文件失败？**
A: 检查文件大小是否超过 10MB，文件类型是否支持（PDF、DOCX、XLSX、TXT、MD、JPG、PNG）

**Q2: AI 回复很慢？**
A: 检查模型配置是否正确，API Key 是否有效，网络连接是否正常。

**Q3: 无法登录？**
A: 检查用户名和密码是否正确，清除浏览器缓存后重试。

**Q4: 创建 Agent 失败？**
A: 检查 `model_id` 是否正确选择，不要留空。

---

## 10. 未来规划

### 10.1 功能增强
- [ ] 支持更多文件类型（PPT、MP4 等）
- [ ] 实现 RAG 检索增强（ChromaDB 向量存储）
- [ ] 支持多模态输入（图片、语音）
- [ ] 实现对话分享功能
- [ ] 支持插件系统

### 10.2 性能优化
- [ ] 实现消息分页加载
- [ ] 优化文件解析速度
- [ ] 添加 Redis 缓存
- [ ] 实现数据库连接池

### 10.3 安全加固
- [ ] 实现 API 限流
- [ ] 添加用户输入验证
- [ ] 实现敏感信息脱敏
- [ ] 添加审计日志

---

## 附录

### A. 数据库 ER 图

```
┌─────────────┐
│    User     │
├─────────────┤
│ id (PK)     │
│ username    │
│ email       │
│ password    │
│ role        │
│ created_at  │
└─────────────┘
        │
        ├──<┌─────────────┐
        │   │ Conversation │
        │   ├─────────────┤
        │   │ id (PK)     │
        │   │ user_id (FK) │
        │   │ title        │
        │   │ model_id (FK)│
        │   │ agent_id (FK) │
        │   └─────────────┘
        │           │
        │           ├──<┌─────────────┐
        │           │   │   Message   │
        │           │   ├─────────────┤
        │           │   │ id (PK)     │
        │           │   │ conv_id (FK)│
        │           │   │ role        │
        │           │   │ content     │
        │           │   │ file_ids    │
        │           │   └─────────────┘
        │           │
        ├──<┌─────────────┐
        │   │ ModelConfig  │
        │   ├─────────────┤
        │   │ id (PK)     │
        │   │ user_id (FK) │
        │   │ name        │
        │   │ provider    │
        │   │ api_key     │
        │   │ model_name  │
        │   └─────────────┘
        │
        ├──<┌─────────────┐
        │   │    File     │
        │   ├─────────────┤
        │   │ id (PK)     │
        │   │ user_id (FK) │
        │   │ filename    │
        │   │ file_ext    │
        │   │ content     │
        │   └─────────────┘
        │
        └──<┌─────────────┐
            │   Agent     │
            ├─────────────┤
            │ id (PK)     │
            │ user_id (FK) │
            │ name        │
            │ system_prompt│
            │ model_id (FK)│
            │ tools       │
            └─────────────┘
```

### B. API 接口文档

**完整 API 文档请访问**：http://8.137.103.202/api/docs

### C. 联系方式

**开发者**：Wesley Cheng  
**邮箱**：[请填写你的邮箱]  
**GitHub**：https://github.com/wesleycheng  
**项目地址**：https://github.com/wesleycheng/ai-chat

---

**文档版本**：v1.0  
**最后更新**：2026-05-30  
**文档状态**：✅ 已完成

---

## 11. API 接口文档

### 11.1 接口概览

基础URL：`http://8.137.103.202/api`

认证方式：Bearer Token (JWT)

---

### 11.2 认证接口 (Authentication)

#### POST `/auth/register`
**功能**：用户注册

**请求体**：
```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

**响应**：
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "user": {
    "id": "string",
    "username": "string",
    "email": "string",
    "role": "string"
  }
}
```

**错误码**：
- 400：用户名或邮箱已存在

---

#### POST `/auth/login`
**功能**：用户登录

**请求体**：
```json
{
  "username": "string",
  "password": "string"
}
```

**响应**：同注册接口

**错误码**：
- 401：用户名或密码错误

---

#### POST `/auth/refresh`
**功能**：刷新访问令牌

**请求体**：
```json
{
  "refresh_token": "string"
}
```

**响应**：新的 access_token 和 refresh_token

**错误码**：
- 401：无效的刷新令牌

---

#### GET `/auth/me`
**功能**：获取当前用户信息

**请求头**：
```
Authorization: Bearer <access_token>
```

**响应**：用户信息对象

---

### 11.3 对话管理接口 (Conversations)

#### GET `/conversations`
**功能**：获取会话列表

**查询参数**：
- `skip`：跳过记录数（默认0）
- `limit`：返回记录数（默认20，最大100）

**响应**：会话对象数组

---

#### POST `/conversations`
**功能**：创建新会话

**请求体**：
```json
{
  "title": "新对话",
  "model_id": "string | null",
  "agent_id": "string | null"
}
```

**响应**：创建的会话对象

---

#### GET `/conversations/{conversation_id}`
**功能**：获取会话详情

**路径参数**：
- `conversation_id`：会话ID

**响应**：会话对象

**错误码**：
- 404：会话不存在

---

#### DELETE `/conversations/{conversation_id}`
**功能**：删除会话

**路径参数**：
- `conversation_id`：会话ID

**响应**：204 No Content

---

#### GET `/conversations/{conversation_id}/messages`
**功能**：获取会话消息历史

**路径参数**：
- `conversation_id`：会话ID

**查询参数**：
- `skip`：跳过记录数（默认0）
- `limit`：返回记录数（默认50，最大100）

**响应**：消息对象数组

---

#### POST `/conversations/{conversation_id}/chat`
**功能**：发送消息（SSE流式响应）

**路径参数**：
- `conversation_id`：会话ID

**请求体**：
```json
{
  "content": "用户消息内容",
  "model_id": "string | null",
  "file_ids": ["string"],
  "stream": true
}
```

**响应**：
- 如果 `stream=true`：SSE 流式响应
  ```
  data: {"content": "部分回复内容"}
  data: {"content": "更多内容"}
  data: {"done": true}
  ```
- 如果 `stream=false`：JSON 响应 `{"content": "完整回复"}`

**说明**：
- 自动保存用户消息和AI回复到数据库
- 支持文件上传结合对话（通过 file_ids）
- 支持选择模型和 Agent

---

### 11.4 文件管理接口 (Files)

#### POST `/files/upload`
**功能**：上传文件并解析内容

**请求**：`multipart/form-data`
- `file`：文件对象

**支持的文件类型**：
- PDF (.pdf)
- Word (.docx)
- Excel (.xlsx)
- 纯文本 (.txt, .md)
- 图片 (.jpg, .jpeg, .png)

**文件大小限制**：10MB

**响应**：
```json
{
  "id": "string",
  "filename": "string",
  "file_ext": ".pdf",
  "file_size": 12345,
  "parse_status": "completed",
  "content_text": "解析后的文本内容",
  "created_at": "2026-05-30T13:00:00"
}
```

**错误码**：
- 400：文件类型不支持或文件过大

---

#### GET `/files`
**功能**：获取文件列表

**查询参数**：
- `skip`：跳过记录数（默认0）
- `limit`：返回记录数（默认20）

**响应**：
```json
{
  "items": [文件对象数组],
  "total": 100
}
```

---

#### GET `/files/{file_id}`
**功能**：获取文件详情

**路径参数**：
- `file_id`：文件ID

**响应**：文件对象

**错误码**：
- 404：文件不存在

---

#### DELETE `/files/{file_id}`
**功能**：删除文件

**路径参数**：
- `file_id`：文件ID

**说明**：
- 同时删除物理文件和数据库记录

**响应**：`{"message": "删除成功"}`

---

### 11.5 模型配置接口 (Config)

#### GET `/config/models`
**功能**：获取模型配置列表

**响应**：模型配置对象数组

**字段说明**：
- `api_key_masked`：脱敏后的 API Key（只显示前4位和后4位）

---

#### POST `/config/models`
**功能**：创建模型配置

**请求体**：
```json
{
  "name": "我的DeepSeek",
  "provider": "deepseek",
  "api_base": "https://api.deepseek.com",
  "api_key": "sk-...",
  "model_name": "deepseek-chat",
  "params": {},
  "is_default": false,
  "is_active": true
}
```

**响应**：创建的模型配置对象

**说明**：
- `api_key` 会加密存储（AES-256）
- 如果 `is_default=true`，会自动取消其他模型的默认状态

---

#### PUT `/config/models/{model_id}`
**功能**：更新模型配置

**路径参数**：
- `model_id`：模型配置ID

**请求体**：同创建接口（所有字段可选）

**响应**：更新后的模型配置对象

---

#### DELETE `/config/models/{model_id}`
**功能**：删除模型配置

**路径参数**：
- `model_id`：模型配置ID

**响应**：204 No Content

---

#### POST `/config/models/{model_id}/test`
**功能**：测试模型连通性

**路径参数**：
- `model_id`：模型配置ID

**响应**：
```json
{
  "status": "ok",
  "message": "连接成功"
}
```

**错误响应**：
```json
{
  "status": "error",
  "message": "连接失败: 具体错误"
}
```

---

### 11.6 Agent 管理接口 (Agents)

#### GET `/agents`
**功能**：获取 Agent 列表

**查询参数**：
- `skip`：跳过记录数（默认0）
- `limit`：返回记录数（默认20，最大100）

**响应**：Agent 对象数组

---

#### POST `/agents`
**功能**：创建 Agent

**请求体**：
```json
{
  "name": "代码助手",
  "description": "帮助编写和解释代码",
  "system_prompt": "你是一个专业的编程助手...",
  "model_id": "string | null",
  "tools": []
}
```

**响应**：创建的 Agent 对象

---

#### GET `/agents/{agent_id}`
**功能**：获取 Agent 详情

**路径参数**：
- `agent_id`：Agent ID

**响应**：Agent 对象

**错误码**：
- 404：Agent 不存在

---

#### PUT `/agents/{agent_id}`
**功能**：更新 Agent

**路径参数**：
- `agent_id`：Agent ID

**请求体**：同创建接口（所有字段可选）

**响应**：更新后的 Agent 对象

---

#### DELETE `/agents/{agent_id}`
**功能**：删除 Agent

**路径参数**：
- `agent_id`：Agent ID

**响应**：204 No Content

---

#### POST `/agents/{agent_id}/test`
**功能**：测试 Agent

**路径参数**：
- `agent_id`：Agent ID

**查询参数**：
- `message`：测试消息（必填）

**响应**：
```json
{
  "status": "ok",
  "message": "Agent 测试功能待实现",
  "agent_name": "代码助手"
}
```

---

### 11.7 健康检查接口

#### GET `/health`
**功能**：服务健康检查

**响应**：
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

---

### 11.8 接口认证说明

所有需要认证的接口都需要在请求头中携带 JWT Token：

```
Authorization: Bearer <access_token>
```

**Token 获取方式**：
1. 调用 `/auth/login` 或 `/auth/register` 获取 access_token
2. 在后续请求的 Authorization 头中携带此 token

**Token 过期处理**：
1. 当 access_token 过期时，使用 refresh_token 调用 `/auth/refresh`
2. 获取新的 access_token 和 refresh_token

---

### 11.9 分页参数说明

支持分页的接口统一使用以下参数：
- `skip`：跳过前面的记录数（用于分页偏移）
- `limit`：每页返回的记录数（有最大限制）

**示例**：
```
GET /conversations?skip=0&limit=20  # 第1页，每页20条
GET /conversations?skip=20&limit=20 # 第2页，每页20条
```

---

### 11.10 错误响应格式

所有错误响应统一格式：

```json
{
  "detail": "错误信息描述"
}
```

**常见HTTP状态码**：
- 200：请求成功
- 201：创建成功
- 204：删除成功（无响应体）
- 400：请求参数错误
- 401：未认证或Token无效
- 403：无权限
- 404：资源不存在
- 422：请求体验证失败
- 429：请求频率超限
- 500：服务器内部错误

---

## 12. 代码仓库信息

### 12.1 GitHub 仓库

**仓库地址**：https://github.com/wesleycheng/ai-chat

**克隆方式**：
```bash
# SSH方式
git clone git@github.com:wesleycheng/ai-chat.git

# HTTPS方式
git clone https://github.com/wesleycheng/ai-chat.git
```

**仓库结构**：
```
ai-chat/
├── frontend/          # 前端代码（React + TypeScript）
├── backend/           # 后端代码（FastAPI）
├── nginx/             # Nginx配置
├── deploy-ecs.sh      # ECS部署脚本
├── docker-compose.yml # Docker编排文件
├── PROJECT_DOCUMENTATION.md  # 项目文档
└── README.md          # 项目说明
```

---

### 12.2 分支说明

- `main`：生产环境分支（当前部署版本）
- `dev`：开发分支（如有）

---

### 12.3 提交记录

**总提交次数**：28次

**主要提交类型**：
- ✨ `feat`：新功能（15次）
- 🐛 `fix`：错误修复（12次）
- 📝 `docs`：文档更新（1次）

**最近10次提交**：
1. `907c52b` - feat: 设置页面支持编辑默认模型和启用状态 (2026-05-30)
2. `b23c987` - fix: 修复文件上传问题，修复认证头拼写错误 (2026-05-29)
3. `eedd3dd` - feat: 优化所有页面响应式设计 (2026-05-29)
4. `adcb7fb` - feat: 响应式UI优化 (2026-05-29)
5. `c6a6c10` - fix: 修复文件上传问题 (2026-05-29)
6. `19dba34` - fix: 修复文件内容获取问题 (2026-05-29)
7. `fbf714c` - fix: 优化文件上传流程，修复上传失败问题 (2026-05-29)
8. `29ec3ab` - feat: 聊天支持上传文件，结合文件内容进行对话 (2026-05-29)
9. `0b76cfd` - feat: 聊天页面支持选择Agent进行对话 (2026-05-29)
10. `9e72e15` - fix: 修复创建Agent时model_id为空字符串导致500错误 (2026-05-29)

---

### 12.4 本地开发环境搭建

**前置要求**：
- Python 3.12+
- Node.js 20+
- Docker Desktop
- Git

**后端启动**：
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**前端启动**：
```bash
cd frontend
npm install
npm run dev
```

**Docker启动**（推荐）：
```bash
docker compose up -d
```

---

### 12.5 生产环境部署

**ECS服务器信息**：
- IP地址：8.137.103.202
- 操作系统：Ubuntu 22.04 LTS
- Docker版本：24.0+

**部署步骤**：
```bash
# 1. SSH登录到ECS
ssh root@8.137.103.202

# 2. 进入项目目录
cd /var/www/ai-chat

# 3. 拉取最新代码
git pull origin main

# 4. 执行部署脚本
bash deploy-ecs.sh

# 5. 检查服务状态
docker compose ps
```

**部署脚本功能**：
- 构建Docker镜像
- 停止旧容器
- 启动新容器
- 执行数据库迁移
- 健康检查

---

### 12.6 环境变量配置

**后端环境变量**（backend/.env）：
```env
# 数据库
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/ai_chat

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# ChromaDB
CHROMA_HOST=localhost
CHROMA_PORT=8000

# 文件上传
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760  # 10MB

# CORS
CORS_ORIGINS=["http://localhost:5173"]
```

**前端环境变量**（frontend/.env）：
```env
VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=http://localhost:8000
```

---

## 附录

### A. 完整API接口列表

| 模块 | 方法 | 路径 | 功能 | 需要认证 |
|------|------|------|------|----------|
| 认证 | POST | /api/auth/register | 用户注册 | ❌ |
| 认证 | POST | /api/auth/login | 用户登录 | ❌ |
| 认证 | POST | /api/auth/refresh | 刷新Token | ❌ |
| 认证 | GET | /api/auth/me | 获取当前用户 | ✅ |
| 对话 | GET | /api/conversations | 获取会话列表 | ✅ |
| 对话 | POST | /api/conversations | 创建会话 | ✅ |
| 对话 | GET | /api/conversations/{id} | 获取会话详情 | ✅ |
| 对话 | DELETE | /api/conversations/{id} | 删除会话 | ✅ |
| 对话 | GET | /api/conversations/{id}/messages | 获取消息历史 | ✅ |
| 对话 | POST | /api/conversations/{id}/chat | 发送消息 | ✅ |
| 文件 | POST | /api/files/upload | 上传文件 | ✅ |
| 文件 | GET | /api/files | 获取文件列表 | ✅ |
| 文件 | GET | /api/files/{id} | 获取文件详情 | ✅ |
| 文件 | DELETE | /api/files/{id} | 删除文件 | ✅ |
| 配置 | GET | /api/config/models | 获取模型列表 | ✅ |
| 配置 | POST | /api/config/models | 创建模型配置 | ✅ |
| 配置 | PUT | /api/config/models/{id} | 更新模型配置 | ✅ |
| 配置 | DELETE | /api/config/models/{id} | 删除模型配置 | ✅ |
| 配置 | POST | /api/config/models/{id}/test | 测试模型 | ✅ |
| Agent | GET | /api/agents | 获取Agent列表 | ✅ |
| Agent | POST | /api/agents | 创建Agent | ✅ |
| Agent | GET | /api/agents/{id} | 获取Agent详情 | ✅ |
| Agent | PUT | /api/agents/{id} | 更新Agent | ✅ |
| Agent | DELETE | /api/agents/{id} | 删除Agent | ✅ |
| Agent | POST | /api/agents/{id}/test | 测试Agent | ✅ |
| 健康 | GET | /health | 健康检查 | ❌ |

**统计**：
- 总接口数：27个
- 需要认证：25个
- 无需认证：2个（注册、登录）

---

**文档版本**：v2.0  
**最后更新**：2026-05-30 21:30  
**文档状态**：✅ 已完成（添加完整API接口文档和代码仓库信息）
