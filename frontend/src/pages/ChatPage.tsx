import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeSanitize from 'rehype-sanitize'
import { Send, Plus, Settings, FileText, Bot, LogOut, Paperclip, X } from 'lucide-react'
import { useAuthStore } from '../stores/authStore'
import { useChatStore } from '../stores/chatStore'
import { conversationApi, configApi, agentApi, fileApi } from '../lib/api'

export default function ChatPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { user, logout } = useAuthStore()
  const { currentConversationId, setCurrentConversation, streamingContent, isStreaming, selectedModelId, setSelectedModelId, selectedAgentId, setSelectedAgentId } = useChatStore()
  
  const [input, setInput] = useState('')
  const [attachedFiles, setAttachedFiles] = useState<{ id: string; name: string }[]>([])
  const [uploadingFile, setUploadingFile] = useState(false)
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
      const fileIds = attachedFiles.length > 0 ? attachedFiles.map(f => f.id) : undefined
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
          ...(fileIds ? { file_ids: fileIds } : {}),
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
    onSettled: () => {
      setAttachedFiles([])
    },
  })

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streamingContent])

  // 上传文件
  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (!files || files.length === 0) return
    setUploadingFile(true)
    try {
      for (const file of files) {
        const res = await fileApi.upload(file)
        setAttachedFiles(prev => [...prev, { id: res.data.id, name: res.data.filename }])
      }
    } catch (err) {
      console.error('文件上传失败', err)
    } finally {
      setUploadingFile(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  const removeFile = (fileId: string) => {
    setAttachedFiles(prev => prev.filter(f => f.id !== fileId))
  }

  const handleSend = () => {
    if (!input.trim() || isStreaming) return
    
    const content = input.trim()
    setInput('')
    sendMessage.mutate(content)
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="h-screen flex">
      {/* 侧边栏 */}
      <aside className="w-64 bg-gray-900 text-white flex flex-col">
        <div className="p-4 border-b border-gray-700">
          <button
            onClick={() => createConversation.mutate()}
            className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-primary-600 rounded-lg hover:bg-primary-700"
          >
            <Plus size={18} />
            新建对话
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-2">
          {conversations?.map((conv: any) => (
            <button
              key={conv.id}
              onClick={() => setCurrentConversation(conv.id)}
              className={`w-full text-left px-3 py-2 rounded-lg mb-1 truncate ${
                currentConversationId === conv.id
                  ? 'bg-gray-700'
                  : 'hover:bg-gray-800'
              }`}
            >
              {conv.title || '新对话'}
            </button>
          ))}
        </div>

        <div className="p-4 border-t border-gray-700">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-400">{user?.username}</span>
            <div className="flex gap-2">
              <button onClick={() => navigate('/files')} className="p-1 hover:bg-gray-700 rounded">
                <FileText size={18} />
              </button>
              <button onClick={() => navigate('/agents')} className="p-1 hover:bg-gray-700 rounded">
                <Bot size={18} />
              </button>
              <button onClick={() => navigate('/settings')} className="p-1 hover:bg-gray-700 rounded">
                <Settings size={18} />
              </button>
              <button onClick={handleLogout} className="p-1 hover:bg-gray-700 rounded">
                <LogOut size={18} />
              </button>
            </div>
          </div>
        </div>
      </aside>

      {/* 主聊天区 */}
      <main className="flex-1 flex flex-col bg-white">
        {currentConversationId ? (
          <>
            {/* 消息列表 */}
            <div className="flex-1 overflow-y-auto p-4">
              {messages?.map((msg: any) => (
                <div
                  key={msg.id}
                  className={`mb-4 ${msg.role === 'user' ? 'text-right' : ''}`}
                >
                  <div
                    className={`inline-block max-w-[80%] px-4 py-2 rounded-lg ${
                      msg.role === 'user'
                        ? 'bg-primary-600 text-white'
                        : 'bg-gray-100'
                    }`}
                  >
                    {msg.role === 'user' ? (
                      msg.content
                    ) : (
                      <div className="markdown-body">
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

            {/* 模型 & Agent 选择器 */}
            <div className="border-t px-4 py-2 flex items-center gap-3 flex-wrap">
              {models && models.length > 0 && (
                <>
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
                </>
              )}
              {agents && agents.length > 0 && (
                <>
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
                </>
              )}
            </div>

            {/* 输入区 */}
            <div className="border-t p-4">
              {/* 已选文件列表 */}
              {attachedFiles.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-2">
                  {attachedFiles.map(f => (
                    <div key={f.id} className="flex items-center gap-1 px-2 py-1 bg-blue-50 text-blue-700 text-sm rounded-lg">
                      <FileText size={14} />
                      <span className="max-w-[120px] truncate">{f.name}</span>
                      <button onClick={() => removeFile(f.id)} className="ml-1 hover:text-blue-900">
                        <X size={14} />
                      </button>
                    </div>
                  ))}
                </div>
              )}
              <div className="flex gap-2">
                <input
                  ref={fileInputRef}
                  type="file"
                  className="hidden"
                  multiple
                  accept=".pdf,.docx,.xlsx,.txt,.md,.jpg,.jpeg,.png"
                  onChange={handleFileSelect}
                />
                <button
                  onClick={() => fileInputRef.current?.click()}
                  disabled={uploadingFile}
                  className="px-3 py-2 border rounded-lg hover:bg-gray-50 disabled:opacity-50"
                  title="上传文件"
                >
                  <Paperclip size={18} className={uploadingFile ? 'animate-pulse' : ''} />
                </button>
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                  placeholder="输入消息..."
                  className="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  disabled={isStreaming}
                />
                <button
                  onClick={handleSend}
                  disabled={!input.trim() || isStreaming}
                  className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
                >
                  <Send size={18} />
                </button>
              </div>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-400">
            选择或创建一个对话开始聊天
          </div>
        )}
      </main>
    </div>
  )
}