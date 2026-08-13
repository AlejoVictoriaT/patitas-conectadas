<script setup>
import { computed, ref } from 'vue'
import { useUiStore } from '@/stores/ui'

const props = defineProps({
  url: { type: String, required: true },
  title: { type: String, default: 'Mira esta publicación en Patitas Conectadas' },
  compact: { type: Boolean, default: false },
})

const ui = useUiStore()
const canNativeShare = ref(typeof navigator !== 'undefined' && Boolean(navigator.share))

const message = computed(() => `${props.title}\n${props.url}`)
const whatsappUrl = computed(() => `https://wa.me/?text=${encodeURIComponent(message.value)}`)
const facebookUrl = computed(
  () => `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(props.url)}`,
)

async function nativeShare() {
  try {
    await navigator.share({ title: props.title, text: props.title, url: props.url })
  } catch {
    /* el usuario canceló */
  }
}

async function copyLink() {
  try {
    await navigator.clipboard.writeText(props.url)
    ui.success('Enlace copiado. Ya puedes pegarlo donde quieras.')
  } catch {
    window.prompt('Copia este enlace:', props.url)
  }
}
</script>

<template>
  <div class="share" :class="{ compact }">
    <a class="btn btn-whatsapp" :href="whatsappUrl" target="_blank" rel="noopener">
      💬 <span>Compartir por WhatsApp</span>
    </a>
    <a class="btn btn-ghost" :href="facebookUrl" target="_blank" rel="noopener">
      📘 <span>Facebook</span>
    </a>
    <button class="btn btn-ghost" type="button" @click="copyLink">🔗 <span>Copiar enlace</span></button>
    <button v-if="canNativeShare" class="btn btn-ghost" type="button" @click="nativeShare">
      📤 <span>Más opciones</span>
    </button>
  </div>
</template>

<style scoped>
.share { display: grid; gap: 8px; }

@media (min-width: 480px) {
  .share { grid-template-columns: 1fr 1fr; }
  .share > :first-child { grid-column: 1 / -1; }
  .share.compact { grid-template-columns: repeat(2, 1fr); }
}
</style>
