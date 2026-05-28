import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { Bot, Plus, Settings, ArrowLeft } from 'lucide-react'
import { agentApi } from '../lib/api'

export default function AgentsPage() {
  const navigate = useNavigate()
  const { data: agents, isLoading } = useQuery({
    queryKey: ['agents'],
    queryFn: () => agentApi.list().then(r => r.data),
  })

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
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
          <button className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700">
            <Plus size={18} />
            创建 Agent
          </button>
        </div>

        {isLoading ? (
          <div className="text-center py-12 text-gray-400">加载中...</div>
        ) : agents?.length === 0 ? (
          <div className="text-center py-12 text-gray-400">暂无 Agent</div>
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
                      <div className="font-medium">{agent.name}</div>
                      <div className="text-sm text-gray-400">{agent.description || '无描述'}</div>
                    </div>
                  </div>
                  <button className="p-2 text-gray-400 hover:bg-gray-100 rounded">
                    <Settings size={18} />
                  </button>
                </div>
                <div className="mt-3 flex gap-2 flex-wrap">
                  {agent.tools?.map((tool: string) => (
                    <span key={tool} className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                      {tool}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}