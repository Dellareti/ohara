<template>
  <div class="library-simple">
    <header class="library-header">
      <h1>🏴‍☠️ Ohara - Biblioteca</h1>
      <p v-if="!libraryPath">Configure sua biblioteca de mangás</p>
      <p v-else>{{ mangaCount }} mangás encontrados</p>
      
      <!-- Status Indicator -->
      <div class="status-indicator" :class="{ 'connected': isConnected, 'disconnected': !isConnected }">
        <span class="status-dot"></span>
        <span>{{ isConnected ? 'Sistema Online' : 'Sistema Offline' }}</span>
      </div>
    </header>

    <!-- Seção de Configuração da Biblioteca -->
    <div v-if="!libraryPath" class="setup-section">
      <div class="setup-card">
        <h2>📂 Configurar Biblioteca</h2>
        <p>Selecione a pasta onde seus mangás estão organizados</p>
        
        <div class="path-input-section">
          <label for="library-path">Caminho da Biblioteca:</label>
          <div class="input-group">
            <input 
              id="library-path"
              v-model="inputPath" 
              type="text" 
              placeholder="/home/user/Mangas ou C:\Mangas"
              class="path-input"
              @keyup.enter="scanLibrary"
            />
            <button @click="scanLibrary" :disabled="scanning" class="scan-btn">
              {{ scanning ? '🔍 Escaneando...' : '📚 Escanear' }}
            </button>
          </div>
        </div>

        <div class="path-examples">
          <h4>💡 Exemplos de estrutura:</h4>
          <pre class="structure-example">
📁 Sua_Biblioteca/
├── 📁 One Piece/
│   ├── 📁 Capítulo 01/
│   │   ├── 01.jpg
│   │   └── 02.jpg
│   └── 📁 Capítulo 02/
├── 📁 Naruto/
└── 📁 Attack on Titan/</pre>
        </div>
      </div>
    </div>

    <!-- Seção da Biblioteca Escaneada -->
    <div v-else class="library-content">
      <div class="library-controls">
        <div class="library-info">
          <strong>📂 Biblioteca:</strong> {{ libraryPath }}
        </div>
        <div class="control-buttons">
          <button @click="refreshLibrary" :disabled="loading" class="refresh-btn">
            {{ loading ? '🔄 Atualizando...' : '🔄 Atualizar' }}
          </button>
          <button @click="changeLibrary" class="change-btn">
            📂 Trocar Pasta
          </button>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>{{ scanning ? 'Escaneando biblioteca...' : 'Carregando mangás...' }}</p>
      </div>

      <!-- Error -->
      <div v-if="error" class="error">
        <p>❌ {{ error }}</p>
        <button @click="refreshLibrary">🔄 Tentar novamente</button>
      </div>

      <!-- Grid de Mangás -->
      <div v-if="!loading && !error && mangas.length > 0" class="manga-grid">
        <div 
          v-for="manga in mangas" 
          :key="manga.id"
          class="manga-card"
          @click="selectManga(manga)"
        >
          <div class="manga-thumbnail">
            <img v-if="manga.thumbnail" :src="manga.thumbnail" :alt="manga.title" />
            <div v-else class="placeholder-thumbnail">📚</div>
          </div>
          <div class="manga-info">
            <h3>{{ manga.title }}</h3>
            <p>{{ manga.chapter_count }} capítulos</p>
            <p class="total-pages">{{ manga.total_pages }} páginas</p>
            <div class="manga-path">{{ manga.path }}</div>
          </div>
        </div>
      </div>

      <!-- Estado Vazio -->
      <div v-if="!loading && !error && mangas.length === 0" class="empty-state">
        <h3>📭 Nenhum mangá encontrado</h3>
        <p>Verifique se a pasta contém mangás organizados em subpastas</p>
        <button @click="changeLibrary" class="change-btn">📂 Escolher Outra Pasta</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useLibraryStore } from '@/store/library'

export default {
  name: 'LibraryViewSimple',
  setup() {
    // Store global
    const libraryStore = useLibraryStore()
    
    // Reactive data local
    const inputPath = ref('')
    const isConnected = ref(false)

    // Computed properties que vêm do store
    const libraryPath = computed(() => libraryStore.libraryPath)
    const mangas = computed(() => libraryStore.mangas)
    const mangaCount = computed(() => libraryStore.totalMangas)
    const loading = computed(() => libraryStore.loading)
    const scanning = computed(() => libraryStore.scanning)
    const error = computed(() => libraryStore.error)

    // Backend status check
    const checkBackendStatus = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/test', {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' }
        })
        
        if (response.ok) {
          isConnected.value = true
          console.log('✅ Backend conectado')
        } else {
          isConnected.value = false
          console.log('❌ Backend com erro:', response.status)
        }
      } catch (error) {
        isConnected.value = false
        console.log('❌ Backend desconectado:', error.message)
      }
    }

    // Methods que usam o store
    const scanLibrary = async () => {
      if (!inputPath.value.trim()) {
        alert('Por favor, digite o caminho da biblioteca')
        return
      }

      try {
        console.log('🔍 Escaneando nova biblioteca:', inputPath.value.trim())
        await libraryStore.scanLibrary(inputPath.value.trim())
        console.log('✅ Escaneamento concluído!')
      } catch (err) {
        console.error('❌ Erro ao escanear:', err)
        alert(`Erro ao escanear biblioteca:\n${err.message}`)
      }
    }

    const refreshLibrary = async () => {
      try {
        console.log('🔄 Atualizando biblioteca...')
        await libraryStore.refreshLibrary()
        console.log('✅ Biblioteca atualizada!')
      } catch (err) {
        console.error('❌ Erro ao atualizar:', err)
        alert(`Erro ao atualizar biblioteca:\n${err.message}`)
      }
    }

    const changeLibrary = async () => {
      try {
        console.log('📂 Trocando biblioteca...')
        
        // Limpar biblioteca completamente
        await libraryStore.clearLibrary()
        
        // Limpar input local
        inputPath.value = ''
        
        console.log('✅ Biblioteca limpa, pronto para nova configuração')
        
      } catch (err) {
        console.error('❌ Erro ao trocar biblioteca:', err)
        alert(`Erro ao trocar biblioteca:\n${err.message}`)
      }
    }

    const selectManga = (manga) => {
      console.log('📖 Mangá selecionado:', manga.title)
      alert(`Você selecionou: ${manga.title}\n\nCapítulos: ${manga.chapter_count}\nPáginas: ${manga.total_pages}\n\n(Em breve: navegação para detalhes do mangá)`)
    }

    // Lifecycle
    onMounted(async () => {
      // Verificar backend na inicialização
      checkBackendStatus()
      
      // Verificar backend a cada 30 segundos
      setInterval(checkBackendStatus, 30000)
      
      // Carregar caminho salvo para o input apenas se não há biblioteca
      if (!libraryStore.libraryPath && libraryStore.libraryPath) {
        inputPath.value = libraryStore.libraryPath
      }
      
      // Inicializar store apenas se necessário
      if (!libraryStore.isInitialized) {
        console.log('🚀 Inicializando store pela primeira vez...')
        await libraryStore.initialize()
      } else {
        console.log('📋 Store já inicializado, usando dados em cache')
      }
    })

    return {
      // Data reativa
      inputPath,
      isConnected,
      
      // Computed do store
      libraryPath,
      mangas,
      mangaCount,
      loading,
      scanning,
      error,
      
      // Methods
      scanLibrary,
      refreshLibrary,
      changeLibrary,
      selectManga
    }
  }
}
</script>

<style scoped>
.library-simple {
  min-height: 100vh;
  background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
  color: white;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  padding: 2rem;
}

.library-header {
  text-align: center;
  margin-bottom: 3rem;
}

.library-header h1 {
  font-size: 3rem;
  margin-bottom: 1rem;
  background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.library-header p {
  font-size: 1.2rem;
  opacity: 0.8;
  margin-bottom: 1rem;
}

/* Status Indicator */
.status-indicator {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-radius: 15px;
  font-size: 0.85rem;
  font-weight: 500;
  transition: all 0.3s ease;
  margin-top: 0.5rem;
}

.status-indicator.connected {
  background: rgba(76, 175, 80, 0.15);
  color: #4CAF50;
  border: 1px solid rgba(76, 175, 80, 0.3);
}

.status-indicator.disconnected {
  background: rgba(244, 67, 54, 0.15);
  color: #F44336;
  border: 1px solid rgba(244, 67, 54, 0.3);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

/* Setup Section */
.setup-section {
  max-width: 800px;
  margin: 0 auto;
}

.setup-card {
  background: rgba(255, 255, 255, 0.1);
  padding: 3rem;
  border-radius: 20px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.setup-card h2 {
  color: #4ecdc4;
  margin-bottom: 1rem;
  text-align: center;
}

.path-input-section {
  margin: 2rem 0;
}

.path-input-section label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
}

.input-group {
  display: flex;
  gap: 1rem;
}

.path-input {
  flex: 1;
  padding: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  background: rgba(0, 0, 0, 0.3);
  color: white;
  font-size: 1rem;
}

.path-input:focus {
  outline: none;
  border-color: #4ecdc4;
}

.scan-btn {
  background: linear-gradient(45deg, #4ecdc4, #44a08d);
  border: none;
  padding: 1rem 2rem;
  border-radius: 10px;
  color: white;
  cursor: pointer;
  font-weight: bold;
  transition: transform 0.2s;
}

.scan-btn:hover:not(:disabled) {
  transform: scale(1.05);
}

.scan-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.path-examples {
  margin: 2rem 0;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 10px;
}

.structure-example {
  background: rgba(0, 0, 0, 0.5);
  padding: 1rem;
  border-radius: 5px;
  font-size: 0.9rem;
  overflow-x: auto;
}

/* Library Content */
.library-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  flex-wrap: wrap;
  gap: 1rem;
}

.library-info {
  font-size: 0.9rem;
  opacity: 0.8;
  word-break: break-all;
}

.control-buttons {
  display: flex;
  gap: 1rem;
}

.refresh-btn, .change-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
}

.refresh-btn {
  background: #4ecdc4;
  color: white;
}

.change-btn {
  background: #ff6b6b;
  color: white;
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Loading */
.loading {
  text-align: center;
  padding: 4rem 2rem;
}

.spinner {
  width: 60px;
  height: 60px;
  border: 4px solid rgba(255,255,255,0.3);
  border-radius: 50%;
  border-top: 4px solid #4ecdc4;
  animation: spin 1s linear infinite;
  margin: 0 auto 2rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Error */
.error {
  text-align: center;
  padding: 2rem;
  background: rgba(255, 107, 107, 0.1);
  border-radius: 10px;
  margin: 2rem 0;
  border: 1px solid rgba(255, 107, 107, 0.3);
}

.error button {
  background: #ff6b6b;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  margin-top: 1rem;
}

/* Manga Grid */
.manga-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 2rem;
  margin-top: 2rem;
}

.manga-card {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  padding: 1.5rem;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
  cursor: pointer;
}

.manga-card:hover {
  transform: translateY(-5px);
  background: rgba(255, 255, 255, 0.15);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.manga-thumbnail {
  text-align: center;
  margin-bottom: 1rem;
}

.manga-thumbnail img {
  width: 100%;
  height: 200px;
  object-fit: cover;
  border-radius: 10px;
}

.placeholder-thumbnail {
  width: 100%;
  height: 200px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 4rem;
}

.manga-info h3 {
  margin: 1rem 0 0.5rem;
  color: #4ecdc4;
  font-size: 1.3rem;
}

.manga-info p {
  margin: 0.25rem 0;
  opacity: 0.8;
}

.total-pages {
  color: #ffeaa7;
  font-size: 0.9rem;
}

.manga-path {
  font-size: 0.8rem;
  opacity: 0.6;
  margin-top: 0.5rem;
  word-break: break-all;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  opacity: 0.8;
}

.empty-state h3 {
  color: #4ecdc4;
  margin-bottom: 1rem;
}

/* Responsive */
@media (max-width: 768px) {
  .library-simple {
    padding: 1rem;
  }
  
  .library-header h1 {
    font-size: 2rem;
  }
  
  .setup-card {
    padding: 2rem 1rem;
  }
  
  .input-group {
    flex-direction: column;
  }
  
  .library-controls {
    flex-direction: column;
    text-align: center;
  }
  
  .manga-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
}
</style>