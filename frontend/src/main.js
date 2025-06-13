import { createApp } from 'vue'
import App from './App.vue'
import router from './router.js'
import store from './store/index.js'

console.log('🚀 Iniciando Ohara...')
console.log('📍 Modo:', import.meta.env.MODE)
console.log('🌐 Base URL:', import.meta.env.BASE_URL)

const app = createApp(App)

app.use(router)

// Usar store Pinia (gerenciamento de estado)
app.use(store)

app.mount('#app')

console.log('Ohara carregado!')
console.log('Router atual:', router.currentRoute.value.path)

// Inicializar store uma única vez no aplicativo
import { useLibraryStore } from './store/library.js'
const libraryStore = useLibraryStore()
libraryStore.initialize()