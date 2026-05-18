import axios from 'axios'
import { ElMessage } from 'element-plus'
import type { ApiResponse } from './types'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 15000
})

request.interceptors.request.use((config) => {
  const token = sessionStorage.getItem('access_token')
  if (token) {
    config.headers = config.headers || {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

;(request.interceptors.response.use as any)(
  (response: any) => {
    const body = response.data as ApiResponse<unknown>
    if (body.code !== 200) {
      ElMessage.error(body.message || '请求失败')
      return Promise.reject(new Error(body.message))
    }
    return body.data
  },
  (error: any) => {
    const message = error.response?.data?.message || error.message || '网络请求失败'
    if (error.response?.status === 401 || error.response?.data?.code === 401) {
      sessionStorage.removeItem('access_token')
      sessionStorage.removeItem('current_user')
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    ElMessage.error(message)
    return Promise.reject(new Error(message))
  }
)

export default request
