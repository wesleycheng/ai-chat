import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeSanitize from 'rehype-sanitize'
import {
  Send, Plus, Settings, FileText, Bot, LogOut,
  Paperclip, X, Menu, MessageSquare,
  Trash2
} from 'lucide-react'
import { useAuthStore } from '../stores/authStore'
import { useChatStore } from '../stores/chatStore'
import { conversationApi, configApi, agentApi, fileApi } from '../lib/api'

export default function ChatPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { user, logout } = useAuthStore()
  const {
    currentConversationId, setCurrentConversation,
    streamingContent, isStreaming,
    selectedModelId, setSelectedModelId,
    selectedAgentId, setSelectedAgentId
  } = useChatStore()

  const [input, setInput] = useState('')
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  const [uploadingFiles, setUploadingFiles] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // 获取会话列表
  const { data: conversations } = useQuery({
    queryKey: ['conversations'],
    queryFn: () => conversationApi.list().then(r => r.data),
  })

  // 获取模型列表
  const { data: modelsData } = useQuery({
    queryKey: ['models'],
    queryFn: () => configApi.listModels().then(r => r.data),
  })
  const models = modelsData

  // 获取Agent列表
  const { data: agents } = useQuery({
    queryKey: ['agents'],
    queryFn: () => agentApi.list().then(r => r.data),
  })

  // 获取当前会话消息
  const { data: messages } = useQuery({
    queryKey: ['messages', currentConversationId],
    queryFn: () => currentConversationId
      ? conversationApi.getMessages(currentConversationId).then(r => r.data)
      : [],
    enabled: !!currentConversationId,
  })

  // 删除会话
  const deleteConversation = useMutation({
    mutationFn: (id: string) => conversationApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['conversations'] })
      if (currentConversationId) {
        setCurrentConversation('')
      }
    },
  })

  // 创建会话
  const createConversation = useMutation({
    mutationFn: () => conversationApi.create({
      title: selectedAgentId ? undefined : '新对话',
      agent_id: selectedAgentId || undefined,
    }),
    onSuccess: (data) => {
      setCurrentConversation(data.data.id)
      queryClient.invalidateQueries({ queryKey: ['conversations'] })
    },
  })

  // 发送消息
  const sendMessage = useMutation({
    mutationFn: async (content: string) => {
      if (!currentConversationId) return

      // 先上传所有文件
      let fileIds: string[] = []
      if (selectedFiles.length > 0) {
        setUploadingFiles(true)
        try {
          for (const file of selectedFiles) {
            console.log('上传文件:', file.name, file.size)
            const res = await fileApi.upload(file)
            console.log('上传成功:', res.data.id)
            fileIds.push(res.data.id)
          }
        } catch (err) {
          console.error('文件上传失败', err)
          throw err
        } finally {
          setUploadingFiles(false)
        }
      }

      // 使用 fetch 进行 SSE 流式请求
      const response = await fetch(`/api/conversations/${currentConversationId}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${useAuthStore.getState().token}`,
        },
        body: JSON.stringify({
          content,
          stream: true,
          ...(selectedModelId ? { model_id: selectedModelId } : {}),
          ...(selectedAgentId ? { agent_id: selectedAgentId } : {}),
          ...(fileIds.length > 0 ? { file_ids: fileIds } : {}),
        }),
      })

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      return new Promise<string>((resolve) => {
        let fullContent = ''

        const read = async () => {
          if (!reader) return
          const { done, value } = await reader.read()
          if (done) {
            queryClient.invalidateQueries({ queryKey: ['messages', currentConversationId] })
            resolve(fullContent)
            return
          }

          const text = decoder.decode(value)
          const lines = text.split('\n')
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = JSON.parse(line.slice(6))
              if (data.content) {
                fullContent += data.content
              }
            }
          }
          read()
        }
        read()
      })
    },
    onSuccess: () => {
      setSelectedFiles([])
    },
  })

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streamingContent])

  // 移动端切换会话时关闭侧边栏
  useEffect(() => {
    if (window.innerWidth < 768) {
      setSidebarOpen(false)
    }
  }, [currentConversationId])

  // 选择文件
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (!files || files.length === 0) return
    setSelectedFiles(prev => [...prev, ...Array.from(files)])
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  const removeFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index))
  }

  const handleSend = () => {
    if (!input.trim() || isStreaming || uploadingFiles) return
    const content = input.trim()
    setInput('')
    sendMessage.mutate(content)
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const handleSelectConversation = (id: string) => {
    setCurrentConversation(id)
    if (window.innerWidth < 768) {
      setSidebarOpen(false)
    }
  }

  // 侧边栏
  const Sidebar = () => (
    <div className="flex flex-col h-full">
      {/* 头部 */}
      <div className="p-3 border-b border-gray-700/50">
        <button
          onClick={() => createConversation.mutate()}
          className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-primary-600 rounded-xl hover:bg-primary-700 transition-colors font-medium"
        >
          <Plus size={18} />
          <span>新对话</span>
        </button>
      </div>

      {/* 会话列表 */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {conversations?.length === 0 && (
          <div className="text-center text-gray-500 py-8 text-sm">
            暂无对话记录
          </div>
        )}
        {conversations?.map((conv: any) => (
          <div
            key={conv.id}
            className={`group flex items-center gap-2 rounded-xl px-3 py-2.5 cursor-pointer transition-colors ${
              currentConversationId === conv.id
                ? 'bg-gray-700/80'
                : 'hover:bg-gray-800/50'
            }`}
          >
            <button
              onClick={() => handleSelectConversation(conv.id)}
              className="flex-1 text-left truncate text-sm"
            >
              <div className="flex items-center gap-2">
                <MessageSquare size={16} className="text-gray-500 shrink-0" />
                <span className="truncate">{conv.title || '新对话'}</span>
              </div>
            </button>
            <button
              onClick={(e) => {
                e.stopPropagation()
                if (confirm('确定删除此对话？')) {
                  deleteConversation.mutate(conv.id)
                }
              }}
              className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-500/20 rounded transition-all text-red-400"
            >
              <Trash2 size={14} />
            </button>
          </div>
        ))}
      </div>

      {/* 底部用户菜单 */}
      <div className="p-3 border-t border-gray-700/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-primary-600 flex items-center justify-center text-sm font-medium">
              {user?.username?.[0]?.toUpperCase() || 'U'}
            </div>
            <span className="text-sm text-gray-300 hidden md:block">{user?.username}</span>
          </div>
          <div className="flex items-center gap-1">
            <button
              onClick={() => navigate('/files')}
              className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
              title="文件管理"
            >
              <FileText size={18} />
            </button>
            <button
              onClick={() => navigate('/agents')}
              className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
              title="Agent管理"
            >
              <Bot size={18} />
            </button>
            <button
              onClick={() => navigate('/settings')}
              className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
              title="设置"
            >
              <Settings size={18} />
            </button>
            <button
              onClick={handleLogout}
              className="p-2 hover:bg-red-500/20 rounded-lg transition-colors text-red-400"
              title="退出登录"
            >
              <LogOut size={18} />
            </button>
          </div>
        </div>
      </div>
    </div>
  )

  return (
    <div className="h-screen flex bg-gray-50">
      {/* 移动端侧边栏遮罩 */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* 侧边栏 */}
      <aside
        className={`
          fixed md:static inset-y-0 left-0 z-50
          w-72 md:w-64 lg:w-72 bg-gray-900 text-white
          transform transition-transform duration-300 ease-in-out
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
        `}
      >
        <Sidebar />
      </aside>

      {/* 主聊天区 */}
      <main className="flex-1 flex flex-col min-w-0">
        {currentConversationId ? (
          <>
            {/* 顶部栏 */}
            <header className="h-14 md:h-16 bg-white border-b flex items-center px-3 md:px-4 gap-3">
              {/* 移动端菜单按钮 */}
              <button
                onClick={() => setSidebarOpen(true)}
                className="p-2 hover:bg-gray-100 rounded-lg md:hidden"
              >
                <Menu size={20} />
              </button>

              <h1 className="font-medium truncate flex-1">
                {conversations?.find((c: any) => c.id === currentConversationId)?.title || '新对话'}
              </h1>

              {/* 移动端设置按钮 */}
              <button
                onClick={() => setShowSettings(!showSettings)}
                className="p-2 hover:bg-gray-100 rounded-lg md:hidden"
              >
                <Settings size={20} />
              </button>
            </header>

            {/* 消息列表 */}
            <div className="flex-1 overflow-y-auto p-3 md:p-4 space-y-4">
              {messages?.length === 0 && (
                <div className="text-center text-gray-400 py-12">
                  <MessageSquare size={48} className="mx-auto mb-4 opacity-50" />
                  <p>开始发送消息进行对话</p>
                </div>
              )}
              {messages?.map((msg: any) => (
                <div
                  key={msg.id}
                  className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
                >
                  {/* 头像 */}
                  <div className={`shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                    msg.role === 'user'
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-200 text-gray-600'
                  }`}>
                    {msg.role === 'user' ? (
                      user?.username?.[0]?.toUpperCase() || 'U'
                    ) : (
                      <Bot size={16} />
                    )}
                  </div>

                  {/* 消息内容 */}
                  <div
                    className={`max-w-[85%] md:max-w-[75%] rounded-2xl px-4 py-2.5 ${
                      msg.role === 'user'
                        ? 'bg-primary-600 text-white rounded-tr-md'
                        : 'bg-white border border-gray-200 text-gray-800 rounded-tl-md'
                    }`}
                  >
                    {msg.role === 'user' ? (
                      <p className="whitespace-pre-wrap break-words">{msg.content}</p>
                    ) : (
                      <div className="markdown-body prose prose-sm max-w-none">
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          rehypePlugins={[rehypeSanitize]}
                        >
                          {msg.content}
                        </ReactMarkdown>
                      </div>
                    )}
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>

            {/* 模型 & Agent 选择器 - 移动端可折叠 */}
            {showSettings && (
              <div className="bg-white border-t px-3 py-3 space-y-2 md:hidden">
                {models && models.length > 0 && (
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-gray-500 shrink-0">模型：</span>
                    <select
                      value={selectedModelId || ''}
                      onChange={(e) => setSelectedModelId(e.target.value || null)}
                      className="flex-1 text-sm px-2 py-1.5 border rounded-lg bg-white"
                    >
                      <option value="">默认模型</option>
                      {models.map((m: any) => (
                        <option key={m.id} value={m.id}>
                          {m.name}
                        </option>
                      ))}
                    </select>
                  </div>
                )}
                {agents && agents.length > 0 && (
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-gray-500 shrink-0">Agent：</span>
                    <select
                      value={selectedAgentId || ''}
                      onChange={(e) => setSelectedAgentId(e.target.value || null)}
                      className="flex-1 text-sm px-2 py-1.5 border rounded-lg bg-white"
                    >
                      <option value="">不使用</option>
                      {agents.map((a: any) => (
                        <option key={a.id} value={a.id}>
                          {a.name}
                        </option>
                      ))}
                    </select>
                  </div>
                )}
              </div>
            )}

            {/* 桌面端模型 & Agent 选择器 */}
            <div className="hidden md:flex bg-white border-t px-4 py-2 items-center gap-4 flex-wrap">
              {models && models.length > 0 && (
                <div className="flex items-center gap-2">
                  <span className="text-sm text-gray-500">模型：</span>
                  <select
                    value={selectedModelId || ''}
                    onChange={(e) => setSelectedModelId(e.target.value || null)}
                    className="text-sm px-2 py-1 border rounded-lg bg-white"
                  >
                    <option value="">默认模型</option>
                    {models.map((m: any) => (
                      <option key={m.id} value={m.id}>
                        {m.name} ({m.provider})
                      </option>
                    ))}
                  </select>
                </div>
              )}
              {agents && agents.length > 0 && (
                <div className="flex items-center gap-2">
                  <span className="text-sm text-gray-500">Agent：</span>
                  <select
                    value={selectedAgentId || ''}
                    onChange={(e) => setSelectedAgentId(e.target.value || null)}
                    className="text-sm px-2 py-1 border rounded-lg bg-white"
                  >
                    <option value="">不使用</option>
                    {agents.map((a: any) => (
                      <option key={a.id} value={a.id}>
                        {a.name}
                      </option>
                    ))}
                  </select>
                </div>
              )}
            </div>

            {/* 输入区 */}
            <div className="bg-white border-t p-3 md:p-4">
              {/* 已选文件列表 */}
              {selectedFiles.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-3">
                  {selectedFiles.map((file, index) => (
                    <div
                      key={index}
                      className="flex items-center gap-2 px-3 py-1.5 bg-blue-50 text-blue-700 text-sm rounded-lg"
                    >
                      <FileText size={14} />
                      <span className="max-w-[100px] md:max-w-[150px] truncate">{file.name}</span>
                      <button
                        onClick={() => removeFile(index)}
                        className="hover:text-blue-900"
                      >
                        <X size={14} />
                      </button>
                    </div>
                  ))}
                </div>
              )}

              {/* 输入框 */}
              <div className="flex gap-2 md:gap-3">
                <input
                  ref={fileInputRef}
                  type="file"
                  className="hidden"
                  multiple
                  accept=".pdf,.docx,.xlsx,.txt,.md"
                  onChange={handleFileSelect}
                />
                <button
                  onClick={() => fileInputRef.current?.click()}
                  disabled={uploadingFiles}
                  className="shrink-0 p-2.5 md:p-2 border rounded-xl hover:bg-gray-50 disabled:opacity-50 transition-colors"
                  title="选择文件"
                >
                  <Paperclip size={20} className={uploadingFiles ? 'animate-pulse' : ''} />
                </button>
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                  placeholder={uploadingFiles ? "上传文件中..." : "输入消息..."}
                  className="flex-1 px-4 py-2.5 md:py-3 border rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm md:text-base"
                  disabled={isStreaming || uploadingFiles}
                />
                <button
                  onClick={handleSend}
                  disabled={!input.trim() || isStreaming || uploadingFiles}
                  className="shrink-0 p-2.5 md:p-3 bg-primary-600 text-white rounded-xl hover:bg-primary-700 disabled:opacity-50 transition-colors"
                >
                  {uploadingFiles ? (
                    <span className="text-sm">上传中</span>
                  ) : (
                    <Send size={20} />
                  )}
                </button>
              </div>
            </div>
          </>
        ) : (
          /* 空状态 */
          <div className="flex-1 flex flex-col items-center justify-center p-4">
            <div className="w-16 h-16 rounded-2xl bg-primary-100 flex items-center justify-center mb-4">
              <MessageSquare size={32} className="text-primary-600" />
            </div>
            <h2 className="text-xl font-semibold text-gray-800 mb-2">开始新对话</h2>
            <p className="text-gray-500 text-center mb-6 max-w-sm">
              选择左侧对话历史或创建新对话，也可以上传文件进行智能分析
            </p>
            <button
              onClick={() => createConversation.mutate()}
              className="flex items-center gap-2 px-6 py-3 bg-primary-600 text-white rounded-xl hover:bg-primary-700 transition-colors font-medium"
            >
              <Plus size={20} />
              <span>新建对话</span>
            </button>
          </div>
        )}
      </main>
    </div>
  )
}
