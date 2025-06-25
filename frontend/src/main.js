import { createApp } from 'vue'
import App from './App.vue'
import router from './router.js'
import store from './store/index.js'

const app = createApp(App)

app.use(router)

// Usar store Pinia (gerenciamento de estado)
app.use(store)

app.mount('#app')

// Inicializar store uma única vez no aplicativo
import { useLibraryStore } from './store/library.js'
const libraryStore = useLibraryStore()
libraryStore.initialize()