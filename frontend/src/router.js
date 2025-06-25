import { createRouter, createWebHistory } from 'vue-router'

// Importar views
const LibraryViewSimple = () => import('@/views/LibraryViewSimple.vue')
const MangaDetailView = () => import('@/views/MangaDetailView.vue')
const MangaReaderView = () => import('@/views/MangaReaderView.vue')
const SettingsView = () => import('@/views/SettingsView.vue')
const ManualView = () => import('@/views/ManualView.vue')

// Importar componentes
const LibrarySetup = () => import('@/components/LibrarySetup.vue')

const routes = [
  {
    path: '/',
    name: 'Home',
    redirect: '/library'
  },
  {
    path: '/library',
    name: 'Library',
    component: LibraryViewSimple,
    meta: {
      title: 'Biblioteca - Ohara'
    }
  },
  {
    path: '/setup',
    name: 'Setup',
    component: LibrarySetup,
    meta: {
      title: 'Configurar Biblioteca - Ohara'
    }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: SettingsView,
    meta: {
      title: 'Configurações - Ohara'
    }
  },
  {
    path: '/manual',
    name: 'Manual',
    component: ManualView,
    meta: {
      title: 'Manual de Uso - Ohara'
    }
  },
  {
    path: '/manga/:id',
    name: 'MangaDetail',
    component: MangaDetailView,
    meta: {
      title: 'Detalhes do Mangá - Ohara'
    }
  },
  {
    path: '/manga/:mangaId/chapter/:chapterId',
    name: 'MangaReader',
    component: MangaReaderView,
    meta: {
      title: 'Leitor - Ohara'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  
  // Atualizar título da página
  if (to.meta.title) {
    document.title = to.meta.title
  }
  
  // Simplesmente permitir navegação
  next()
})

export default router