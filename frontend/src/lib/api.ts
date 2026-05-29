import axios from 'axios'
import { useAuthStore } from '../stores/authStore'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    // 如果是 FormData，不设置 Content-Type（让浏览器自动设置 boundary）
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type']
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

export const authApi = {
  login: (data: { username: string; password: string }) => api.post('/auth/login', data),
  register: (data: { username: string; email?: string; password: string }) => api.post('/auth/register', data),
  me: () => api.get('/auth/me'),
}

export const conversationApi = {
  list: () => api.get('/conversations'),
  create: (data: any) => api.post('/conversations', data),
  getMessages: (id: string) => api.get(`/conversations/${id}/messages`),
  delete: (id: string) => api.delete(`/conversations/${id}`),
  chat: (id: string, data: any) => api.post(`/conversations/${id}/chat`, data),
}

export const fileApi = {
  upload: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/files/upload', formData)
  },
  list: () => api.get('/files'),
  get: (id: string) => api.get(`/files/${id}`),
  getStatus: (id: string) => api.get(`/files/${id}/status`),
  delete: (id: string) => api.delete(`/files/${id}`),
}

export const agentApi = {
  list: () => api.get('/agents'),
  create: (data: any) => api.post('/agents', data),
  update: (id: string, data: any) => api.put(`/agents/${id}`, data),
  delete: (id: string) => api.delete(`/agents/${id}`),
}

export const configApi = {
  listModels: () => api.get('/config/models'),
  createModel: (data: any) => api.post('/config/models', data),
  updateModel: (id: string, data: any) => api.put(`/config/models/${id}`, data),
  deleteModel: (id: string) => api.delete(`/config/models/${id}`),
  listProviders: () => api.get('/config/providers'),
}
