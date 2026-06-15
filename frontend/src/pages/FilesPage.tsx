import { useState, useRef } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { FileText, Trash2, ArrowLeft, Plus, AlertCircle, CheckCircle } from 'lucide-react'
import { fileApi } from '../lib/api'

export default function FilesPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState('')

  const { data: files, isLoading } = useQuery({
    queryKey: ['files'],
    queryFn: () => fileApi.list().then(r => r.data?.data?.items ?? []),
  })

  const deleteFile = useMutation({
    mutationFn: (id: string) => fileApi.delete(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['files'] }),
  })

  const uploadFile = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData()
      formData.append('file', file)
      return fileApi.upload({ file, formData } as any)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['files'] })
      setUploading(false)
      setUploadProgress('')
    },
    onError: () => {
      setUploading(false)
      setUploadProgress('')
    },
  })

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const inputFiles = e.target.files
    if (!inputFiles || inputFiles.length === 0) return

    setUploading(true)
    for (let i = 0; i < inputFiles.length; i++) {
      setUploadProgress(`上传中 (${i + 1}/${inputFiles.length})`)
      try {
        await uploadFile.mutateAsync(inputFiles[i])
      } catch (err) {
        console.error('上传失败:', err)
      }
    }
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded-full"><CheckCircle size={12} /> 已解析</span>
      case 'failed':
        return <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-red-100 text-red-700 text-xs rounded-full"><AlertCircle size={12} /> 失败</span>
      default:
        return <span className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded-full">待处理</span>
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-6">
        {/* 顶部栏 */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/')}
              className="p-2 hover:bg-gray-200 rounded-xl transition-colors"
            >
              <ArrowLeft size={20} />
            </button>
            <h1 className="text-xl md:text-2xl font-bold">文件管理</h1>
          </div>
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
            className="flex items-center gap-2 px-4 py-2.5 bg-primary-600 text-white rounded-xl hover:bg-primary-700 disabled:opacity-50 transition-colors"
          >
            {uploading ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span className="text-sm">{uploadProgress}</span>
              </>
            ) : (
              <>
                <Plus size={18} />
                <span>上传文件</span>
              </>
            )}
          </button>
          <input
            ref={fileInputRef}
            type="file"
            className="hidden"
            multiple
            accept=".pdf,.docx,.xlsx,.txt,.md,.csv"
            onChange={handleFileSelect}
          />
        </div>

        {/* 文件列表 */}
        <div className="bg-white rounded-2xl shadow-sm border overflow-hidden">
          {isLoading ? (
            <div className="text-center py-12 text-gray-400">加载中...</div>
          ) : !files || files.length === 0 ? (
            <div className="text-center py-12">
              <FileText size={48} className="mx-auto mb-3 text-gray-300" />
              <p className="text-gray-500">暂无文件</p>
              <p className="text-sm text-gray-400 mt-1">支持 PDF、Word、Excel、TXT、Markdown 等格式</p>
            </div>
          ) : (
            <div className="divide-y">
              {files.map((file: any) => (
                <div
                  key={file.id}
                  className="flex items-center gap-3 p-4 hover:bg-gray-50 transition-colors"
                >
                  <div className="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center shrink-0">
                    <FileText size={20} className="text-blue-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="font-medium truncate">{file.filename}</div>
                    <div className="flex items-center gap-3 text-sm text-gray-500 mt-0.5">
                      <span>{file.file_size ? formatSize(file.file_size) : '-'}</span>
                      {getStatusBadge(file.parse_status)}
                    </div>
                  </div>
                  <button
                    onClick={() => {
                      if (confirm('确定删除此文件？')) {
                        deleteFile.mutate(file.id)
                      }
                    }}
                    className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors shrink-0"
                  >
                    <Trash2 size={18} />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* 提示信息 */}
        <div className="mt-6 p-4 bg-blue-50 rounded-xl">
          <h3 className="font-medium text-blue-800 mb-2">文件使用说明</h3>
          <ul className="text-sm text-blue-700 space-y-1">
            <li>• 在聊天时选择文件，AI 将结合文件内容回答问题</li>
            <li>• 支持的文件格式：PDF、Word、Excel、纯文本、Markdown</li>
            <li>• 单个文件大小限制：10MB</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
