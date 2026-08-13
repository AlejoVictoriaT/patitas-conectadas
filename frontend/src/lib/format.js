/** Formato de fechas, etiquetas y textos según el tipo de publicación. */

const MESES = [
  'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
  'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre',
]

function toDate(value) {
  if (!value) return null
  // Las fechas sin hora (YYYY-MM-DD) se interpretan en horario local, no UTC.
  const date = /^\d{4}-\d{2}-\d{2}$/.test(value) ? new Date(`${value}T12:00:00`) : new Date(value)
  return Number.isNaN(date.getTime()) ? null : date
}

export function formatDate(value) {
  const date = toDate(value)
  if (!date) return ''
  return `${date.getDate()} de ${MESES[date.getMonth()]} de ${date.getFullYear()}`
}

export function formatShortDate(value) {
  const date = toDate(value)
  if (!date) return ''
  return `${date.getDate()} ${MESES[date.getMonth()].slice(0, 3)} ${date.getFullYear()}`
}

export function timeAgo(value) {
  const date = toDate(value)
  if (!date) return ''
  const seconds = Math.floor((Date.now() - date.getTime()) / 1000)
  if (seconds < 60) return 'hace un momento'
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `hace ${minutes} min`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `hace ${hours} h`
  const days = Math.floor(hours / 24)
  if (days === 1) return 'ayer'
  if (days < 30) return `hace ${days} días`
  const months = Math.floor(days / 30)
  if (months < 12) return `hace ${months} ${months === 1 ? 'mes' : 'meses'}`
  const years = Math.floor(months / 12)
  return `hace ${years} ${years === 1 ? 'año' : 'años'}`
}

export function todayISO() {
  const now = new Date()
  const offset = now.getTimezoneOffset() * 60000
  return new Date(now.getTime() - offset).toISOString().slice(0, 10)
}

export const TYPE_META = {
  perdida: {
    emoji: '🔴',
    label: 'Perdida',
    action: 'Perdí una mascota',
    color: 'perdida',
    dateLabel: '¿Qué día se perdió?',
    descriptionHint: 'Se perdió cerca del parque. Lleva collar azul y responde al nombre de Max.',
    resolvedMessage: '🎉 ¡Esta mascota ya fue reunida con su familia!',
  },
  encontrada: {
    emoji: '🟢',
    label: 'Encontrada',
    action: 'Encontré una mascota',
    color: 'encontrada',
    dateLabel: '¿Qué día la encontraste?',
    descriptionHint: 'Fue encontrada cerca de la iglesia. Es tranquila y parece estar acostumbrada a las personas.',
    resolvedMessage: '🏠 Esta mascota ya fue entregada a su familia.',
  },
  adopcion: {
    emoji: '💙',
    label: 'En adopción',
    action: 'Dar en adopción',
    color: 'adopcion',
    dateLabel: '¿Desde qué fecha está disponible?',
    descriptionHint: 'Es cariñosa, juguetona y busca una familia responsable.',
    resolvedMessage: '❤️ Esta mascota ya fue adoptada.',
  },
}

export const SPECIES_EMOJI = {
  perro: '🐕',
  gato: '🐈',
  otro: '🐾',
}

const STATUS_COLOR = {
  perdida: 'perdida',
  reunida: 'encontrada',
  buscando_familia: 'encontrada',
  entregada: 'encontrada',
  disponible: 'adopcion',
  adoptada: 'adopcion',
  cerrada: 'cerrada',
}

export function statusColor(status) {
  return STATUS_COLOR[status] || 'cerrada'
}

export function typeMeta(type) {
  return TYPE_META[type] || TYPE_META.perdida
}

export function speciesEmoji(species) {
  return SPECIES_EMOJI[species] || '🐾'
}

export function locationLine(post) {
  return [post.city, post.neighborhood].filter(Boolean).join(' · ')
}
