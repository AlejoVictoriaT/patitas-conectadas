<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/api/client'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import { setPageTitle } from '@/lib/head'

const auth = useAuthStore()
const ui = useUiStore()
const route = useRoute()
const router = useRouter()

const name = ref('')
const email = ref('')
const password = ref('')
const sending = ref(false)
const error = ref('')

onMounted(() => setPageTitle('Crear cuenta'))

async function submit() {
  if (password.value.length < 8) {
    error.value = 'La contraseña debe tener al menos 8 caracteres.'
    return
  }
  sending.value = true
  error.value = ''
  try {
    await auth.register({ name: name.value.trim(), email: email.value.trim(), password: password.value })

    // Si venía desde una publicación de invitado, se vincula automáticamente.
    const token = route.query.vincular
    if (token) {
      try {
        await api.claimPost(token)
        ui.forgetGuestPost(token)
        ui.success('Tu publicación quedó vinculada a la cuenta.')
      } catch {
        ui.toast('Creamos tu cuenta, pero no pudimos vincular la publicación.', 'info')
      }
    }

    router.push(route.query.redirect || '/mis-publicaciones')
  } catch (err) {
    error.value = err.message
  } finally {
    sending.value = false
  }
}

function googleLogin() {
  const next = route.query.redirect || '/mis-publicaciones'
  window.location.href = `/api/auth/google/start?next=${encodeURIComponent(next)}`
}
</script>

<template>
  <div class="container section auth-page">
    <div class="panel">
      <h1>Crear una cuenta</h1>
      <p class="text-soft">
        Con una cuenta administras todas tus publicaciones desde un solo lugar. Es gratis.
      </p>

      <button v-if="auth.providers.google" class="btn btn-ghost btn-block" type="button" @click="googleLogin">
        <span aria-hidden="true">🔵</span> Continuar con Google
      </button>

      <div v-if="auth.providers.google" class="divider"><span>o</span></div>

      <form novalidate @submit.prevent="submit">
        <div class="field">
          <label class="label" for="name">Tu nombre</label>
          <input id="name" v-model="name" class="input" type="text" autocomplete="name" required />
        </div>

        <div class="field">
          <label class="label" for="email">Correo electrónico</label>
          <input id="email" v-model="email" class="input" type="email" autocomplete="email" required />
        </div>

        <div class="field">
          <label class="label" for="password">Contraseña</label>
          <input
            id="password"
            v-model="password"
            class="input"
            type="password"
            autocomplete="new-password"
            minlength="8"
            required
          />
          <p class="hint">Mínimo 8 caracteres.</p>
        </div>

        <p v-if="error" class="alert alert-error" role="alert">{{ error }}</p>

        <button class="btn btn-primary btn-lg btn-block" type="submit" :disabled="sending">
          <span v-if="sending" class="spinner"></span>
          {{ sending ? 'Creando…' : 'Crear cuenta' }}
        </button>
      </form>

      <p class="text-center switch">
        ¿Ya tienes cuenta?
        <router-link :to="{ name: 'ingresar', query: route.query }">Inicia sesión</router-link>
      </p>

      <p class="text-center text-muted small">
        Al crear una cuenta aceptas los
        <router-link to="/legal/terminos">términos</router-link> y la
        <router-link to="/legal/privacidad">política de privacidad</router-link>.
      </p>
    </div>
  </div>
</template>

<style scoped>
.auth-page { max-width: 460px; }
.auth-page h1 { margin-bottom: 4px; }
.auth-page > .panel > p:first-of-type { margin-bottom: 18px; }

.divider {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 16px 0;
  color: var(--text-muted);
  font-size: 0.85rem;
}
.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border);
}

.switch { margin: 16px 0 6px; }
</style>
