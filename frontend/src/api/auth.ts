import request from './http'
import type { TokenResponse, UserProfile } from './types'

export function loginApi(payload: { username: string; password: string }) {
  return request.post<unknown, TokenResponse>('/auth/login', payload)
}

export function getMeApi() {
  return request.get<unknown, UserProfile>('/auth/me')
}

