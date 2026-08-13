import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  { path: '/', name: 'inicio', component: () => import('@/views/HomeView.vue') },
  { path: '/buscar', name: 'buscar', component: () => import('@/views/SearchView.vue') },
  {
    path: '/adopciones',
    name: 'adopciones',
    component: () => import('@/views/SearchView.vue'),
    props: { fixedType: 'adopcion' },
  },
  { path: '/publicar', name: 'publicar', component: () => import('@/views/PublishView.vue') },
  {
    path: '/mascotas/:type/:slug',
    name: 'mascota',
    component: () => import('@/views/PetDetailView.vue'),
    props: true,
  },
  {
    path: '/mis-publicaciones',
    name: 'mis-publicaciones',
    component: () => import('@/views/MyPostsView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/gestionar/:token',
    name: 'gestionar',
    component: () => import('@/views/ManageView.vue'),
    props: true,
  },
  {
    path: '/publicacion/:id/editar',
    name: 'editar',
    component: () => import('@/views/EditPostView.vue'),
    props: true,
  },
  { path: '/ingresar', name: 'ingresar', component: () => import('@/views/LoginView.vue') },
  { path: '/crear-cuenta', name: 'crear-cuenta', component: () => import('@/views/RegisterView.vue') },
  { path: '/auth/callback', name: 'auth-callback', component: () => import('@/views/AuthCallbackView.vue') },
  { path: '/noticias', name: 'noticias', component: () => import('@/views/NewsView.vue') },
  { path: '/noticias/:slug', name: 'noticia', component: () => import('@/views/ArticleView.vue'), props: true },
  {
    path: '/admin',
    name: 'admin',
    component: () => import('@/views/AdminView.vue'),
    meta: { requiresAdmin: true },
  },
  {
    path: '/legal/privacidad',
    name: 'privacidad',
    component: () => import('@/views/LegalView.vue'),
    props: { doc: 'privacidad' },
  },
  {
    path: '/legal/terminos',
    name: 'terminos',
    component: () => import('@/views/LegalView.vue'),
    props: { doc: 'terminos' },
  },
  { path: '/:pathMatch(.*)*', name: 'no-encontrado', component: () => import('@/views/NotFoundView.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, saved) {
    if (saved) return saved
    if (to.hash) return { el: to.hash, behavior: 'smooth' }
    return { top: 0 }
  },
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  await auth.init()

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'ingresar', query: { redirect: to.fullPath } }
  }
  if (to.meta.requiresAdmin && !auth.isAdmin) {
    return auth.isAuthenticated ? { name: 'inicio' } : { name: 'ingresar', query: { redirect: to.fullPath } }
  }
  return true
})

export default router
