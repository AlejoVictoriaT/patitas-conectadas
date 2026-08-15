<script setup>
import { onBeforeUnmount, onMounted } from 'vue'

defineProps({
  title: { type: String, default: '' },
})
const emit = defineEmits(['close'])

function onKey(event) {
  if (event.key === 'Escape') emit('close')
}

onMounted(() => {
  document.addEventListener('keydown', onKey)
  document.body.style.overflow = 'hidden'
})

onBeforeUnmount(() => {
  document.removeEventListener('keydown', onKey)
  document.body.style.overflow = ''
})
</script>

<template>
  <!--
    Se teletransporta al <body> a propósito.

    El modal es `position: fixed`, pero eso solo lo ancla al viewport si ningún
    ancestro crea un bloque contenedor. Cualquier antepasado con `transform`,
    `filter` o `will-change` — una animación de entrada, una tarjeta con efecto
    al pasar el cursor — hace que el «fijo» pase a medirse contra ese elemento,
    y el modal termina recortado o fuera de la pantalla. Como este componente se
    usa dentro de formularios y listas, no hay forma de garantizar el contexto
    desde aquí: sacarlo al body lo hace inmune.
  -->
  <Teleport to="body">
    <div class="modal-backdrop" @click.self="emit('close')">
      <div class="modal" role="dialog" aria-modal="true" :aria-label="title">
        <div class="modal-head">
          <h3>{{ title }}</h3>
          <button class="btn-quiet close" type="button" aria-label="Cerrar" @click="emit('close')">×</button>
        </div>
        <slot />
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.close {
  border: none;
  background: none;
  font-size: 1.8rem;
  line-height: 1;
  cursor: pointer;
  color: var(--text-soft);
  padding: 0 6px;
}
</style>
