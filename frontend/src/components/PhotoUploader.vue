<script setup>
import { computed, ref } from 'vue'
import { api } from '@/api/client'
import { compressImage } from '@/lib/image'
import { useUiStore } from '@/stores/ui'

const props = defineProps({
  /** Array de { url, is_primary } */
  modelValue: { type: Array, default: () => [] },
  max: { type: Number, default: 5 },
})

const emit = defineEmits(['update:modelValue'])
const ui = useUiStore()

const uploading = ref(0)
const cameraInput = ref(null)
const galleryInput = ref(null)

const photos = computed(() => props.modelValue || [])
const remaining = computed(() => Math.max(0, props.max - photos.value.length))
const isFull = computed(() => remaining.value === 0)

function update(list) {
  if (list.length && !list.some((p) => p.is_primary)) list[0].is_primary = true
  emit('update:modelValue', list)
}

async function handleFiles(event) {
  const input = event.target
  const files = Array.from(input.files || [])
  input.value = ''
  if (!files.length) return

  const allowed = files.slice(0, remaining.value)
  if (files.length > allowed.length) {
    ui.toast(`Puedes subir máximo ${props.max} fotos.`, 'info')
  }

  for (const file of allowed) {
    uploading.value += 1
    try {
      const optimized = await compressImage(file)
      const { url } = await api.upload(optimized)
      update([...photos.value, { url, is_primary: photos.value.length === 0 }])
    } catch (error) {
      ui.error(error.message || 'No pudimos subir la foto. Inténtalo otra vez.')
    } finally {
      uploading.value -= 1
    }
  }
}

function setPrimary(index) {
  update(photos.value.map((photo, i) => ({ ...photo, is_primary: i === index })))
}

function remove(index) {
  const list = photos.value.filter((_, i) => i !== index).map((p) => ({ ...p }))
  update(list)
}

function move(index, delta) {
  const target = index + delta
  if (target < 0 || target >= photos.value.length) return
  const list = photos.value.map((p) => ({ ...p }))
  const [item] = list.splice(index, 1)
  list.splice(target, 0, item)
  update(list)
}
</script>

<template>
  <div class="uploader">
    <div v-if="photos.length" class="thumbs">
      <figure v-for="(photo, index) in photos" :key="photo.url" class="thumb" :class="{ 'is-primary': photo.is_primary }">
        <img :src="photo.url" :alt="`Foto ${index + 1} de la mascota`" />

        <span v-if="photo.is_primary" class="primary-flag">⭐ Principal</span>

        <figcaption class="thumb-actions">
          <button
            v-if="!photo.is_primary"
            type="button"
            class="icon-btn"
            title="Establecer como foto principal"
            @click="setPrimary(index)"
          >
            ⭐
          </button>
          <button
            type="button"
            class="icon-btn"
            title="Mover antes"
            :disabled="index === 0"
            @click="move(index, -1)"
          >
            ←
          </button>
          <button
            type="button"
            class="icon-btn"
            title="Mover después"
            :disabled="index === photos.length - 1"
            @click="move(index, 1)"
          >
            →
          </button>
          <button type="button" class="icon-btn danger" title="Eliminar foto" @click="remove(index)">🗑️</button>
        </figcaption>
      </figure>

      <div v-for="n in uploading" :key="`load-${n}`" class="thumb skeleton loading-thumb">
        <span class="spinner spinner-dark"></span>
      </div>
    </div>

    <div v-else-if="uploading" class="thumbs">
      <div v-for="n in uploading" :key="`first-${n}`" class="thumb skeleton loading-thumb">
        <span class="spinner spinner-dark"></span>
      </div>
    </div>

    <div v-if="!isFull" class="upload-actions">
      <button type="button" class="btn btn-primary btn-block" @click="cameraInput.click()">
        📷 Tomar una foto
      </button>
      <button type="button" class="btn btn-ghost btn-block" @click="galleryInput.click()">
        🖼️ Elegir de la galería
      </button>
    </div>

    <p class="hint">
      <template v-if="photos.length">
        {{ photos.length }} de {{ max }} fotos. La foto marcada con ⭐ es la que verán primero.
      </template>
      <template v-else>
        Agrega al menos una foto. La primera será la principal y puedes cambiarla después.
      </template>
    </p>

    <input
      ref="cameraInput"
      class="sr-only"
      type="file"
      accept="image/*"
      capture="environment"
      @change="handleFiles"
    />
    <input
      ref="galleryInput"
      class="sr-only"
      type="file"
      accept="image/jpeg,image/png,image/webp,image/heic"
      multiple
      @change="handleFiles"
    />
  </div>
</template>

<style scoped>
.uploader { display: grid; gap: 12px; }

.thumbs {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.thumb {
  position: relative;
  margin: 0;
  aspect-ratio: 1;
  border-radius: var(--radius);
  overflow: hidden;
  background: var(--surface-2);
  border: 2px solid var(--border);
}

.thumb.is-primary { border-color: var(--brand); }

.thumb img { width: 100%; height: 100%; object-fit: cover; }

.loading-thumb { display: grid; place-items: center; }

.primary-flag {
  position: absolute;
  top: 6px;
  left: 6px;
  background: var(--brand);
  color: #fff;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: var(--radius-pill);
}

.thumb-actions {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  justify-content: center;
  gap: 4px;
  padding: 6px 4px;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.65));
}

.icon-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.92);
  cursor: pointer;
  font-size: 0.95rem;
  display: grid;
  place-items: center;
}
.icon-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.icon-btn.danger { background: rgba(255, 226, 226, 0.95); }

.upload-actions { display: grid; gap: 8px; }

@media (min-width: 480px) {
  .thumbs { grid-template-columns: repeat(3, 1fr); }
  .upload-actions { grid-template-columns: 1fr 1fr; }
}
</style>
