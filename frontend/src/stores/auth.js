import { defineStore } from 'pinia'
import { api, getToken, setToken } from '@/api/client'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    loading: false,
    ready: false,
    providers: { email: true, google: false },
  }),

  getters: {
    isAuthenticated: (state) => Boolean(state.user),
    isAdmin: (state) => Boolean(state.user?.is_admin),
    displayName: (state) => state.user?.name?.split(' ')[0] || '',
  },

  actions: {
    async init() {
      if (this.ready) return
      api.authProviders()
        .then((data) => { this.providers = data })
        .catch(() => {})

      if (!getToken()) {
        this.ready = true
        return
      }
      try {
        this.user = await api.me()
      } catch {
        setToken('')
        this.user = null
      } finally {
        this.ready = true
      }
    },

    async login(credentials) {
      const data = await api.login(credentials)
      setToken(data.access_token)
      this.user = data.user
      return data.user
    },

    async register(payload) {
      const data = await api.register(payload)
      setToken(data.access_token)
      this.user = data.user
      return data.user
    },

    async applyToken(token) {
      setToken(token)
      this.user = await api.me()
      this.ready = true
      return this.user
    },

    logout() {
      setToken('')
      this.user = null
    },
  },
})
