<script setup>
import EmptyState from '@/components/EmptyState.vue'
</script>

<template>
  <div class="container section">
    <EmptyState
      emoji="🐾"
      title="No encontramos esta página"
      message="Puede que el enlace esté incompleto o que la publicación ya no exista."
    >
      <div class="row">
        <router-link class="btn btn-primary" to="/">Ir al inicio</router-link>
        <router-link class="btn btn-ghost" to="/buscar">Buscar mascotas</router-link>
      </div>
    </EmptyState>
  </div>
</template>
