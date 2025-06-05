<template>
  <div class="library-simple">
    <!-- Header com navegação -->
    <div class="header">
      <h1>Biblioteca</h1>
      <div class="header-actions">
        <router-link to="/setup" class="setup-btn">Configuração</router-link>
        <button @click="refreshLibrary" class="refresh-btn">🔄 Atualizar</button>
      </div>
    </div>
    
    <!-- Descomentar ou excluir depois -->
    <!-- Stats da biblioteca -->
    <!-- <div v-if="libraryStore.mangas.length > 0" class="library-stats">
      <div class="stat-card">
        <div class="stat-number">{{ libraryStore.totalMangas }}</div>
        <div class="stat-label">Mangás</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">{{ libraryStore.totalChapters }}</div>
        <div class="stat-label">Capítulos</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">{{ formatPages(totalPages) }}</div>
        <div class="stat-label">Páginas</div>
      </div>
    </div> -->

    <!-- Loading -->
    <div v-if="libraryStore.loading" class="loading-section">
      <div class="spinner"></div>
      <p>Carregando biblioteca...</p>
    </div>

    <!-- Error -->
    <div v-if="libraryStore.error" class="error-section">
      <p>❌ {{ libraryStore.error }}</p>
      <button @click="loadLibrary" class="retry-btn">🔄 Tentar novamente</button>
    </div>

    <!-- Biblioteca vazia -->
    <div v-if="!libraryStore.loading && !libraryStore.error && libraryStore.mangas.length === 0" class="empty-library">
      <div class="empty-icon">📚</div>
      <h2>Biblioteca Vazia</h2>
      <p>Configure sua biblioteca para começar a leitura</p>
      <router-link to="/setup" class="setup-link">⚙️ Configurar Agora</router-link>
    </div>

    <!-- Grid de Mangás -->
    <div v-if="!libraryStore.loading && !libraryStore.error && libraryStore.mangas.length > 0" class="manga-grid">
      <div 
        v-for="manga in libraryStore.mangas" 
        :key="manga.id"
        class="manga-card"
        @click="selectManga(manga)"
      >
        <div class="manga-thumbnail">
          <img 
            v-if="manga.thumbnail" 
            :src="getThumbnailUrl(manga.thumbnail)"
            :alt="manga.title"
            @error="onImageError"
          />
          <div v-else class="placeholder-thumbnail">
            📖
          </div>
        </div>
        
        <div class="manga-info">
          <h3>{{ manga.title }}</h3>
          <div class="manga-meta">
            <span class="chapter-count">{{ manga.chapter_count || 0 }} capítulos</span>
            <span v-if="manga.author" class="author">{{ manga.author }}</span>
            <span v-if="manga.status" class="status" :class="manga.status.toLowerCase()">
              {{ manga.status }}
            </span>
          </div>
          <div v-if="manga.genres && manga.genres.length" class="genres">
            <span v-for="genre in manga.genres.slice(0, 3)" :key="genre" class="genre">
              {{ genre }}
            </span>
          </div>
        </div>
      </div>
    </div>  
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useLibraryStore } from '@/store/library'

export default {
  name: 'LibraryViewSimple',
  setup() {
    const router = useRouter()
    const libraryStore = useLibraryStore()
    const testResult = ref('')

    // Computed
    const totalPages = computed(() => {
      return libraryStore.mangas.reduce((sum, manga) => sum + (manga.total_pages || 0), 0)
    })

    // Methods
    const loadLibrary = async () => {
      try {
        await libraryStore.fetchLibrary()
      } catch (error) {
        console.error('❌ Erro ao carregar biblioteca:', error)
      }
    }

    const refreshLibrary = async () => {
      if (libraryStore.libraryPath) {
        try {
          await libraryStore.scanLibrary()
        } catch (error) {
          console.error('❌ Erro ao atualizar biblioteca:', error)
        }
      } else {
        await loadLibrary()
      }
    }

    const selectManga = (manga) => {
      console.log('📖 Mangá selecionado:', manga.title)
      
      // Navegar para página de detalhes
      router.push({
        name: 'MangaDetail',
        params: { id: manga.id }
      })
    }

    const getThumbnailUrl = (thumbnailPath) => {
      if (!thumbnailPath) return null
      
      // Se for um caminho absoluto, converter para URL da API
      if (thumbnailPath.startsWith('/')) {
        return `http://localhost:8000/api/image?path=${encodeURIComponent(thumbnailPath)}`
      }
      
      return thumbnailPath
    }

    const onImageError = (event) => {
      // Esconder imagem quebrada e mostrar placeholder
      event.target.style.display = 'none'
      event.target.parentElement.innerHTML = '<div class="placeholder-thumbnail">📖</div>'
    }

    const formatPages = (pages) => {
      if (pages > 1000) {
        return (pages / 1000).toFixed(1) + 'k'
      }
      return pages.toString()
    }

    const testBackend = async () => {
      try {
        console.log('🔄 Testando backend...')
        const response = await fetch('http://localhost:8000/api/test')
        const data = await response.json()
        testResult.value = JSON.stringify(data, null, 2)
        console.log('✅ Backend funcionando:', data)
      } catch (error) {
        testResult.value = `❌ Erro: ${error.message}`
        console.error('❌ Erro ao testar backend:', error)
      }
    }

    const loadMockData = async () => {
      try {
        await libraryStore.loadMockData()
        console.log('✅ Dados mock carregados')
      } catch (error) {
        console.error('❌ Erro ao carregar mock:', error)
      }
    }

    // Lifecycle
    onMounted(async () => {
      // Recuperar configuração salva
      libraryStore.loadSavedConfiguration()
      
      // Carregar biblioteca se já configurada
      if (libraryStore.libraryPath) {
        await refreshLibrary()
      } else {
        await loadLibrary()
      }
    })

    return {
      libraryStore,
      testResult,
      totalPages,
      loadLibrary,
      refreshLibrary,
      selectManga,
      getThumbnailUrl,
      onImageError,
      formatPages,
      testBackend,
      loadMockData
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
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 30px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.header h1 {
  font-size: 2.5rem;
  margin: 0;
  background: #fff;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.header-actions {
  display: flex;
  gap: 15px;
}

.setup-btn,
.refresh-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 10px;
  font-weight: bold;
  cursor: pointer;
  text-decoration: none;
  transition: all 0.3s ease;
}

.setup-btn {
  background: linear-gradient(45deg, #4ecdc4, #44a08d);
  color: white;
}

.refresh-btn {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.setup-btn:hover,
.refresh-btn:hover {
  transform: translateY(-2px);
}

.library-stats {
  display: flex;
  justify-content: center;
  gap: 30px;
  padding: 30px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.1);
  padding: 20px 30px;
  border-radius: 15px;
  text-align: center;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.stat-number {
  font-size: 2rem;
  font-weight: bold;
  color: #fff;
}

.stat-label {
  font-size: 0.9rem;
  opacity: 0.8;
  margin-top: 5px;
}

.loading-section,
.error-section,
.empty-library {
  text-align: center;
  padding: 60px 20px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255,255,255,0.3);
  border-radius: 50%;
  border-top: 4px solid #4ecdc4;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-section {
  background: rgba(255, 107, 107, 0.1);
  border-radius: 15px;
  margin: 20px;
}

.retry-btn {
  background: #ff6b6b;
  border: none;
  padding: 10px 20px;
  border-radius: 10px;
  color: white;
  cursor: pointer;
  margin-top: 15px;
}

.empty-library {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 20px;
  margin: 20px;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.setup-link {
  display: inline-block;
  background: linear-gradient(45deg, #4ecdc4, #44a08d);
  color: white;
  text-decoration: none;
  padding: 15px 30px;
  border-radius: 15px;
  font-weight: bold;
  margin-top: 20px;
  transition: transform 0.3s ease;
}

.setup-link:hover {
  transform: translateY(-3px);
}

.manga-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 25px;
  padding: 30px;
}

.manga-card {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 20px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
  cursor: pointer;
}

.manga-card:hover {
  transform: translateY(-8px);
  background: rgba(255, 255, 255, 0.15);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.manga-thumbnail {
  width: 100%;
  height: 300px;
  margin-bottom: 15px;
  border-radius: 15px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.05);
}

.manga-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.placeholder-thumbnail {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 4rem;
  background: linear-gradient(135deg, rgba(78, 205, 196, 0.2), rgba(255, 107, 107, 0.2));
}

.manga-info h3 {
  margin: 0 0 10px 0;
  color: #fff;
  font-size: 1.3rem;
  line-height: 1.3;
}

.manga-meta {
  display: flex;
  flex-direction: column;
  gap: 5px;
  margin-bottom: 10px;
}

.chapter-count {
  font-weight: bold;
  color: #fff;
}

.author {
  font-size: 0.9rem;
  opacity: 0.8;
}

.status {
  font-size: 0.8rem;
  padding: 2px 8px;
  border-radius: 12px;
  align-self: flex-start;
}

.status.ongoing {
  background: rgba(76, 175, 80, 0.3);
  color: #4caf50;
}

.status.completed {
  background: rgba(33, 150, 243, 0.3);
  color: #2196f3;
}

.genres {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.genre {
  font-size: 0.7rem;
  background: rgba(255, 255, 255, 0.2);
  padding: 2px 6px;
  border-radius: 8px;
  opacity: 0.8;
}

.test-section {
  margin: 30px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 15px;
  padding: 20px;
}

.test-section summary {
  cursor: pointer;
  font-weight: bold;
  padding: 10px 0;
}

.test-content {
  padding-top: 15px;
}

.test-btn {
  background: linear-gradient(45deg, #ff9f43, #ff7675);
  border: none;
  padding: 10px 20px;
  border-radius: 10px;
  color: white;
  cursor: pointer;
  margin-right: 10px;
  margin-bottom: 10px;
}

.test-btn:hover {
  transform: translateY(-2px);
}

.result {
  margin-top: 15px;
  padding: 15px;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 10px;
  border-left: 4px solid #4ecdc4;
}

.result pre {
  background: rgba(0, 0, 0, 0.7);
  padding: 10px;
  border-radius: 5px;
  overflow-x: auto;
  white-space: pre-wrap;
  font-size: 0.8rem;
}

@media (max-width: 768px) {
  .header {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .header h1 {
    font-size: 2rem;
  }
  
  .library-stats {
    flex-direction: column;
    align-items: center;
  }
  
  .manga-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 20px;
    padding: 20px;
  }
}
</style>