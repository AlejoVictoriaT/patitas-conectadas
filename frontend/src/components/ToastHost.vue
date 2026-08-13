<script setup>
import { useUiStore } from '@/stores/ui'

const ui = useUiStore()
</script>

<template>
  <div class="toast-host" role="status" aria-live="polite">
    <transition-group name="toast">
      <div v-for="toast in ui.toasts" :key="toast.id" class="toast" :class="`toast-${toast.type}`">
        <span>{{ toast.message }}</span>
        <button type="button" aria-label="Cerrar aviso" @click="ui.dismiss(toast.id)">×</button>
      </div>
    </transition-group>
  </div>
</template>

<style scoped>
.toast-host {
  position: fixed;
  left: 12px;
  right: 12px;
  bottom: calc(var(--tabbar-h) + 12px + env(safe-area-inset-bottom, 0px));
  z-index: 80;
  display: grid;
  gap: 8px;
  pointer-events: none;
}

.toast {
  pointer-events: auto;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border-radius: var(--radius);
  background: var(--text);
  color: #fff;
  box-shadow: var(--shadow-lg);
  font-size: 0.95rem;
}

.toast button {
  margin-left: auto;
  background: none;
  border: none;
  color: inherit;
  font-size: 1.3rem;
  line-height: 1;
  cursor: pointer;
  padding: 0 4px;
}

.toast-success { background: #05603a; }
.toast-error { background: #b42318; }
.toast-info { background: var(--text); }

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
.toast-enter-active,
.toast-leave-active {
  transition: all 0.2s ease;
}

@media (min-width: 768px) {
  .toast-host {
    left: auto;
    right: 24px;
    bottom: 24px;
    width: min(380px, calc(100vw - 48px));
  }
}
</style>
