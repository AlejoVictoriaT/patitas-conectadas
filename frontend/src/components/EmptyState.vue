<script setup>
defineProps({
  emoji: { type: String, default: '🐾' },
  title: { type: String, required: true },
  message: { type: String, default: '' },
})
</script>

<template>
  <div class="empty panel text-center">
    <div class="empty-emoji" aria-hidden="true">{{ emoji }}</div>
    <h3>{{ title }}</h3>
    <p v-if="message" class="text-soft">{{ message }}</p>
    <slot />
  </div>
</template>

<style scoped>
.empty {
  display: grid;
  justify-items: center;
  gap: 6px;
  padding: 32px 20px;
}
.empty-emoji { font-size: 2.6rem; }
.empty h3 { margin: 0; }
.empty p { margin: 0; max-width: 46ch; }
</style>
