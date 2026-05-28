import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Trash2, Pencil, X, Check } from 'lucide-react'
import { configApi } from '../lib/api'

const providerDefaults: Record<string, { api_base: string; model_name: string }> = {
  deepseek: { api_base: 'https://api.deepseek.com/v1', model_name: 'deepseek-chat' },
  openai: { api_base: 'https://api.openai.com/v1', model_name: 'gpt-4o' },
  ollama: { api_base: 'http://localhost:11434/v1', model_name: 'llama3' },
  anthropic: { api_base: 'https://api.anthropic.com/v1', model_name: 'claude-3-5-sonnet-20241022' },
}

export default function SettingsPage() {
  const queryClient = useQueryClient()

  // modal 状态：null=关闭，'add'=新增，{id,...}=编辑
  const [modalMode, setModalMode] = useState<'add' | null>(null)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [form, setForm] = useState({ name: '', provider: 'deepseek', api_base: '', api_key: '', model_name: '' })

  // 删除确认
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null)

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
    setForm({ name: '', provider: 'deepseek', api_base: '', api_key: '', model_name: '' })
    setEditingId(null)
    setModalMode('add')
  }

  const openEditModal = (model: any) => {
    setForm({
      name: model.name,
      provider: model.provider,
      api_base: model.api_base,
      api_key: '',  // 不回填 key
      model_name: model.model_name || '',
    })
    setEditingId(model.id)
    setModalMode('add')  // reuse same modal
  }

  const closeModal = () => {
    setModalMode(null)
    setEditingId(null)
    setForm({ name: '', provider: 'deepseek', api_base: '', api_key: '', model_name: '' })
  }

  const handleProviderChange = (provider: string) => {
    const defaults = providerDefaults[provider] || { api_base: '', model_name: '' }
    setForm(prev => ({ ...prev, provider, api_base: defaults.api_base, model_name: defaults.model_name }))
  }

  const handleSave = () => {
    if (editingId) {
      const payload: Record<string, unknown> = {}
      if (form.name) payload.name = form.name
      if (form.provider) payload.provider = form.provider
      if (form.api_base) payload.api_base = form.api_base
      if (form.api_key) payload.api_key = form.api_key
      if (form.model_name) payload.model_name = form.model_name
      updateModel.mutate({ id: editingId, payload })
    } else {
      addModel.mutate(form)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold mb-6">设置</h1>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold">模型配置</h2>
            <button
              onClick={openAddModal}
              className="flex items-center gap-2 px-3 py-1.5 bg-primary-600 text-white rounded-lg hover:bg-primary-700 text-sm"
            >
              <Plus size={16} />
              添加模型
            </button>
          </div>

          {isLoading ? (
            <div className="text-center py-8 text-gray-400">加载中...</div>
          ) : !models || models.length === 0 ? (
            <div className="text-center py-8 text-gray-400">暂无模型配置，点击上方按钮添加</div>
          ) : (
            <div className="space-y-2">
              {models.map((model: any) => (
                <div
                  key={model.id}
                  className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50"
                >
                  <div className="flex-1 min-w-0">
                    <div className="font-medium flex items-center gap-2">
                      {model.name}
                      {model.is_default && (
                        <span className="px-2 py-0.5 bg-primary-100 text-primary-600 text-xs rounded">默认</span>
                      )}
                    </div>
                    <div className="text-sm text-gray-400 truncate">
                      {model.provider} · {model.model_name}
                    </div>
                    <div className="text-xs text-gray-400 mt-0.5">{model.api_key_masked}</div>
                  </div>
                  <div className="flex items-center gap-1 ml-2">
                    <button
                      onClick={() => openEditModal(model)}
                      className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded"
                      title="编辑"
                    >
                      <Pencil size={16} />
                    </button>
                    {deleteConfirmId === model.id ? (
                      <div className="flex items-center gap-1">
                        <button
                          onClick={() => deleteModel.mutate(model.id)}
                          className="p-1 text-white bg-red-500 rounded hover:bg-red-600"
                          title="确认删除"
                        >
                          <Check size={14} />
                        </button>
                        <button
                          onClick={() => setDeleteConfirmId(null)}
                          className="p-1 text-gray-400 hover:bg-gray-200 rounded"
                          title="取消"
                        >
                          <X size={14} />
                        </button>
                      </div>
                    ) : (
                      <button
                        onClick={() => setDeleteConfirmId(model.id)}
                        className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded"
                        title="删除"
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
      </div>

      {/* 新增/编辑弹窗 */}
      {modalMode && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50" onClick={closeModal}>
          <div className="bg-white rounded-xl shadow-xl p-6 w-full max-w-lg" onClick={e => e.stopPropagation()}>
            <h3 className="text-lg font-semibold mb-4">{editingId ? '编辑模型' : '添加新模型'}</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-600 mb-1">名称</label>
                <input
                  type="text"
                  value={form.name}
                  onChange={e => setForm(prev => ({ ...prev, name: e.target.value }))}
                  className="w-full px-3 py-2 border rounded-lg"
                  placeholder="我的 DeepSeek"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-600 mb-1">提供商</label>
                <select
                  value={form.provider}
                  onChange={e => handleProviderChange(e.target.value)}
                  className="w-full px-3 py-2 border rounded-lg"
                >
                  <option value="deepseek">DeepSeek</option>
                  <option value="openai">OpenAI</option>
                  <option value="anthropic">Anthropic</option>
                  <option value="ollama">Ollama（本地）</option>
                  <option value="custom">自定义</option>
                </select>
              </div>
              <div>
                <label className="block text-sm text-gray-600 mb-1">API 端点</label>
                <input
                  type="text"
                  value={form.api_base}
                  onChange={e => setForm(prev => ({ ...prev, api_base: e.target.value }))}
                  className="w-full px-3 py-2 border rounded-lg text-sm"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-600 mb-1">模型 ID（API 真实名称）</label>
                <input
                  type="text"
                  value={form.model_name}
                  onChange={e => setForm(prev => ({ ...prev, model_name: e.target.value }))}
                  className="w-full px-3 py-2 border rounded-lg text-sm"
                  placeholder="如 deepseek-chat"
                />
              </div>
              <div className="col-span-2">
                <label className="block text-sm text-gray-600 mb-1">
                  API Key {editingId && '（留空保持不变）'}
                </label>
                <input
                  type="password"
                  value={form.api_key}
                  onChange={e => setForm(prev => ({ ...prev, api_key: e.target.value }))}
                  className="w-full px-3 py-2 border rounded-lg"
                  placeholder="sk-..."
                />
              </div>
            </div>
            <div className="flex justify-end gap-2 mt-6">
              <button
                onClick={closeModal}
                className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg"
              >
                取消
              </button>
              <button
                onClick={handleSave}
                disabled={!form.name || (!editingId && !form.api_key)}
                className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
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
