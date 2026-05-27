import { useQuery } from '@tanstack/react-query'
import { Upload, FileText, Trash2 } from 'lucide-react'
import { fileApi } from '../lib/api'

export default function FilesPage() {
  const { data: files, isLoading } = useQuery({
    queryKey: ['files'],
    queryFn: () => fileApi.list().then(r => r.data),
  })

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold">文件管理</h1>
          <button className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700">
            <Upload size={18} />
            上传文件
          </button>
        </div>

        {isLoading ? (
          <div className="text-center py-12 text-gray-400">加载中...</div>
        ) : files?.length === 0 ? (
          <div className="text-center py-12 text-gray-400">暂无文件</div>
        ) : (
          <div className="space-y-2">
            {files?.map((file: any) => (
              <div
                key={file.id}
                className="flex items-center justify-between p-4 bg-white rounded-lg shadow"
              >
                <div className="flex items-center gap-3">
                  <FileText className="text-gray-400" />
                  <div>
                    <div className="font-medium">{file.filename}</div>
                    <div className="text-sm text-gray-400">
                      {file.file_size ? `${(file.file_size / 1024).toFixed(1)} KB` : '-'}
                      {' · '}
                      状态: {file.parse_status}
                    </div>
                  </div>
                </div>
                <button className="p-2 text-red-500 hover:bg-red-50 rounded">
                  <Trash2 size={18} />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}