<template>
  <footer class="site-footer">
    <div class="container footer-inner">
      <div>
        <strong>🐾 Patitas Conectadas</strong>
        <p class="text-muted">
          Una herramienta sencilla para reunir mascotas con su familia y encontrar nuevos hogares.
        </p>
      </div>

      <nav aria-label="Enlaces del pie">
        <router-link to="/buscar">Buscar mascotas</router-link>
        <router-link to="/publicar">Publicar</router-link>
        <router-link to="/noticias">Noticias y ayuda</router-link>
        <router-link to="/legal/privacidad">Política de privacidad</router-link>
        <router-link to="/legal/terminos">Términos y condiciones</router-link>
      </nav>
    </div>
  </footer>
</template>

<style scoped>
.site-footer {
  border-top: 1px solid var(--border);
  background: var(--surface-2);
  padding: 28px 0;
  margin-top: 32px;
}

.footer-inner {
  display: grid;
  gap: 20px;
}

.footer-inner p { margin: 6px 0 0; max-width: 42ch; }

nav {
  display: grid;
  gap: 8px;
}

nav a {
  color: var(--text-soft);
  font-size: 0.95rem;
}

@media (min-width: 768px) {
  .footer-inner {
    grid-template-columns: 1fr auto;
    align-items: start;
  }
  nav {
    grid-template-columns: repeat(2, auto);
    column-gap: 32px;
  }
}
</style>
