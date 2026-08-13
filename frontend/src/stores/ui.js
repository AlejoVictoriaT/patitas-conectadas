import { defineStore } from 'pinia'

const CITY_KEY = 'patitas.city'
const GUEST_KEY = 'patitas.publicaciones'

function readJSON(key, fallback) {
  try {
    const raw = localStorage.getItem(key)
    return raw ? JSON.parse(raw) : fallback
  } catch {
    return fallback
  }
}

function writeJSON(key, value) {
  try {
    localStorage.setItem(key, JSON.stringify(value))
  } catch {
    /* almacenamiento no disponible */
  }
}

export const useUiStore = defineStore('ui', {
  state: () => ({
    toasts: [],
    /** Ciudad elegida en la portada: { city, region, country } */
    city: readJSON(CITY_KEY, null),
    /** Publicaciones creadas como invitado en este dispositivo */
    guestPosts: readJSON(GUEST_KEY, []),
    config: null,
  }),

  actions: {
    toast(message, type = 'info', timeout = 4000) {
      const id = Date.now() + Math.random()
      this.toasts.push({ id, message, type })
      setTimeout(() => this.dismiss(id), timeout)
    },

    success(message) { this.toast(message, 'success') },
    error(message) { this.toast(message, 'error', 6000) },

    dismiss(id) {
      this.toasts = this.toasts.filter((t) => t.id !== id)
    },

    setCity(city) {
      this.city = city
      writeJSON(CITY_KEY, city)
    },

    rememberGuestPost(entry) {
      const list = [entry, ...this.guestPosts.filter((p) => p.token !== entry.token)].slice(0, 20)
      this.guestPosts = list
      writeJSON(GUEST_KEY, list)
    },

    forgetGuestPost(token) {
      this.guestPosts = this.guestPosts.filter((p) => p.token !== token)
      writeJSON(GUEST_KEY, this.guestPosts)
    },
  },
})
