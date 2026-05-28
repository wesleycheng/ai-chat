import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Trash2 } from 'lucide-react'
import { configApi } from '../lib/api'

export default function SettingsPage() {
  const queryClient = useQueryClient()
  const [showAddModel, setShowAddModel] = useState(false)
  const [newModel, setNewModel] = useState({
    name: '',
    provider: 'deepseek',
    api_base: '',
    api_key: '',
    model_name: '',
  })

  const { data: models, isLoading } = useQuery({
    queryKey: ['models'],
    queryFn: () => configApi.listModels().then(r => r.data),
  })

  const addModel = useMutation({
    mutationFn: (data: typeof newModel) => configApi.createModel(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['models'] })
      setShowAddModel(false)
      setNewModel({ name: '', provider: 'deepseek', api_base: '', api_key: '', model_name: '' })
    },
  })

  const deleteModel = useMutation({
    mutationFn: (id: string) => configApi.deleteModel(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['models'] }),
  })

  const providerDefaults: Record<string, { api_base: string; model_name: string }> = {
    deepseek: { api_base: 'https://api.deepseek.com/v1', model_name: 'deepseek-chat' },
    openai: { api_base: 'https://api.openai.com/v1', model_name: 'gpt-4o' },
    ollama: { api_base: 'http://localhost:11434/v1', model_name: 'llama3' },
  }

  const handleProviderChange = (provider: string) => {
    const defaults = providerDefaults[provider] || { api_base: '', model_name: '' }
    setNewModel(prev => ({
      ...prev,
      provider,
      api_base: defaults.api_base,
      model_name: defaults.model_name,
    }))
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold mb-6">设置</h1>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold">模型配置</h2>
            <button
              onClick={() => setShowAddModel(true)}
              className="flex items-center gap-2 px-3 py-1.5 bg-primary-600 text-white rounded-lg hover:bg-primary-700 text-sm"
            >
              <Plus size={16} />
              添加模型
            </button>
          </div>

          {showAddModel && (
            <div className="mb-6 p-4 border rounded-lg bg-gray-50">
              <h3 className="font-medium mb-3">添加新模型</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-600 mb-1">名称</label>
                  <input
                    type="text"
                    value={newModel.name}
                    onChange={e => setNewModel(prev => ({ ...prev, name: e.target.value }))}
                    className="w-full px-3 py-2 border rounded-lg"
                    placeholder="我的 DeepSeek"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-600 mb-1">提供商</label>
                  <select
                    value={newModel.provider}
                    onChange={e => handleProviderChange(e.target.value)}
                    className="w-full px-3 py-2 border rounded-lg"
                  >
                    <option value="deepseek">DeepSeek</option>
                    <option value="openai">OpenAI</option>
                    <option value="ollama">Ollama (本地)</option>
                    <option value="custom">自定义</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm text-gray-600 mb-1">API 端点</label>
                  <input
                    type="text"
                    value={newModel.api_base}
                    onChange={e => setNewModel(prev => ({ ...prev, api_base: e.target.value }))}
                    className="w-full px-3 py-2 border rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-600 mb-1">模型名称</label>
                  <input
                    type="text"
                    value={newModel.model_name}
                    onChange={e => setNewModel(prev => ({ ...prev, model_name: e.target.value }))}
                    className="w-full px-3 py-2 border rounded-lg"
                  />
                </div>
                <div className="col-span-2">
                  <label className="block text-sm text-gray-600 mb-1">API Key</label>
                  <input
                    type="password"
                    value={newModel.api_key}
                    onChange={e => setNewModel(prev => ({ ...prev, api_key: e.target.value }))}
                    className="w-full px-3 py-2 border rounded-lg"
                    placeholder="sk-..."
                  />
                </div>
              </div>
              <div className="flex justify-end gap-2 mt-4">
                <button
                  onClick={() => setShowAddModel(false)}
                  className="px-3 py-1.5 text-gray-600 hover:bg-gray-200 rounded-lg"
                >
                  取消
                </button>
                <button
                  onClick={() => addModel.mutate(newModel)}
                  disabled={!newModel.name || !newModel.api_key}
                  className="px-3 py-1.5 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
                >
                  保存
                </button>
              </div>
            </div>
          )}

          {isLoading ? (
            <div className="text-center py-8 text-gray-400">加载中...</div>
          ) : models?.length === 0 ? (
            <div className="text-center py-8 text-gray-400">暂无模型配置</div>
          ) : (
            <div className="space-y-2">
              {models?.map((model: any) => (
                <div
                  key={model.id}
                  className="flex items-center justify-between p-3 border rounded-lg"
                >
                  <div>
                    <div className="font-medium flex items-center gap-2">
                      {model.name}
                      {model.is_default && (
                        <span className="px-2 py-0.5 bg-primary-100 text-primary-600 text-xs rounded">默认</span>
                      )}
                    </div>
                    <div className="text-sm text-gray-400">
                      {model.provider} · {model.model_name}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-400">{model.api_key_masked}</span>
                    <button
                      onClick={() => deleteModel.mutate(model.id)}
                      className="p-1.5 text-red-500 hover:bg-red-50 rounded"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}