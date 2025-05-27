import { createRouter, createWebHistory } from 'vue-router'

// Importar views de forma lazy (melhor para debug)
const LibraryView = () => import('@/views/LibraryView.vue')
const LibraryViewSimple = () => import('@/views/LibraryViewSimple.vue')

const routes = [
  {
    path: '/',
    name: 'Home',
    redirect: '/library'
  },
  {
    path: '/library',
    name: 'Library',
    component: LibraryViewSimple, // Usando versão simples para teste
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
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to) => {
  console.log('🔄 Navegando para:', to.path)
  if (to.meta.title) {
    document.title = to.meta.title
  }
})

export default router