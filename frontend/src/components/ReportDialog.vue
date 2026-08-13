<script setup>
import { onMounted, ref } from 'vue'
import AppModal from '@/components/AppModal.vue'
import { api } from '@/api/client'
import { useUiStore } from '@/stores/ui'

const props = defineProps({
  identifier: { type: String, required: true },
})
const emit = defineEmits(['close'])

const ui = useUiStore()
const reasons = ref([])
const reason = ref('')
const details = ref('')
const sending = ref(false)
const error = ref('')

onMounted(async () => {
  try {
    reasons.value = await api.reportReasons()
  } catch {
    reasons.value = [{ value: 'otro', label: 'Otro motivo' }]
  }
})

async function submit() {
  if (!reason.value) {
    error.value = 'Selecciona un motivo.'
    return
  }
  sending.value = true
  error.value = ''
  try {
    const result = await api.reportPost(props.identifier, {
      reason: reason.value,
      details: details.value.trim() || null,
    })
    ui.success(result.message || 'Gracias por avisarnos.')
    emit('close')
  } catch (err) {
    error.value = err.message
  } finally {
    sending.value = false
  }
}
</script>

<template>
  <AppModal title="Reportar publicación" @close="emit('close')">
    <p class="text-soft">
      Cuéntanos qué ocurre con esta publicación. Nuestro equipo la revisará lo antes posible.
    </p>

    <div class="field">
      <span class="label">Motivo</span>
      <div class="option-list">
        <button
          v-for="item in reasons"
          :key="item.value"
          type="button"
          class="option"
          :class="{ 'is-selected': reason === item.value }"
          @click="reason = item.value"
        >
          {{ item.label }}
        </button>
      </div>
    </div>

    <div class="field">
      <label class="label" for="report-details">
        Detalles <span class="optional">(opcional)</span>
      </label>
      <textarea
        id="report-details"
        v-model="details"
        class="textarea"
        maxlength="1000"
        placeholder="Cuéntanos brevemente qué sucede"
      ></textarea>
    </div>

    <p v-if="error" class="alert alert-error">{{ error }}</p>

    <div class="actions">
      <button class="btn btn-ghost" type="button" @click="emit('close')">Cancelar</button>
      <button class="btn btn-primary" type="button" :disabled="sending" @click="submit">
        <span v-if="sending" class="spinner"></span>
        {{ sending ? 'Enviando…' : 'Enviar reporte' }}
      </button>
    </div>
  </AppModal>
</template>

<style scoped>
.actions {
  display: grid;
  gap: 8px;
  margin-top: 4px;
}
@media (min-width: 480px) {
  .actions { grid-template-columns: 1fr 1fr; }
}
</style>
