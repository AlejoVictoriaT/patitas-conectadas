<script setup>
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
</script>

<template>
  <nav class="tabbar hide-desktop" aria-label="Navegación">
    <router-link to="/" class="tab" exact-active-class="is-active">
      <span aria-hidden="true">🏠</span>
      <small>Inicio</small>
    </router-link>
    <router-link to="/buscar" class="tab" active-class="is-active">
      <span aria-hidden="true">🔎</span>
      <small>Buscar</small>
    </router-link>

    <router-link to="/publicar" class="tab tab-cta" aria-label="Publicar una mascota">
      <span class="cta-circle" aria-hidden="true">🐾</span>
      <small>Publicar</small>
    </router-link>

    <router-link to="/adopciones" class="tab" active-class="is-active">
      <span aria-hidden="true">💙</span>
      <small>Adoptar</small>
    </router-link>
    <router-link
      :to="auth.isAuthenticated ? '/mis-publicaciones' : '/ingresar'"
      class="tab"
      active-class="is-active"
    >
      <span aria-hidden="true">{{ auth.isAuthenticated ? '📋' : '👤' }}</span>
      <small>{{ auth.isAuthenticated ? 'Mis avisos' : 'Entrar' }}</small>
    </router-link>
  </nav>
</template>

<style scoped>
.tabbar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 45;
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  align-items: end;
  background: var(--surface);
  border-top: 1px solid var(--border);
  padding: 6px 4px calc(6px + env(safe-area-inset-bottom, 0px));
  box-shadow: 0 -2px 12px rgba(31, 41, 51, 0.06);
}

.tab {
  display: grid;
  justify-items: center;
  gap: 2px;
  padding: 6px 2px;
  min-height: 52px;
  color: var(--text-muted);
  font-size: 1.15rem;
  text-decoration: none;
  border-radius: var(--radius-sm);
}
.tab:hover { text-decoration: none; }

.tab small {
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.01em;
}

.tab.is-active { color: var(--brand); }

.tab-cta { color: var(--brand); }

.cta-circle {
  display: grid;
  place-items: center;
  width: 48px;
  height: 48px;
  margin-top: -20px;
  border-radius: 50%;
  background: var(--brand);
  color: #fff;
  font-size: 1.3rem;
  box-shadow: 0 6px 16px rgba(15, 118, 110, 0.35);
  border: 3px solid var(--bg);
}
</style>
