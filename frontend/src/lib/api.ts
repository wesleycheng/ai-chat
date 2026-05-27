import axios from 'axios'
import { useAuthStore } from '../stores/authStore'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// 认证 API
export const authApi = {
  login: (username: string, password: string) =>
    api.post('/auth/login', { username, password }),
  
  register: (username: string, email: string, password: string) =>
    api.post('/auth/register', { username, email, password }),
  
  refresh: (refreshToken: string) =>
    api.post('/auth/refresh', { refresh_token: refreshToken }),
  
  getMe: () => api.get('/auth/me'),
}

// 会话 API
export const conversationApi = {
  list: (skip = 0, limit = 20) =>
    api.get('/conversations', { params: { skip, limit } }),
  
  create: (data: { title?: string; model_id?: string; agent_id?: string }) =>
    api.post('/conversations', data),
  
  get: (id: string) => api.get(`/conversations/${id}`),
  
  delete: (id: string) => api.delete(`/conversations/${id}`),
  
  getMessages: (id: string, skip = 0, limit = 50) =>
    api.get(`/conversations/${id}/messages`, { params: { skip, limit } }),
  
  chat: (id: string, content: string, options?: { file_ids?: string[]; model_id?: string }) =>
    api.post(`/conversations/${id}/chat`, { content, ...options }),
}

// 文件 API
export const fileApi = {
  upload: async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/files/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  
  list: (skip = 0, limit = 20) =>
    api.get('/files', { params: { skip, limit } }),
  
  get: (id: string) => api.get(`/files/${id}`),
  
  getStatus: (id: string) => api.get(`/files/${id}/status`),
  
  delete: (id: string) => api.delete(`/files/${id}`),
}

// Agent API
export const agentApi = {
  list: (skip = 0, limit = 20) =>
    api.get('/agents', { params: { skip, limit } }),
  
  create: (data: {
    name: string
    description?: string
    system_prompt: string
    model_id?: string
    tools?: string[]
  }) => api.post('/agents', data),
  
  get: (id: string) => api.get(`/agents/${id}`),
  
  update: (id: string, data: Record<string, unknown>) =>
    api.put(`/agents/${id}`, data),
  
  delete: (id: string) => api.delete(`/agents/${id}`),
}

// 配置 API
export const configApi = {
  listModels: () => api.get('/config/models'),
  
  createModel: (data: {
    name: string
    provider: string
    api_base: string
    api_key: string
    model_name: string
    params?: Record<string, unknown>
  }) => api.post('/config/models', data),
  
  updateModel: (id: string, data: Record<string, unknown>) =>
    api.put(`/config/models/${id}`, data),
  
  deleteModel: (id: string) => api.delete(`/config/models/${id}`),
  
  testModel: (id: string) => api.post(`/config/models/${id}/test`),
}

export default api