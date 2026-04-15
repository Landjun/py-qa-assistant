import { defineStore } from 'pinia'

interface AuthState {
  token: string
  username: string
}

const TOKEN_KEY = 'teaching_ops_token'
const USERNAME_KEY = 'teaching_ops_username'

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    token: localStorage.getItem(TOKEN_KEY) || '',
    username: localStorage.getItem(USERNAME_KEY) || ''
  }),
  getters: {
    isLogin: (state) => Boolean(state.token)
  },
  actions: {
    login(username: string, password: string) {
      // mock login
      if (!username || !password) return false
      this.token = `mock-token-${Date.now()}`
      this.username = username
      localStorage.setItem(TOKEN_KEY, this.token)
      localStorage.setItem(USERNAME_KEY, username)
      return true
    },
    logout() {
      this.token = ''
      this.username = ''
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(USERNAME_KEY)
    }
  }
})
