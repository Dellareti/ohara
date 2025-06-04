import { createRouter, createWebHistory } from 'vue-router'

// Importar views
const LibraryView = () => import('@/views/LibraryView.vue')
const LibraryViewSimple = () => import('@/views/LibraryViewSimple.vue')
const MangaDetailView = () => import('@/views/MangaDetailView.vue')
const MangaReaderView = () => import('@/views/MangaReaderView.vue')

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
    path: '/library-full',
    name: 'LibraryFull', 
    component: LibraryView,
    meta: {
      title: 'Biblioteca Completa - Ohara'
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
  console.log('🔄 Navegando para:', to.path)
  
  // Atualizar título da página
  if (to.meta.title) {
    document.title = to.meta.title
  }
  
  // Simplesmente permitir navegação
  next()
})

export default router