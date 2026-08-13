<script setup>
import { onMounted } from 'vue'
import AppHeader from '@/components/AppHeader.vue'
import AppFooter from '@/components/AppFooter.vue'
import MobileTabBar from '@/components/MobileTabBar.vue'
import ToastHost from '@/components/ToastHost.vue'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import { api } from '@/api/client'

const auth = useAuthStore()
const ui = useUiStore()

onMounted(async () => {
  await auth.init()
  try {
    ui.config = await api.config()
  } catch {
    /* la app funciona con los valores por defecto */
  }
})
</script>

<template>
  <a class="skip-link" href="#contenido">Ir al contenido</a>
  <AppHeader />

  <main id="contenido" class="app-main">
    <!--
      Sin <transition> alrededor de router-view: una vista con más de un nodo raíz
      (por ejemplo un comentario suelto o un v-if/v-else) no se puede animar, y con
      mode="out-in" la salida nunca termina y la pantalla queda en blanco.
    -->
    <router-view />
  </main>

  <AppFooter />
  <MobileTabBar />
  <ToastHost />
</template>

<style>
.skip-link {
  position: absolute;
  left: -9999px;
  top: 0;
  background: var(--brand);
  color: #fff;
  padding: 10px 16px;
  z-index: 100;
  border-radius: 0 0 var(--radius) 0;
}
.skip-link:focus {
  left: 0;
}
</style>
