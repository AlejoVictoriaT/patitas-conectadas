<script setup>
/**
 * Navegación inferior de celular.
 *
 * Cuatro destinos fijos + «Más». Los fijos son los que se usan a diario; el
 * resto vive en una hoja que sube desde abajo.
 *
 * Por qué existe «Más»: el menú del encabezado (`AppHeader`) solo aparece a
 * partir de 768px y no hay botón de hamburguesa, así que en celular —que es
 * de donde viene casi todo el tráfico— Guías, Emergencia y el panel de
 * administración no se podían abrir por ningún lado, y Noticias solo desde un
 * enlace del pie. Esta hoja es la que los vuelve alcanzables.
 */
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const open = ref(false)
const moreBtn = ref(null)
const sheet = ref(null)

// Rutas que solo se alcanzan desde la hoja: mientras se esté en una de ellas,
// «Más» queda marcado. Sin esto la barra no señalaría nada y se sentiría rota.
const RUTAS_EN_HOJA = [
  'guias', 'guia', 'emergencia', 'noticias',
  'mis-publicaciones', 'admin', 'ingresar', 'crear-cuenta',
  'privacidad', 'terminos',
]

const moreActive = computed(() => RUTAS_EN_HOJA.includes(route.name))

function alternar() {
  if (open.value) cerrar()
  else open.value = true
}

function cerrar() {
  if (!open.value) return
  open.value = false
  // El foco vuelve al botón que abrió: si se pierde, el lector de pantalla
  // arranca de nuevo desde el principio del documento.
  moreBtn.value?.focus()
}

function onKey(event) {
  if (event.key === 'Escape') cerrar()
}

function logout() {
  auth.logout()
  cerrar()
  router.push({ name: 'inicio' })
}

// Navegar cierra la hoja. Se observa la ruta completa y no solo el nombre para
// que también cierre al cambiar de guía dentro de /guias/:slug.
watch(() => route.fullPath, () => { open.value = false })

watch(open, (abierta) => {
  if (abierta) {
    document.addEventListener('keydown', onKey)
    document.body.style.overflow = 'hidden'
    // Se espera al siguiente fotograma: el panel aún no está en el DOM.
    requestAnimationFrame(() => sheet.value?.focus())
  } else {
    document.removeEventListener('keydown', onKey)
    document.body.style.overflow = ''
  }
})

/*
  A partir de 768px la barra y la hoja se ocultan por CSS (`hide-desktop`), pero
  ocultar no es cerrar: el `overflow: hidden` del body seguiría puesto y la
  página quedaría sin scroll. Pasa de verdad al girar una tablet de vertical a
  horizontal con la hoja abierta. Se cierra al cruzar el umbral.
*/
const escritorio = window.matchMedia('(min-width: 768px)')

function alCambiarAncho(event) {
  if (event.matches) open.value = false
}

escritorio.addEventListener('change', alCambiarAncho)

onBeforeUnmount(() => {
  document.removeEventListener('keydown', onKey)
  escritorio.removeEventListener('change', alCambiarAncho)
  document.body.style.overflow = ''
})
</script>

<template>
  <nav class="tabbar hide-desktop" aria-label="Navegación">
    <router-link to="/" class="tab" exact-active-class="is-active">
      <span aria-hidden="true">🏠</span>
      <small>Inicio</small>
    </router-link>
    <router-link to="/buscar" class="tab" active-class="is-active">
      <span aria-hidden="true">🔎</span>
      <small>Buscar</small>
    </router-link>

    <router-link to="/publicar" class="tab tab-cta" aria-label="Publicar una mascota">
      <span class="cta-circle" aria-hidden="true">🐾</span>
      <small>Publicar</small>
    </router-link>

    <router-link to="/adopciones" class="tab" active-class="is-active">
      <span aria-hidden="true">💙</span>
      <small>Adoptar</small>
    </router-link>

    <button
      ref="moreBtn"
      type="button"
      class="tab tab-more"
      :class="{ 'is-active': moreActive || open }"
      aria-haspopup="dialog"
      :aria-expanded="open"
      @click="alternar"
    >
      <span aria-hidden="true">☰</span>
      <small>Más</small>
    </button>
  </nav>

  <!--
    Teleport al <body> por lo mismo que el modal: `position: fixed` deja de
    medirse contra la pantalla si algún ancestro tiene `transform`, y la barra
    lleva animaciones. Fuera del árbol no hay forma de que quede recortada.
  -->
  <Teleport to="body">
    <Transition name="sheet">
      <div v-if="open" class="sheet-backdrop hide-desktop" @click.self="cerrar">
        <div
          ref="sheet"
          class="sheet"
          role="dialog"
          aria-modal="true"
          aria-label="Más opciones"
          tabindex="-1"
        >
          <div class="grabber" aria-hidden="true"></div>

          <p class="sheet-group">Explorar</p>
          <div class="sheet-links">
            <router-link to="/guias" class="sheet-link">
              <span class="ico" aria-hidden="true">📖</span>
              <span>
                <strong>Guías</strong>
                <small>Qué hacer paso a paso</small>
              </span>
            </router-link>
            <router-link to="/emergencia" class="sheet-link">
              <span class="ico" aria-hidden="true">🚨</span>
              <span>
                <strong>Emergencia</strong>
                <small>Teléfonos y entidades de atención</small>
              </span>
            </router-link>
            <router-link to="/noticias" class="sheet-link">
              <span class="ico" aria-hidden="true">📰</span>
              <span>
                <strong>Noticias</strong>
                <small>Adopción, salud y buenas historias</small>
              </span>
            </router-link>
          </div>

          <p class="sheet-group">Tu cuenta</p>
          <div class="sheet-links">
            <template v-if="auth.isAuthenticated">
              <router-link to="/mis-publicaciones" class="sheet-link">
                <span class="ico" aria-hidden="true">📋</span>
                <span>
                  <strong>Mis publicaciones</strong>
                  <small>Editar, cambiar estado o cerrar un caso</small>
                </span>
              </router-link>
              <router-link v-if="auth.isAdmin" to="/admin" class="sheet-link">
                <span class="ico" aria-hidden="true">🛡️</span>
                <span>
                  <strong>Panel administrativo</strong>
                  <small>Reportes, contenido y métricas</small>
                </span>
              </router-link>
              <button type="button" class="sheet-link" @click="logout">
                <span class="ico" aria-hidden="true">🚪</span>
                <span>
                  <strong>Cerrar sesión</strong>
                  <small>{{ auth.displayName }}</small>
                </span>
              </button>
            </template>
            <template v-else>
              <router-link to="/ingresar" class="sheet-link">
                <span class="ico" aria-hidden="true">👤</span>
                <span>
                  <strong>Iniciar sesión</strong>
                  <small>Para reunir tus publicaciones en un solo lugar</small>
                </span>
              </router-link>
              <router-link to="/crear-cuenta" class="sheet-link">
                <span class="ico" aria-hidden="true">✨</span>
                <span>
                  <strong>Crear cuenta</strong>
                  <small>No hace falta para publicar</small>
                </span>
              </router-link>
            </template>
          </div>

          <nav class="sheet-legal" aria-label="Enlaces legales">
            <router-link to="/legal/privacidad">Privacidad</router-link>
            <span aria-hidden="true">·</span>
            <router-link to="/legal/terminos">Términos</router-link>
          </nav>

          <button type="button" class="btn btn-quiet btn-block sheet-close" @click="cerrar">
            Cerrar
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.tabbar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 45;
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  align-items: end;
  background: var(--surface);
  border-top: 1px solid var(--border);
  padding: 6px 4px calc(6px + env(safe-area-inset-bottom, 0px));
  box-shadow: 0 -2px 12px rgba(31, 41, 51, 0.06);
}

.tab {
  display: grid;
  justify-items: center;
  gap: 2px;
  padding: 6px 2px;
  min-height: 52px;
  color: var(--text-muted);
  font-size: 1.15rem;
  text-decoration: none;
  border-radius: var(--radius-sm);
}
.tab:hover { text-decoration: none; }

.tab small {
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.01em;
}

.tab.is-active { color: var(--brand); }

/* «Más» es un botón, no un enlace: hay que devolverle la apariencia de pestaña
   que el navegador le quita. */
.tab-more {
  border: none;
  background: none;
  font: inherit;
  font-size: 1.15rem;
  cursor: pointer;
  align-content: center;
}

.tab-cta { color: var(--brand); }

.cta-circle {
  display: grid;
  place-items: center;
  width: 48px;
  height: 48px;
  margin-top: -20px;
  border-radius: 50%;
  background: var(--brand);
  color: #fff;
  font-size: 1.3rem;
  box-shadow: 0 6px 16px rgba(15, 118, 110, 0.35);
  border: 3px solid var(--bg);
}

/* ------------------------------------------------------------------- hoja */

.sheet-backdrop {
  position: fixed;
  inset: 0;
  z-index: 60; /* por encima de la barra (45) y del encabezado (40) */
  display: flex;
  align-items: flex-end;
  background: rgba(31, 41, 51, 0.45);
  backdrop-filter: blur(2px);
}

.sheet {
  width: 100%;
  max-height: 85vh;
  overflow-y: auto;
  background: var(--surface);
  border-radius: var(--radius-lg) var(--radius-lg) 0 0;
  box-shadow: var(--shadow-lg);
  padding: 8px 16px calc(16px + env(safe-area-inset-bottom, 0px));
  outline: none;
}

.grabber {
  width: 40px;
  height: 4px;
  margin: 4px auto 12px;
  border-radius: var(--radius-pill);
  background: var(--border-strong);
}

.sheet-group {
  margin: 14px 0 6px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-muted);
}
.sheet-group:first-of-type { margin-top: 4px; }

.sheet-links { display: grid; gap: 2px; }

.sheet-link {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  min-height: var(--tap);
  padding: 10px 8px;
  border: none;
  border-radius: var(--radius);
  background: none;
  color: var(--text);
  text-align: left;
  text-decoration: none;
  font: inherit;
  cursor: pointer;
}
.sheet-link:hover,
.sheet-link:active {
  background: var(--surface-2);
  text-decoration: none;
}
.sheet-link.router-link-active {
  background: var(--brand-light);
  color: var(--brand-dark);
}

.sheet-link .ico {
  display: grid;
  place-items: center;
  flex: none;
  width: 38px;
  height: 38px;
  border-radius: var(--radius-sm);
  background: var(--surface-2);
  font-size: 1.15rem;
}
.sheet-link.router-link-active .ico { background: var(--surface); }

.sheet-link strong {
  display: block;
  font-size: 0.98rem;
  font-weight: 600;
  line-height: 1.3;
}
.sheet-link small {
  display: block;
  color: var(--text-muted);
  font-size: 0.8rem;
  line-height: 1.35;
}

.sheet-legal {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-top: 16px;
  font-size: 0.85rem;
  color: var(--text-muted);
}
.sheet-legal a { color: var(--text-soft); }

.sheet-close { margin-top: 12px; }

/* Entrada: el fondo se funde y el panel sube. `prefers-reduced-motion` ya lo
   neutraliza globalmente en main.css. */
.sheet-enter-active,
.sheet-leave-active {
  transition: opacity var(--dur) var(--ease-out);
}
.sheet-enter-active .sheet,
.sheet-leave-active .sheet {
  transition: transform var(--dur) var(--ease-out);
}
.sheet-enter-from,
.sheet-leave-to { opacity: 0; }
.sheet-enter-from .sheet,
.sheet-leave-to .sheet { transform: translateY(100%); }
</style>
