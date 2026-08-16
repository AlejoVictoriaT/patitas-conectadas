<script setup>
/**
 * Noticias del mundo animal: notas de medios externos traídas por RSS.
 *
 * Es contenido ajeno, y la interfaz lo deja claro en todo momento: el nombre
 * del medio siempre visible, el enlace abre fuera del sitio y en ningún caso se
 * reproduce el cuerpo de la nota. Las guías propias viven en otra sección para
 * que nadie confunda quién escribió qué.
 *
 * El servidor ya descarta lo angustiante y mezcla los temas en la primera
 * página, así que aquí no hay lógica editorial: solo filtros y presentación.
 */
import { computed, onMounted, ref, watch } from 'vue'
import EmptyState from '@/components/EmptyState.vue'
import { api } from '@/api/client'
import { timeAgo } from '@/lib/format'
import { setPageDescription, setPageTitle } from '@/lib/head'

const news = ref([])
const topics = ref([])
const topic = ref('')
const loading = ref(true)

const page = ref(1)
const pages = ref(1)
const total = ref(0)
const PAGE_SIZE = 12

// Ancla para el scroll al cambiar de página.
const gridRef = ref(null)

const TOPIC_ICONS = {
  adopcion: '🏡',
  refugios: '🤝',
  salud: '💉',
  comportamiento: '🧠',
  historias: '💚',
}

const hayFiltros = computed(() => Boolean(topic.value))

function topicLabel(valor) {
  return topics.value.find((t) => t.value === valor)?.label || valor
}

async function loadNews(nuevaPagina = page.value) {
  loading.value = true
  try {
    const data = await api.news({
      topic: topic.value,
      page: nuevaPagina,
      page_size: PAGE_SIZE,
    })
    news.value = data.items
    page.value = data.page
    pages.value = data.pages
    total.value = data.total
  } catch {
    news.value = []
    total.value = 0
    pages.value = 1
  } finally {
    loading.value = false
  }
}

async function irAPagina(destino) {
  if (destino < 1 || destino > pages.value) return
  await loadNews(destino)
  // Se sube hasta la primera noticia, no hasta el inicio de la página: quien
  // pasa de página quiere seguir leyendo, no volver a ver el título y los
  // filtros que ya usó. El margen deja el encabezado fijo sin tapar la tarjeta.
  const destinoY = gridRef.value?.getBoundingClientRect().top ?? 0
  window.scrollTo({
    top: window.scrollY + destinoY - 90,
    behavior: 'smooth',
  })
}

function limpiarFiltros() {
  topic.value = ''
}

onMounted(async () => {
  setPageTitle('Noticias del mundo animal')
  setPageDescription(
    'Jornadas de adopción, albergues, vacunación, comportamiento y buenas historias de perros ' +
      'y gatos, reunidas de varios medios.',
  )
  try {
    topics.value = await api.newsTopics()
  } catch {
    topics.value = []
  }
  await loadNews(1)
})

// Cualquier cambio de filtro vuelve a la primera página: conservar la página 7
// al cambiar de tema dejaría la pantalla en blanco.
watch(topic, () => loadNews(1))
</script>

<template>
  <div class="container section">
    <h1>Noticias del mundo animal</h1>
    <p class="text-soft intro">
      Jornadas de adopción, albergues que necesitan manos, vacunación, comportamiento y buenas
      historias de perros y gatos. Traemos el titular y el enlace; la nota completa la lees en el
      medio que la escribió.
    </p>

    <!-- Filtros -->
    <div class="panel filters">
      <div class="field">
        <span class="label">Tema</span>
        <div class="chip-group">
          <button type="button" class="chip" :class="{ 'is-selected': !topic }" @click="topic = ''">
            Todo
          </button>
          <button
            v-for="item in topics"
            :key="item.value"
            type="button"
            class="chip"
            :class="{ 'is-selected': topic === item.value }"
            @click="topic = item.value"
          >
            {{ TOPIC_ICONS[item.value] || '·' }} {{ item.label }}
          </button>
        </div>
      </div>

      <button v-if="hayFiltros" class="btn btn-quiet btn-sm clear" type="button" @click="limpiarFiltros">
        Quitar filtros
      </button>
    </div>

    <p v-if="loading" class="text-soft">Cargando noticias…</p>

    <template v-else-if="news.length">
      <p class="text-soft count">
        {{ total }} {{ total === 1 ? 'noticia' : 'noticias' }} ·
        página {{ page }} de {{ pages }}
      </p>

      <div ref="gridRef" class="news-grid stagger">
        <a
          v-for="(item, index) in news"
          :key="item.id"
          class="card news-card"
          :class="`topic-${item.topic}`"
          :style="{ '--i': index }"
          :href="item.url"
          target="_blank"
          rel="noopener noreferrer"
        >
          <!--
            Sin foto, a propósito. La mayoría de estas notas llegan por búsqueda
            temática en toda la prensa, y esa vía no trae imagen de portada:
            apenas una de cada diez la tiene. Ponerla solo en esas diez hace que
            las otras noventa parezcan rotas. Sin ninguna, la lista queda pareja,
            entra más titular en pantalla y carga más rápido. El dato se sigue
            guardando: si algún día las fuentes traen imagen, es volver a poner
            este bloque.
          -->
          <div class="card-body">
            <div class="news-meta">
              <span class="badge" :class="`badge-topic-${item.topic}`">
                {{ TOPIC_ICONS[item.topic] }} {{ topicLabel(item.topic) }}
              </span>
              <span v-if="item.cities" class="badge badge-neutral">📍 {{ item.cities }}</span>
            </div>

            <h2>{{ item.title }}</h2>
            <p v-if="item.summary" class="text-soft small summary">{{ item.summary }}</p>

            <p class="text-muted small source-line">
              <strong>{{ item.source }}</strong>
              · {{ timeAgo(item.published_at) }}
              <span class="external" aria-hidden="true">↗</span>
            </p>
          </div>
        </a>
      </div>

      <div v-if="pages > 1" class="pager">
        <button class="btn btn-ghost btn-sm" type="button" :disabled="page <= 1" @click="irAPagina(page - 1)">
          ← Anteriores
        </button>
        <span class="text-soft small">{{ page }} / {{ pages }}</span>
        <button class="btn btn-ghost btn-sm" type="button" :disabled="page >= pages" @click="irAPagina(page + 1)">
          Siguientes →
        </button>
      </div>
    </template>

    <EmptyState
      v-else
      emoji="🐾"
      title="No hay noticias para estos filtros"
      message="Puede que todavía no se haya publicado nada reciente sobre este tema. Prueba quitando algún filtro."
    >
      <button v-if="hayFiltros" class="btn btn-primary" type="button" @click="limpiarFiltros">
        Ver todas las noticias
      </button>
    </EmptyState>

    <div class="alert alert-info guides-link">
      <div>
        <strong>¿Buscas algo para hacer hoy?</strong>
        <p class="small">
          Las mascotas que esperan familia están en Adopciones, y las guías para buscar o cuidar a
          una mascota, en Guías.
        </p>
        <div class="row-tight">
          <router-link class="btn btn-ghost btn-sm" to="/adopciones">Adopciones</router-link>
          <router-link class="btn btn-quiet btn-sm" to="/guias">Guías</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/*
  Dos colores propios de esta pantalla. El resto de la paleta sale de los tokens
  globales, pero «comportamiento» e «historias» no tienen equivalente allí: los
  tokens de color describen estados de una publicación (perdida, encontrada,
  adopción), y estos son temas de lectura. Meterlos en el sistema global haría
  creer que significan lo mismo.
*/
.news-grid {
  --tema-comportamiento: #b45309;
  --tema-comportamiento-soft: #fdf0dd;
  --tema-historias: #6d4aa8;
  --tema-historias-soft: #f1ecfa;
}

.intro { max-width: 64ch; margin-top: -6px; }

.filters { margin-bottom: 14px; }
.filters .field:last-of-type { margin-bottom: 0; }

.count { margin: 0 0 12px; }

/* Con 12 tarjetas el paso por defecto haría esperar casi un segundo a la
   última: se acorta para que la rejilla entre de corrido. */
.news-grid { display: grid; gap: 14px; grid-auto-rows: 1fr; --stagger-step: 35ms; }

.news-card {
  display: flex;
  flex-direction: column;
  height: 100%;
  color: var(--text);
  /* Franja de color por tema: se distingue de un vistazo sin leer la etiqueta. */
  border-left: 4px solid var(--cerrada);
  transition:
    transform var(--dur) var(--ease-out),
    box-shadow var(--dur) var(--ease-out);
}
.news-card:hover {
  text-decoration: none;
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.news-card.topic-adopcion { border-left-color: var(--adopcion); }
.news-card.topic-refugios { border-left-color: var(--brand); }
.news-card.topic-salud { border-left-color: var(--encontrada); }
.news-card.topic-comportamiento { border-left-color: var(--tema-comportamiento); }
.news-card.topic-historias { border-left-color: var(--tema-historias); }

.news-card .card-body { display: flex; flex-direction: column; gap: 8px; flex: 1; }
.news-meta { display: flex; flex-wrap: wrap; gap: 6px; }
.news-card h2 { margin: 0; font-size: 1.02rem; line-height: 1.35; }

.summary {
  margin: 0;
  /* Tres líneas como máximo: mantiene la rejilla pareja. */
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.source-line { margin: auto 0 0; padding-top: 4px; }
.external { opacity: 0.6; }

.badge-topic-adopcion { background: var(--adopcion-soft); color: #175cd3; }
.badge-topic-refugios { background: var(--brand-light); color: var(--brand-dark); }
.badge-topic-salud { background: var(--encontrada-soft); color: #027a48; }
.badge-topic-comportamiento {
  background: var(--tema-comportamiento-soft);
  color: var(--tema-comportamiento);
}
.badge-topic-historias {
  background: var(--tema-historias-soft);
  color: var(--tema-historias);
}

.clear { margin-top: 4px; }

.pager {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14px;
  margin-top: 20px;
}

.guides-link { margin-top: 28px; }
.guides-link p { margin: 4px 0 10px; }

@media (min-width: 768px) {
  .news-grid { grid-template-columns: repeat(2, 1fr); }
  /* Antes eran dos columnas porque había dos filtros, tema y departamento. Con
     uno solo, esa rejilla lo encogía a 320px y partía los chips en tres filas. */
}

@media (min-width: 1024px) {
  .news-grid { grid-template-columns: repeat(3, 1fr); }
}
</style>
