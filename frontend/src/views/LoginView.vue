<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { setPageTitle } from '@/lib/head'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const email = ref('')
const password = ref('')
const sending = ref(false)
const error = ref('')

const ERRORES_GOOGLE = {
  google_cancelado: 'Cancelaste el acceso con Google.',
  google_token: 'No pudimos completar el acceso con Google. Inténtalo de nuevo.',
  google_perfil: 'No pudimos leer tu perfil de Google.',
  google_conexion: 'No pudimos conectarnos con Google. Revisa tu conexión.',
  google_sin_correo: 'Tu cuenta de Google no tiene un correo verificado.',
  estado_invalido: 'La sesión de acceso expiró. Inténtalo otra vez.',
  cuenta_desactivada: 'Esta cuenta está desactivada.',
}

onMounted(() => {
  setPageTitle('Iniciar sesión')
  if (route.query.error) error.value = ERRORES_GOOGLE[route.query.error] || 'No pudimos iniciar sesión.'
})

async function submit() {
  sending.value = true
  error.value = ''
  try {
    await auth.login({ email: email.value.trim(), password: password.value })
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
      <h1>Iniciar sesión</h1>
      <p class="text-soft">Entra para administrar tus publicaciones.</p>

      <button v-if="auth.providers.google" class="btn btn-ghost btn-block google" type="button" @click="googleLogin">
        <span aria-hidden="true">🔵</span> Continuar con Google
      </button>

      <div v-if="auth.providers.google" class="divider"><span>o</span></div>

      <form novalidate @submit.prevent="submit">
        <div class="field">
          <label class="label" for="email">Correo electrónico</label>
          <input
            id="email"
            v-model="email"
            class="input"
            type="email"
            autocomplete="email"
            required
          />
        </div>

        <div class="field">
          <label class="label" for="password">Contraseña</label>
          <input
            id="password"
            v-model="password"
            class="input"
            type="password"
            autocomplete="current-password"
            required
          />
        </div>

        <p v-if="error" class="alert alert-error" role="alert">{{ error }}</p>

        <button class="btn btn-primary btn-lg btn-block" type="submit" :disabled="sending">
          <span v-if="sending" class="spinner"></span>
          {{ sending ? 'Entrando…' : 'Entrar' }}
        </button>
      </form>

      <p class="text-center switch">
        ¿No tienes cuenta?
        <router-link :to="{ name: 'crear-cuenta', query: route.query }">Créala gratis</router-link>
      </p>

      <p class="text-center text-muted small">
        También puedes publicar sin cuenta.
        <router-link to="/publicar">Publicar como invitado</router-link>.
      </p>
    </div>
  </div>
</template>

<style scoped>
.auth-page { max-width: 460px; }
.auth-page h1 { margin-bottom: 4px; }
.auth-page > .panel > p:first-of-type { margin-bottom: 18px; }

.google { margin-bottom: 4px; }

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
