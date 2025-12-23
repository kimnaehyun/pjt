import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '@/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || null)
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const isAuthenticated = computed(() => !!token.value)

  async function login(credentials) {
    const response = await authAPI.login(credentials)
    token.value = response.data.token
    user.value = response.data.user
    localStorage.setItem('token', response.data.token)
    localStorage.setItem('user', JSON.stringify(response.data.user))
    return response.data
  }

  async function signup(userData) {
    const response = await authAPI.signup(userData)
    token.value = response.data.token
    user.value = response.data.user
    localStorage.setItem('token', response.data.token)
    localStorage.setItem('user', JSON.stringify(response.data.user))
    return response.data
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  async function fetchUser() {
    const response = await authAPI.getMe()
    user.value = response.data
    localStorage.setItem('user', JSON.stringify(response.data))
    return response.data
  }

  async function updateUser(userData) {
    const response = await authAPI.updateMe(userData)
    user.value = response.data
    localStorage.setItem('user', JSON.stringify(response.data))
    return response.data
  }

  return {
    token,
    user,
    isAuthenticated,
    login,
    signup,
    logout,
    fetchUser,
    updateUser
  }
})
