<script setup>
import { onMounted, ref, watch } from 'vue'
import EmptyState from '@/components/EmptyState.vue'
import CitySelect from '@/components/CitySelect.vue'
import { api } from '@/api/client'
import { formatShortDate } from '@/lib/format'
import { setPageTitle } from '@/lib/head'

const articles = ref([])
const categories = ref([])
const category = ref('')
const city = ref(null)
const loading = ref(true)

const ICONOS = {
  noticia: '📰',
  albergue: '🏚️',
  hogar_de_paso: '🏡',
  fundacion: '🤝',
  jornada_adopcion: '💙',
  esterilizacion: '🏥',
  vacunacion: '💉',
  consejo: '💡',
  bienestar_animal: '🐾',
}

async function load() {
  loading.value = true
  try {
    articles.value = await api.articles({ category: category.value, city: city.value?.city, limit: 40 })
  } catch {
    articles.value = []
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  setPageTitle('Noticias y ayuda')
  try {
    categories.value = await api.articleCategories()
  } catch {
    categories.value = []
  }
  await load()
})

watch([category, city], load)
</script>

<template>
  <div class="container section">
    <h1>📰 Noticias y ayuda</h1>
    <p class="text-soft intro">
      Albergues, hogares de paso, fundaciones, jornadas de adopción, esterilización, vacunación y
      consejos para cuidar y encontrar mascotas.
    </p>

    <div class="filters panel">
      <div class="field">
        <span class="label">📍 Ciudad</span>
        <CitySelect v-model="city" allow-clear placeholder="Todo el país" />
        <p class="hint">Los recursos sin ciudad aplican a todo el país.</p>
      </div>

      <div class="field">
        <span class="label">Categoría</span>
        <div class="chip-group">
          <button type="button" class="chip" :class="{ 'is-selected': !category }" @click="category = ''">
            Todo
          </button>
          <button
            v-for="item in categories"
            :key="item.value"
            type="button"
            class="chip"
            :class="{ 'is-selected': category === item.value }"
            @click="category = item.value"
          >
            {{ ICONOS[item.value] || '📄' }} {{ item.label }}
          </button>
        </div>
      </div>
    </div>

    <p v-if="loading" class="text-soft">Cargando…</p>

    <div v-else-if="articles.length" class="article-grid">
      <article v-for="item in articles" :key="item.id" class="card article-card">
        <img v-if="item.image_url" :src="item.image_url" :alt="item.title" loading="lazy" />
        <div class="card-body">
          <span class="badge badge-neutral">{{ ICONOS[item.category] || '📄' }} {{ item.category.replace(/_/g, ' ') }}</span>
          <h2>
            <router-link :to="`/noticias/${item.slug}`">{{ item.title }}</router-link>
          </h2>
          <p class="text-soft small">{{ item.excerpt || item.content.slice(0, 140) + '…' }}</p>
          <p class="text-muted small">
            {{ formatShortDate(item.published_at) }}
            <template v-if="item.city"> · 📍 {{ item.city }}</template>
          </p>
        </div>
      </article>
    </div>

    <EmptyState
      v-else
      emoji="📰"
      title="Todavía no hay contenido en esta categoría"
      message="Pronto publicaremos recursos e información de ayuda para tu ciudad."
    />
  </div>
</template>

<style scoped>
.intro { max-width: 62ch; margin-top: -6px; }
.filters { margin-bottom: 20px; }
.filters .field:last-child { margin-bottom: 0; }

.article-grid { display: grid; gap: 14px; }

.article-card img { width: 100%; aspect-ratio: 16 / 9; object-fit: cover; }
.article-card .card-body { display: grid; gap: 8px; align-content: start; }
.article-card h2 { font-size: 1.08rem; margin: 0; }
.article-card h2 a { color: var(--text); }
.article-card p { margin: 0; }
.article-card .badge { justify-self: start; text-transform: capitalize; }

@media (min-width: 768px) {
  .article-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (min-width: 1024px) {
  .article-grid { grid-template-columns: repeat(3, 1fr); }
}
</style>
