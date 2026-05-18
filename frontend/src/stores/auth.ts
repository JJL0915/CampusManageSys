import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { loginApi, getMeApi } from '../api/auth'
import type { Role, UserProfile } from '../api/types'

function readUser(): UserProfile | null {
  const raw = sessionStorage.getItem('current_user')
  if (!raw) return null
  try {
    return JSON.parse(raw) as UserProfile
  } catch {
    return null
  }
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<UserProfile | null>(readUser())
  const token = ref(sessionStorage.getItem('access_token') || '')
  const isAuthed = computed(() => Boolean(token.value && user.value))

  async function login(username: string, password: string) {
    const data = await loginApi({ username, password })
    token.value = data.access_token
    user.value = data.user
    sessionStorage.setItem('access_token', data.access_token)
    sessionStorage.setItem('current_user', JSON.stringify(data.user))
  }

  async function loadMe() {
    if (!token.value) return
    const data = await getMeApi()
    user.value = data
    sessionStorage.setItem('current_user', JSON.stringify(data))
  }

  function logout() {
    token.value = ''
    user.value = null
    sessionStorage.removeItem('access_token')
    sessionStorage.removeItem('current_user')
  }

  function hasRole(roles?: Role[]) {
    if (!roles || roles.length === 0) return true
    return Boolean(user.value && roles.includes(user.value.role))
  }

  return { user, token, isAuthed, login, loadMe, logout, hasRole }
})
