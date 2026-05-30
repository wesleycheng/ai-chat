import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ArrowLeft, Plus, Trash2, Pencil, X, Check, Cpu, ChevronDown, ChevronUp } from 'lucide-react'
import { configApi } from '../lib/api'

const providerDefaults: Record<string, { api_base: string; model_name: string }> = {
  deepseek: { api_base: 'https://api.deepseek.com/v1', model_name: 'deepseek-chat' },
  openai: { api_base: 'https://api.openai.com/v1', model_name: 'gpt-4o' },
  ollama: { api_base: 'http://localhost:11434/v1', model_name: 'llama3' },
  anthropic: { api_base: 'https://api.anthropic.com/v1', model_name: 'claude-3-5-sonnet-20241022' },
}

export default function SettingsPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const [modalMode, setModalMode] = useState<'add' | null>(null)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [form, setForm] = useState({ name: '', provider: 'deepseek', api_base: '', api_key: '', model_name: '', is_default: false, is_active: true })
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null)
  const [expanded, setExpanded] = useState(false)

  const { data: models, isLoading } = useQuery({
    queryKey: ['models'],
    queryFn: () => configApi.listModels().then(r => r.data),
  })

  const addModel = useMutation({
    mutationFn: (data: typeof form) => configApi.createModel(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['models'] })
      closeModal()
    },
  })

  const updateModel = useMutation({
    mutationFn: (data: { id: string; payload: Record<string, unknown> }) =>
      configApi.updateModel(data.id, data.payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['models'] })
      closeModal()
    },
  })

  const deleteModel = useMutation({
    mutationFn: (id: string) => configApi.deleteModel(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['models'] })
      setDeleteConfirmId(null)
    },
  })

  const openAddModal = () => {
    setForm({ name: '', provider: 'deepseek', api_base: '', api_key: '', model_name: '', is_default: false, is_active: true })
    setEditingId(null)
    setModalMode('add')
  }

  const openEditModal = (model: any) => {
    setForm({
      name: model.name,
      provider: model.provider,
      api_base: model.api_base,
      api_key: '',
      model_name: model.model_name || '',
      is_default: model.is_default || false,
      is_active: model.is_active !== false,
    })
    setEditingId(model.id)
    setModalMode('add')
  }

  const closeModal = () => {
    setModalMode(null)
    setEditingId(null)
    setForm({ name: '', provider: 'deepseek', api_base: '', api_key: '', model_name: '', is_default: false, is_active: true })
  }

  const handleProviderChange = (provider: string) => {
    const defaults = providerDefaults[provider] || { api_base: '', model_name: '' }
    setForm(prev => ({ ...prev, provider, api_base: defaults.api_base, model_name: defaults.model_name }))
  }

  const handleSave = () => {
    const payload: Record<string, unknown> = {
      name: form.name,
      provider: form.provider,
      api_base: form.api_base,
      model_name: form.model_name,
      is_default: form.is_default,
      is_active: form.is_active,
    }
    if (form.api_key) {
      payload.api_key = form.api_key
    }
    if (editingId) {
      updateModel.mutate({ id: editingId, payload })
    } else {
      addModel.mutate(form)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-3xl mx-auto px-4 py-6">
        {/* 顶部栏 */}
        <div className="flex items-center gap-3 mb-6">
          <button
            onClick={() => navigate('/')}
            className="p-2 hover:bg-gray-200 rounded-xl transition-colors"
          >
            <ArrowLeft size={20} />
          </button>
          <h1 className="text-xl md:text-2xl font-bold">设置</h1>
        </div>

        {/* 模型配置卡片 */}
        <div className="bg-white rounded-2xl shadow-sm border overflow-hidden">
          <button
            onClick={() => setExpanded(!expanded)}
            className="w-full flex items-center justify-between p-4 md:p-5 hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-primary-100 flex items-center justify-center">
                <Cpu size={20} className="text-primary-600" />
              </div>
              <div className="text-left">
                <h2 className="font-semibold">模型配置</h2>
                <p className="text-sm text-gray-500">{models?.length || 0} 个模型</p>
              </div>
            </div>
            {expanded ? <ChevronUp size={20} className="text-gray-400" /> : <ChevronDown size={20} className="text-gray-400" />}
          </button>

          {expanded && (
            <div className="border-t px-4 pb-4 md:px-5 md:pb-5">
              <div className="flex justify-end py-3">
                <button
                  onClick={openAddModal}
                  className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-xl hover:bg-primary-700 text-sm font-medium transition-colors"
                >
                  <Plus size={16} />
                  添加模型
                </button>
              </div>

              {isLoading ? (
                <div className="text-center py-8 text-gray-400">加载中...</div>
              ) : !models || models.length === 0 ? (
                <div className="text-center py-8 text-gray-400">
                  暂无模型配置，点击上方按钮添加
                </div>
              ) : (
                <div className="space-y-2">
                  {models.map((model: any) => (
                    <div
                      key={model.id}
                      className="flex items-center gap-3 p-3 border rounded-xl hover:bg-gray-50 transition-colors"
                    >
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="font-medium">{model.name}</span>
                          {model.is_default && (
                            <span className="px-2 py-0.5 bg-primary-100 text-primary-600 text-xs rounded-full">默认</span>
                          )}
                          {!model.is_active && (
                            <span className="px-2 py-0.5 bg-gray-100 text-gray-500 text-xs rounded-full">已禁用</span>
                          )}
                        </div>
                        <div className="text-sm text-gray-500 truncate mt-0.5">
                          {model.provider} · {model.model_name}
                        </div>
                        <div className="text-xs text-gray-400 mt-0.5">{model.api_key_masked}</div>
                      </div>
                      <div className="flex items-center gap-1 shrink-0">
                        <button
                          onClick={() => openEditModal(model)}
                          className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                        >
                          <Pencil size={16} />
                        </button>
                        {deleteConfirmId === model.id ? (
                          <div className="flex items-center gap-1">
                            <button
                              onClick={() => deleteModel.mutate(model.id)}
                              className="p-2 text-white bg-red-500 rounded-lg hover:bg-red-600"
                            >
                              <Check size={16} />
                            </button>
                            <button
                              onClick={() => setDeleteConfirmId(null)}
                              className="p-2 text-gray-400 hover:bg-gray-200 rounded-lg"
                            >
                              <X size={16} />
                            </button>
                          </div>
                        ) : (
                          <button
                            onClick={() => setDeleteConfirmId(model.id)}
                            className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                          >
                            <Trash2 size={16} />
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* 弹窗 */}
      {modalMode && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4" onClick={closeModal}>
          <div className="bg-white rounded-2xl shadow-xl p-5 md:p-6 w-full max-w-lg" onClick={e => e.stopPropagation()}>
            <h3 className="text-lg font-semibold mb-5">{editingId ? '编辑模型' : '添加新模型'}</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">名称</label>
                <input
                  type="text"
                  value={form.name}
                  onChange={e => setForm(prev => ({ ...prev, name: e.target.value }))}
                  className="w-full px-3 py-2.5 border rounded-xl focus:ring-2 focus:ring-primary-500"
                  placeholder="我的 DeepSeek"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">提供商</label>
                <select
                  value={form.provider}
                  onChange={e => handleProviderChange(e.target.value)}
                  className="w-full px-3 py-2.5 border rounded-xl focus:ring-2 focus:ring-primary-500"
                >
                  <option value="deepseek">DeepSeek</option>
                  <option value="openai">OpenAI</option>
                  <option value="anthropic">Anthropic</option>
                  <option value="ollama">Ollama（本地）</option>
                  <option value="custom">自定义</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">API 端点</label>
                <input
                  type="text"
                  value={form.api_base}
                  onChange={e => setForm(prev => ({ ...prev, api_base: e.target.value }))}
                  className="w-full px-3 py-2.5 border rounded-xl focus:ring-2 focus:ring-primary-500 text-sm"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">模型 ID</label>
                <input
                  type="text"
                  value={form.model_name}
                  onChange={e => setForm(prev => ({ ...prev, model_name: e.target.value }))}
                  className="w-full px-3 py-2.5 border rounded-xl focus:ring-2 focus:ring-primary-500 text-sm"
                  placeholder="如 deepseek-chat"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  API Key {editingId && <span className="text-gray-400">（留空保持不变）</span>}
                </label>
                <input
                  type="password"
                  value={form.api_key}
                  onChange={e => setForm(prev => ({ ...prev, api_key: e.target.value }))}
                  className="w-full px-3 py-2.5 border rounded-xl focus:ring-2 focus:ring-primary-500"
                  placeholder="sk-..."
                />
              </div>
              <div className="flex items-center gap-4">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={form.is_default}
                    onChange={e => setForm(prev => ({ ...prev, is_default: e.target.checked }))}
                    className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
                  />
                  <span className="text-sm">设为默认模型</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={form.is_active}
                    onChange={e => setForm(prev => ({ ...prev, is_active: e.target.checked }))}
                    className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
                  />
                  <span className="text-sm">启用</span>
                </label>
              </div>
            </div>
            <div className="flex gap-2 mt-6">
              <button
                onClick={closeModal}
                className="flex-1 px-4 py-2.5 text-gray-600 hover:bg-gray-100 rounded-xl transition-colors"
              >
                取消
              </button>
              <button
                onClick={handleSave}
                disabled={!form.name || (!editingId && !form.api_key)}
                className="flex-1 px-4 py-2.5 bg-primary-600 text-white rounded-xl hover:bg-primary-700 disabled:opacity-50 transition-colors font-medium"
              >
                {editingId ? '保存' : '创建'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
