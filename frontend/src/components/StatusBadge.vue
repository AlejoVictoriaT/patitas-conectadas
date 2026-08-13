<script setup>
import { computed } from 'vue'
import { statusColor, typeMeta } from '@/lib/format'

const props = defineProps({
  post: { type: Object, required: true },
  variant: { type: String, default: 'status' }, // 'status' | 'type'
})

const meta = computed(() => typeMeta(props.post.type))
const color = computed(() =>
  props.variant === 'type' ? meta.value.color : statusColor(props.post.status),
)
const text = computed(() =>
  props.variant === 'type' ? props.post.type_label : props.post.status_label,
)
</script>

<template>
  <span class="badge" :class="`badge-${color}`">
    <span class="dot" aria-hidden="true"></span>
    {{ text }}
  </span>
</template>
