<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import CitySelect from '@/components/CitySelect.vue'
import PetCard from '@/components/PetCard.vue'
import EmptyState from '@/components/EmptyState.vue'
import { api } from '@/api/client'
import { useUiStore } from '@/stores/ui'

const ui = useUiStore()
const posts = ref([])
const loading = ref(true)
const stats = ref({ ciudades: 0 })

const page = ref(1)
const pages = ref(1)
const total = ref(0)
const PAGE_SIZE = 12

// Ancla para volver al inicio de la rejilla al cambiar de página.
const gridRef = ref(null)

const city = computed({
  get: () => ui.city,
  set: (value) => ui.setCity(value),
})

async function loadRecent(nuevaPagina = 1) {
  loading.value = true
  try {
    const data = await api.listPosts({
      page: nuevaPagina,
      page_size: PAGE_SIZE,
      city: ui.city?.city,
    })
    posts.value = data.items
    page.value = data.page
    pages.value = data.pages
    total.value = data.total
  } catch {
    posts.value = []
    total.value = 0
    pages.value = 1
  } finally {
    loading.value = false
  }
}

async function irAPagina(destino) {
  if (destino < 1 || destino > pages.value || destino === page.value) return
  await loadRecent(destino)
  // Se sube hasta la primera tarjeta, no al inicio de la portada: quien pasa de
  // página quiere seguir viendo mascotas, no releer el encabezado.
  const y = gridRef.value?.getBoundingClientRect().top ?? 0
  window.scrollTo({ top: window.scrollY + y - 90, behavior: 'smooth' })
}

/** Números de página a mostrar: siempre primera y última, y una ventana
 *  alrededor de la actual. Con muchas páginas, los saltos se marcan con «…». */
const paginasVisibles = computed(() => {
  const ultima = pages.value
  if (ultima <= 7) return Array.from({ length: ultima }, (_, i) => i + 1)

  const actual = page.value
  const cerca = new Set([1, ultima, actual, actual - 1, actual + 1])
  if (actual <= 3) [2, 3, 4].forEach((n) => cerca.add(n))
  if (actual >= ultima - 2) [ultima - 3, ultima - 2, ultima - 1].forEach((n) => cerca.add(n))

  const numeros = [...cerca].filter((n) => n >= 1 && n <= ultima).sort((a, b) => a - b)

  const salida = []
  let previo = 0
  for (const n of numeros) {
    if (previo && n - previo > 1) salida.push('…')
    salida.push(n)
    previo = n
  }
  return salida
})

onMounted(async () => {
  await loadRecent(1)
  try {
    stats.value.ciudades = (await api.postsCities()).length
  } catch {
    /* opcional */
  }
})

// Al cambiar de ciudad se vuelve a la primera página: quedarse en la 5 mostraría
// un hueco vacío si esa ciudad tiene menos publicaciones.
watch(() => ui.city?.city, () => loadRecent(1))
</script>

<template>
  <div>
    <!-- Portada -->
    <section class="hero">
      <div class="container hero-inner">
        <p class="eyebrow">🐾 Patitas Conectadas</p>
        <h1>Reencuentros, rescates y nuevos comienzos</h1>
        <p class="lead">
          Publica una mascota perdida, encontrada o en adopción en menos de dos minutos.
          Sin formularios largos y sin necesidad de crear una cuenta.
        </p>

        <div class="actions stagger">
          <router-link
            class="action action-perdida"
            :style="{ '--i': 0 }"
            :to="{ path: '/publicar', query: { tipo: 'perdida' } }"
          >
            <span class="action-emoji" aria-hidden="true">🔴</span>
            <span>
              <strong>Perdí una mascota</strong>
              <small>Publica para que la comunidad la busque contigo</small>
            </span>
          </router-link>

          <router-link
            class="action action-encontrada"
            :style="{ '--i': 1 }"
            :to="{ path: '/publicar', query: { tipo: 'encontrada' } }"
          >
            <span class="action-emoji" aria-hidden="true">🟢</span>
            <span>
              <strong>Encontré una mascota</strong>
              <small>Ayúdala a reencontrarse con su familia</small>
            </span>
          </router-link>

          <router-link class="action action-adopcion" :style="{ '--i': 2 }" to="/adopciones">
            <span class="action-emoji" aria-hidden="true">💙</span>
            <span>
              <strong>Quiero adoptar</strong>
              <small>Conoce mascotas que buscan un hogar</small>
            </span>
          </router-link>

          <router-link class="action action-buscar" :style="{ '--i': 3 }" to="/buscar">
            <span class="action-emoji" aria-hidden="true">🔎</span>
            <span>
              <strong>Buscar mascotas</strong>
              <small>Filtra por ciudad, especie y fecha</small>
            </span>
          </router-link>
        </div>

        <router-link class="btn btn-primary btn-lg btn-block publish-main" to="/publicar">
          🐾 Publicar una mascota
        </router-link>
      </div>
    </section>

    <!-- Ciudad + recientes -->
    <section class="section">
      <div class="container">
        <div v-reveal class="city-bar panel">
          <div>
            <h2 class="city-title">📍 Selecciona tu ciudad</h2>
            <p class="text-muted">
              Verás primero las mascotas publicadas cerca de ti.
              <template v-if="stats.ciudades">Ya hay publicaciones en {{ stats.ciudades }} ciudades.</template>
            </p>
          </div>
          <CitySelect v-model="city" allow-clear placeholder="Todas las ciudades" />
        </div>

        <div class="section-head">
          <h2>🐾 Mascotas recientes</h2>
          <router-link class="btn btn-quiet btn-sm" to="/buscar">Buscar con filtros →</router-link>
        </div>

        <div v-if="loading" class="pet-grid">
          <div v-for="n in 8" :key="n" class="skeleton card-skeleton"></div>
        </div>

        <template v-else-if="posts.length">
          <p class="text-soft count">
            {{ total }} {{ total === 1 ? 'publicación' : 'publicaciones' }}
            <template v-if="pages > 1"> · página {{ page }} de {{ pages }}</template>
          </p>

          <div ref="gridRef" class="pet-grid stagger">
            <PetCard
              v-for="(post, index) in posts"
              :key="post.id"
              :post="post"
              :style="{ '--i': index }"
            />
          </div>

          <nav v-if="pages > 1" class="pager" aria-label="Páginas de publicaciones">
            <button
              class="btn btn-ghost btn-sm"
              type="button"
              :disabled="page <= 1"
              @click="irAPagina(page - 1)"
            >
              ← Anterior
            </button>

            <div class="pages">
              <template v-for="(n, i) in paginasVisibles" :key="`${n}-${i}`">
                <span v-if="n === '…'" class="gap" aria-hidden="true">…</span>
                <button
                  v-else
                  type="button"
                  class="page-btn"
                  :class="{ 'is-current': n === page }"
                  :aria-current="n === page ? 'page' : undefined"
                  :aria-label="`Ir a la página ${n}`"
                  @click="irAPagina(n)"
                >
                  {{ n }}
                </button>
              </template>
            </div>

            <button
              class="btn btn-ghost btn-sm"
              type="button"
              :disabled="page >= pages"
              @click="irAPagina(page + 1)"
            >
              Siguiente →
            </button>
          </nav>
        </template>

        <EmptyState
          v-else
          title="Todavía no hay publicaciones aquí"
          :message="
            ui.city
              ? `Aún no hay mascotas publicadas en ${ui.city.city}. Puedes ser la primera persona en publicar.`
              : 'Sé la primera persona en publicar y ayuda a que esta comunidad crezca.'
          "
        >
          <router-link class="btn btn-primary" to="/publicar">Publicar una mascota</router-link>
        </EmptyState>
      </div>
    </section>

    <!-- Ayuda -->
    <section class="section help">
      <div class="container">
        <div class="help-grid">
          <article v-reveal="{ delay: 0 }" class="panel">
            <h3>¿Perdiste a tu mascota?</h3>
            <p class="text-soft">
              Las primeras horas son decisivas. Publica con una foto clara, comparte el enlace por
              WhatsApp y avisa en tu barrio.
            </p>
            <router-link class="btn btn-ghost btn-sm" to="/guias">Ver la guía</router-link>
          </article>

          <article v-reveal="{ delay: 90 }" class="panel">
            <h3>¿Encontraste una mascota?</h3>
            <p class="text-soft">
              Revisa si tiene placa o microchip, tómale una foto y publícala indicando el sector
              donde la viste.
            </p>
            <router-link class="btn btn-ghost btn-sm" :to="{ path: '/publicar', query: { tipo: 'encontrada' } }">
              Publicar ahora
            </router-link>
          </article>

          <article v-reveal="{ delay: 180 }" class="panel">
            <h3>Emergencia y actualidad</h3>
            <p class="text-soft">
              Teléfonos de emergencia y enlaces oficiales de gobernaciones y alcaldías, junto con lo
              que están publicando los medios sobre el terremoto.
            </p>
            <div class="row-tight">
              <router-link class="btn btn-ghost btn-sm" to="/emergencia">Teléfonos</router-link>
              <router-link class="btn btn-quiet btn-sm" to="/noticias">Noticias</router-link>
            </div>
          </article>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.hero {
  position: relative;
  background:
    radial-gradient(1200px 320px at 15% -10%, var(--brand-light), transparent 70%),
    radial-gradient(900px 260px at 92% 0%, var(--accent-soft), transparent 72%),
    linear-gradient(180deg, var(--accent-soft) 0%, var(--bg) 65%);
  padding: 24px 0 8px;
  overflow: hidden;
}

.hero-inner { display: grid; gap: 14px; }

/* Entrada en cascada de la portada: cada pieza entra un poco después que la
   anterior. Es lo primero que ve el usuario, así que marca el tono. */
@keyframes hero-in {
  from {
    opacity: 0;
    transform: translateY(16px);
  }
  to {
    opacity: 1;
    transform: none;
  }
}

.eyebrow,
.hero h1,
.lead,
.publish-main {
  animation: hero-in 0.7s var(--ease-out) both;
}

.eyebrow { animation-delay: 0.02s; }
.hero h1 { animation-delay: 0.1s; }
.lead { animation-delay: 0.18s; }
.publish-main { animation-delay: 0.5s; }

/* Las cuatro tarjetas de acción entran en cascada (clase `stagger`), empezando
   después del texto de la portada. */
.actions { --stagger-step: 70ms; }
.actions > * { animation-delay: calc(0.26s + var(--stagger-step) * var(--i, 0)); }

.eyebrow {
  margin: 0;
  font-weight: 700;
  color: var(--brand);
  letter-spacing: 0.02em;
}

.hero h1 { margin: 0; }

.lead {
  margin: 0;
  color: var(--text-soft);
  font-size: 1.02rem;
  max-width: 56ch;
}

.actions {
  display: grid;
  gap: 10px;
  margin-top: 6px;
}

.action {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  min-height: 72px;
  border-radius: var(--radius-lg);
  background: var(--surface);
  border: 1px solid var(--border);
  color: var(--text);
  box-shadow: var(--shadow-sm);
  transition: transform 0.12s ease, box-shadow 0.12s ease;
}
.action:hover {
  text-decoration: none;
  transform: translateY(-2px);
  box-shadow: var(--shadow);
}

.action span { display: grid; gap: 2px; }
.action strong { font-size: 1.02rem; }
.action small { color: var(--text-soft); font-size: 0.85rem; }
.action-emoji { font-size: 1.6rem; display: block; flex: none; }

.action-perdida { border-left: 5px solid var(--perdida); }
.action-encontrada { border-left: 5px solid var(--encontrada); }
.action-adopcion { border-left: 5px solid var(--adopcion); }
.action-buscar { border-left: 5px solid var(--brand); }

.publish-main { margin-top: 4px; }

.city-bar {
  display: grid;
  gap: 12px;
  margin-bottom: 22px;
}

.city-title { margin: 0 0 2px; font-size: 1.1rem; }
.city-bar p { margin: 0; }

.card-skeleton { height: 300px; }

.count { margin: 0 0 12px; }

/* --------------------------------------------------------------- paginador */

.pager {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-top: 22px;
}

.pages { display: flex; flex-wrap: wrap; align-items: center; gap: 4px; }

.page-btn {
  min-width: var(--tap);
  min-height: var(--tap);
  padding: 8px 12px;
  border: 1px solid transparent;
  border-radius: var(--radius);
  background: transparent;
  color: var(--text-soft);
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  cursor: pointer;
  transition:
    background var(--dur) var(--ease-out),
    color var(--dur) var(--ease-out),
    border-color var(--dur) var(--ease-out);
}

.page-btn:hover { background: var(--surface-2); color: var(--text); }

.page-btn.is-current {
  background: var(--brand);
  border-color: var(--brand);
  color: var(--brand-contrast);
}

.gap { padding: 0 2px; color: var(--text-muted); }

.help-grid { display: grid; gap: 14px; }
.help-grid h3 { margin-top: 0; }
.help-grid p { font-size: 0.95rem; }

@media (min-width: 480px) {
  .actions { grid-template-columns: 1fr 1fr; }
}

@media (min-width: 768px) {
  .hero { padding: 44px 0 20px; }
  .lead { font-size: 1.12rem; }
  .publish-main { justify-self: start; width: auto; padding-inline: 40px; }
  .city-bar { grid-template-columns: 1fr minmax(260px, 340px); align-items: center; }
  .help-grid { grid-template-columns: repeat(3, 1fr); }
}

@media (min-width: 1024px) {
  .actions { grid-template-columns: repeat(4, 1fr); }
  .action { flex-direction: column; align-items: flex-start; min-height: 128px; }
}
</style>
