import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ArrowLeft, Bot, Plus, Settings, Trash2, X, Check, Zap } from 'lucide-react'
import { agentApi, configApi } from '../lib/api'

const TOOL_OPTIONS = [
  { id: 'file_search', label: '文件搜索', desc: '在上传的文件中检索相关内容' },
  { id: 'web_search', label: '网页搜索', desc: '搜索互联网获取最新信息' },
  { id: 'calculator', label: '计算器', desc: '执行数学计算' },
]

const TOOL_LABELS: Record<string, string> = {
  file_search: '文件搜索',
  web_search: '网页搜索',
  calculator: '计算器',
}

const EMPTY_FORM = {
  name: '',
  description: '',
  system_prompt: '',
  model_id: '',
  tools: [] as string[],
}

export default function AgentsPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  // Modal state
  const [modalOpen, setModalOpen] = useState(false)
  const [editingAgent, setEditingAgent] = useState<any>(null)
  const [form, setForm] = useState(EMPTY_FORM)
  // const [showToolsDropdown, setShowToolsDropdown] = useState(false)

  // Delete confirm
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null)

  // Queries
  const { data: agents, isLoading } = useQuery({
    queryKey: ['agents'],
    queryFn: () => agentApi.list().then(r => r.data?.data?.items ?? []),
  })

  const { data: models } = useQuery({
    queryKey: ['models'],
    queryFn: () => configApi.listModels().then(r => r.data?.data?.items ?? []),
  })

  // Mutations
  const createAgent = useMutation({
    mutationFn: (data: typeof form) => agentApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents'] })
      closeModal()
    },
  })

  const updateAgent = useMutation({
    mutationFn: ({ id, data }: { id: string; data: typeof form }) =>
      agentApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents'] })
      closeModal()
    },
  })

  const deleteAgent = useMutation({
    mutationFn: (id: string) => agentApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents'] })
      setDeleteConfirmId(null)
    },
  })

  // Handlers
  const openCreateModal = () => {
    setEditingAgent(null)
    setForm(EMPTY_FORM)
    setModalOpen(true)
  }

  const openEditModal = (agent: any) => {
    setEditingAgent(agent)
    setForm({
      name: agent.name,
      description: agent.description || '',
      system_prompt: agent.system_prompt,
      model_id: agent.model_id || '',
      tools: agent.tools || [],
    })
    setModalOpen(true)
  }

  const closeModal = () => {
    setModalOpen(false)
    setEditingAgent(null)
    setForm(EMPTY_FORM)
    // setShowToolsDropdown(false)
  }

  const handleSave = () => {
    if (!form.name.trim() || !form.system_prompt.trim()) return
    const payload = {
      ...form,
      model_id: form.model_id || null,
    } as any
    if (editingAgent) {
      updateAgent.mutate({ id: editingAgent.id, data: payload })
    } else {
      createAgent.mutate(payload)
    }
  }

  const toggleTool = (toolId: string) => {
    setForm(prev => ({
      ...prev,
      tools: prev.tools.includes(toolId)
        ? prev.tools.filter(t => t !== toolId)
        : [...prev.tools, toolId],
    }))
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/')}
              className="p-2 hover:bg-gray-200 rounded-lg transition-colors"
              title="返回聊天"
            >
              <ArrowLeft size={20} />
            </button>
            <h1 className="text-2xl font-bold">Agent 管理</h1>
          </div>
          <button
            onClick={openCreateModal}
            className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            <Plus size={18} />
            创建 Agent
          </button>
        </div>

        {/* Agent List */}
        {isLoading ? (
          <div className="text-center py-12 text-gray-400">加载中...</div>
        ) : agents?.length === 0 ? (
          <div className="text-center py-16">
            <Bot size={48} className="mx-auto text-gray-300 mb-4" />
            <div className="text-gray-400 mb-4">暂无 Agent，点击上方按钮创建</div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {agents?.map((agent: any) => (
              <div
                key={agent.id}
                className="p-4 bg-white rounded-lg shadow hover:shadow-md transition"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-primary-100 rounded-lg">
                      <Bot className="text-primary-600" />
                    </div>
                    <div>
                      <div className="font-medium flex items-center gap-2">
                        {agent.name}
                        {agent.is_active ? (
                          <span className="px-1.5 py-0.5 bg-green-100 text-green-600 text-xs rounded">启用</span>
                        ) : (
                          <span className="px-1.5 py-0.5 bg-gray-100 text-gray-500 text-xs rounded">停用</span>
                        )}
                      </div>
                      <div className="text-sm text-gray-400 mt-0.5">
                        {agent.description || '无描述'}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-1">
                    <button
                      onClick={() => openEditModal(agent)}
                      className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded"
                      title="编辑"
                    >
                      <Settings size={16} />
                    </button>
                    {deleteConfirmId === agent.id ? (
                      <div className="flex items-center gap-1">
                        <button
                          onClick={() => deleteAgent.mutate(agent.id)}
                          className="p-1.5 text-white bg-red-500 rounded hover:bg-red-600"
                          title="确认删除"
                        >
                          <Check size={14} />
                        </button>
                        <button
                          onClick={() => setDeleteConfirmId(null)}
                          className="p-1.5 text-gray-400 hover:bg-gray-200 rounded"
                          title="取消"
                        >
                          <X size={14} />
                        </button>
                      </div>
                    ) : (
                      <button
                        onClick={() => setDeleteConfirmId(agent.id)}
                        className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded"
                        title="删除"
                      >
                        <Trash2 size={16} />
                      </button>
                    )}
                  </div>
                </div>

                {/* System prompt preview */}
                <div className="mt-3 text-sm text-gray-500 bg-gray-50 rounded-md p-2 line-clamp-2">
                  {agent.system_prompt}
                </div>

                {/* Tools */}
                <div className="mt-3 flex gap-2 flex-wrap">
                  {agent.tools?.length > 0 ? (
                    agent.tools.map((tool: string) => (
                      <span key={tool} className="px-2 py-1 bg-blue-50 text-blue-600 text-xs rounded flex items-center gap-1">
                        <Zap size={12} />
                        {TOOL_LABELS[tool] || tool}
                      </span>
                    ))
                  ) : (
                    <span className="text-xs text-gray-400">未配置工具</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Create / Edit Modal */}
      {modalOpen && (
        <div
          className="fixed inset-0 bg-black/40 flex items-center justify-center z-50"
          onClick={closeModal}
        >
          <div
            className="bg-white rounded-xl shadow-xl p-6 w-full max-w-lg max-h-[90vh] overflow-y-auto"
            onClick={e => e.stopPropagation()}
          >
            <h3 className="text-lg font-semibold mb-4">
              {editingAgent ? '编辑 Agent' : '创建新 Agent'}
            </h3>

            <div className="space-y-4">
              {/* Name */}
              <div>
                <label className="block text-sm text-gray-600 mb-1">名称 <span className="text-red-500">*</span></label>
                <input
                  type="text"
                  value={form.name}
                  onChange={e => setForm(prev => ({ ...prev, name: e.target.value }))}
                  className="w-full px-3 py-2 border rounded-lg"
                  placeholder="如：文档助手"
                />
              </div>

              {/* Description */}
              <div>
                <label className="block text-sm text-gray-600 mb-1">描述</label>
                <input
                  type="text"
                  value={form.description}
                  onChange={e => setForm(prev => ({ ...prev, description: e.target.value }))}
                  className="w-full px-3 py-2 border rounded-lg"
                  placeholder="简要描述 Agent 的用途"
                />
              </div>

              {/* Model */}
              <div>
                <label className="block text-sm text-gray-600 mb-1">关联模型</label>
                <select
                  value={form.model_id}
                  onChange={e => setForm(prev => ({ ...prev, model_id: e.target.value }))}
                  className="w-full px-3 py-2 border rounded-lg"
                >
                  <option value="">使用默认模型</option>
                  {models?.map((model: any) => (
                    <option key={model.id} value={model.id}>
                      {model.name} ({model.provider})
                    </option>
                  ))}
                </select>
              </div>

              {/* System Prompt */}
              <div>
                <label className="block text-sm text-gray-600 mb-1">系统提示词 <span className="text-red-500">*</span></label>
                <textarea
                  value={form.system_prompt}
                  onChange={e => setForm(prev => ({ ...prev, system_prompt: e.target.value }))}
                  className="w-full px-3 py-2 border rounded-lg min-h-[120px] resize-y"
                  placeholder="你是一个专业的AI助手，擅长..."
                  rows={5}
                />
              </div>

              {/* Tools */}
              <div>
                <label className="block text-sm text-gray-600 mb-1">工具能力</label>
                <div className="space-y-2">
                  {TOOL_OPTIONS.map(tool => (
                    <label
                      key={tool.id}
                      className={`flex items-center gap-3 p-3 border rounded-lg cursor-pointer transition ${
                        form.tools.includes(tool.id)
                          ? 'border-primary-500 bg-primary-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={form.tools.includes(tool.id)}
                        onChange={() => toggleTool(tool.id)}
                        className="accent-primary-600"
                      />
                      <div>
                        <div className="text-sm font-medium">{tool.label}</div>
                        <div className="text-xs text-gray-400">{tool.desc}</div>
                      </div>
                    </label>
                  ))}
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex justify-end gap-2 mt-6">
              <button
                onClick={closeModal}
                className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg"
              >
                取消
              </button>
              <button
                onClick={handleSave}
                disabled={!form.name.trim() || !form.system_prompt.trim() || createAgent.isPending || updateAgent.isPending}
                className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
              >
                {createAgent.isPending || updateAgent.isPending ? '保存中...' : editingAgent ? '保存' : '创建'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}


