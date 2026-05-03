import { defineStore } from 'pinia'
import { authAPI } from '@/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    hasProfile: false,
    loading: false,
    checked: false,
  }),

  getters: {
    isAuthenticated: (state) => !!state.user,
  },

  actions: {
    async checkAuth() {
      try {
        const res = await authAPI.check()
        this.user = res.data.authenticated ? res.data.user : null
        this.hasProfile = res.data.has_profile || false
      } catch {
        this.user = null
        this.hasProfile = false
      } finally {
        this.checked = true
      }
    },

    async login(email, password) {
      const res = await authAPI.login({ email, password })
      this.user = res.data.user
      this.hasProfile = res.data.has_profile || false
      return res.data
    },

    async register(email, username, password) {
      const res = await authAPI.register({ email, username, password })
      this.user = res.data.user
      this.hasProfile = false
      return res.data
    },

    async logout() {
      await authAPI.logout()
      this.user = null
      this.hasProfile = false
    },

    setHasProfile(val) {
      this.hasProfile = val
    }
  }
})
