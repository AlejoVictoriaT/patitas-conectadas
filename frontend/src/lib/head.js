/** Actualiza el título y la descripción de la página (útil para el historial y SEO básico). */

const BASE_TITLE = 'Patitas Conectadas'

export function setPageTitle(title) {
  document.title = title ? `${title} — ${BASE_TITLE}` : `${BASE_TITLE} — Mascotas perdidas, encontradas y en adopción`
}

export function setPageDescription(description) {
  if (!description) return
  let tag = document.querySelector('meta[name="description"]')
  if (!tag) {
    tag = document.createElement('meta')
    tag.setAttribute('name', 'description')
    document.head.appendChild(tag)
  }
  tag.setAttribute('content', description.slice(0, 300))
}
