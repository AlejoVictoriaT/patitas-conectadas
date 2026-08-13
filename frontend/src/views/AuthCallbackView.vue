<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'

const auth = useAuthStore()
const ui = useUiStore()
const router = useRouter()
const error = ref('')

onMounted(async () => {
  const params = new URLSearchParams(window.location.hash.replace(/^#/, ''))
  const token = params.get('token')
  const next = params.get('next') || '/mis-publicaciones'

  if (!token) {
    error.value = 'No recibimos la información de acceso.'
    return
  }

  try {
    await auth.applyToken(token)
    ui.success(`¡Hola, ${auth.displayName}!`)
    // Limpia el token del fragmento de la URL antes de continuar.
    window.history.replaceState(null, '', window.location.pathname)
    router.replace(next)
  } catch {
    error.value = 'No pudimos completar el acceso. Inténtalo de nuevo.'
  }
})
</script>

<template>
  <div class="container section text-center callback">
    <template v-if="error">
      <h1>Algo salió mal</h1>
      <p class="text-soft">{{ error }}</p>
      <router-link class="btn btn-primary" to="/ingresar">Volver a intentar</router-link>
    </template>
    <template v-else>
      <span class="spinner spinner-dark big"></span>
      <p class="text-soft">Iniciando sesión…</p>
    </template>
  </div>
</template>

<style scoped>
.callback {
  display: grid;
  justify-items: center;
  gap: 12px;
  padding-top: 60px;
}
.big { width: 34px; height: 34px; }
</style>
