<template>
  <div class="manga-detail">
    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Carregando detalhes do mangá...</p>
    </div>

    <!-- Error State -->
    <div v-if="error" class="error-state">
      <h2>❌ Erro ao Carregar Mangá</h2>
      <p>{{ error }}</p>
      <button @click="loadManga" class="retry-btn">🔄 Tentar Novamente</button>
    </div>

    <!-- Manga Content -->
    <div v-if="manga && !loading" class="manga-content">
      <!-- Header com Info do Mangá -->
      <div class="manga-header">
        <div class="manga-cover">
          <img 
            v-if="manga.thumbnail" 
            :src="manga.thumbnail" 
            :alt="manga.title"
            class="cover-image"
          />
          <div v-else class="cover-placeholder">📚</div>
          
          <!-- Ações Rápidas -->
          <div class="quick-actions">
            <button @click="continueReading" class="continue-btn">
              📖 Continuar Leitura
            </button>
            <button @click="markAsRead" class="mark-read-btn">
              ✅ Marcar como Lido
            </button>
            <button @click="addToFavorites" class="favorite-btn">
              {{ manga.isFavorite ? '💖' : '🤍' }} Favorito
            </button>
          </div>
        </div>

        <div class="manga-info">
          <h1>{{ manga.title }}</h1>
          
          <!-- Metadados -->
          <div class="metadata">
            <div class="meta-item" v-if="manga.author">
              <strong>✍️ Autor:</strong> {{ manga.author }}
            </div>
            <div class="meta-item" v-if="manga.artist">
              <strong>🎨 Artista:</strong> {{ manga.artist }}
            </div>
            <div class="meta-item" v-if="manga.status">
              <strong>📊 Status:</strong> 
              <span :class="statusClass">{{ manga.status }}</span>
            </div>
            <div class="meta-item" v-if="manga.genres && manga.genres.length">
              <strong>🏷️ Gêneros:</strong>
              <div class="genres">
                <span v-for="genre in manga.genres" :key="genre" class="genre-tag">
                  {{ genre }}
                </span>
              </div>
            </div>
          </div>

          <!-- Estatísticas -->
          <div class="stats">
            <div class="stat-item">
              <div class="stat-number">{{ manga.chapter_count }}</div>
              <div class="stat-label">Capítulos</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">{{ manga.total_pages }}</div>
              <div class="stat-label">Páginas</div>
            </div>
            <div class="stat-item">
              <div class="stat-number">{{ readProgress }}%</div>
              <div class="stat-label">Progresso</div>
            </div>
          </div>

          <!-- Descrição -->
          <div v-if="manga.description" class="description">
            <h3>📝 Descrição</h3>
            <p>{{ manga.description }}</p>
          </div>
        </div>
      </div>

      <!-- Filtros e Ordenação -->
      <div class="chapter-controls">
        <div class="view-controls">
          <button 
            @click="viewMode = 'list'" 
            :class="{ active: viewMode === 'list' }"
            class="view-btn"
          >
            📋 Lista
          </button>
          <button 
            @click="viewMode = 'grid'" 
            :class="{ active: viewMode === 'grid' }"
            class="view-btn"
          >
            🔲 Grade
          </button>
        </div>

        <div class="sort-controls">
          <select v-model="sortOrder" class="sort-select">
            <option value="desc">🔽 Mais Recente Primeiro</option>
            <option value="asc">🔼 Mais Antigo Primeiro</option>
          </select>
          
          <input 
            v-model="searchTerm" 
            type="text" 
            placeholder="🔍 Buscar capítulo..."
            class="search-input"
          />
        </div>
      </div>

      <!-- Lista de Capítulos -->
      <div class="chapters-section">
        <h2>📚 Capítulos ({{ filteredChapters.length }})</h2>
        
        <div :class="['chapters-container', viewMode]">
          <div 
            v-for="chapter in filteredChapters" 
            :key="chapter.id"
            class="chapter-item"
            @click="openChapter(chapter)"
            :class="{
              'read': chapter.isRead,
              'current': chapter.id === currentChapterId,
              'downloading': chapter.isDownloading
            }"
          >
            <!-- Thumbnail do Capítulo -->
            <div class="chapter-thumbnail">
              <img 
                v-if="chapter.thumbnail" 
                :src="chapter.thumbnail" 
                :alt="chapter.name"
              />
              <div v-else class="chapter-placeholder">📖</div>
              
              <!-- Indicadores -->
              <div class="chapter-indicators">
                <span v-if="chapter.isRead" class="read-indicator">✅</span>
                <span v-if="chapter.isDownloading" class="download-indicator">⬇️</span>
                <span v-if="chapter.id === currentChapterId" class="current-indicator">👁️</span>
              </div>
            </div>

            <!-- Info do Capítulo -->
            <div class="chapter-info">
              <h3>{{ chapter.name }}</h3>
              <div class="chapter-meta">
                <span v-if="chapter.number" class="chapter-number">
                  Cap. {{ chapter.number }}
                </span>
                <span v-if="chapter.volume" class="volume-number">
                  Vol. {{ chapter.volume }}
                </span>
                <span class="page-count">{{ chapter.page_count }} páginas</span>
                <span v-if="chapter.date_added" class="date-added">
                  {{ formatDate(chapter.date_added) }}
                </span>
              </div>
              
              <!-- Progresso de Leitura -->
              <div v-if="chapter.readProgress" class="reading-progress">
                <div class="progress-bar">
                  <div 
                    class="progress-fill" 
                    :style="{ width: chapter.readProgress + '%' }"
                  ></div>
                </div>
                <span class="progress-text">{{ chapter.readProgress }}%</span>
              </div>
            </div>

            <!-- Ações do Capítulo -->
            <div class="chapter-actions">
              <button @click.stop="downloadChapter(chapter)" class="action-btn">
                📥
              </button>
              <button @click.stop="toggleChapterRead(chapter)" class="action-btn">
                {{ chapter.isRead ? '👁️' : '👁️‍🗨️' }}
              </button>
              <button @click.stop="showChapterMenu(chapter)" class="action-btn">
                ⋮
              </button>
            </div>
          </div>
        </div>

        <!-- Load More -->
        <div v-if="hasMoreChapters" class="load-more">
          <button @click="loadMoreChapters" class="load-more-btn">
            📚 Carregar Mais Capítulos
          </button>
        </div>
      </div>
    </div>

    <!-- Floating Action Button -->
    <div class="floating-actions">
      <button @click="scrollToTop" class="fab secondary">⬆️</button>
      <button @click="continueReading" class="fab primary">📖</button>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useLibraryStore } from '@/store/library'

export default {
  name: 'MangaDetailView',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const libraryStore = useLibraryStore()

    // Reactive data
    const manga = ref(null)
    const loading = ref(true)
    const error = ref(null)
    const viewMode = ref('list') // 'list' ou 'grid'
    const sortOrder = ref('desc') // 'asc' ou 'desc'
    const searchTerm = ref('')
    const currentChapterId = ref(null)
    const chapterLimit = ref(50)

    // Computed
    const mangaId = computed(() => route.params.id)
    
    const statusClass = computed(() => {
      if (!manga.value?.status) return ''
      return {
        'status-ongoing': manga.value.status.toLowerCase().includes('ongoing'),
        'status-completed': manga.value.status.toLowerCase().includes('completed'),
        'status-hiatus': manga.value.status.toLowerCase().includes('hiatus')
      }
    })

    const readProgress = computed(() => {
      if (!manga.value?.chapters) return 0
      const readChapters = manga.value.chapters.filter(ch => ch.isRead).length
      return Math.round((readChapters / manga.value.chapters.length) * 100)
    })

    const filteredChapters = computed(() => {
      if (!manga.value?.chapters) return []
      
      let chapters = [...manga.value.chapters]
      
      // Filtrar por busca
      if (searchTerm.value) {
        const term = searchTerm.value.toLowerCase()
        chapters = chapters.filter(ch => 
          ch.name.toLowerCase().includes(term) ||
          ch.number?.toString().includes(term)
        )
      }
      
      // Ordenar
      chapters.sort((a, b) => {
        const aNum = a.number || 0
        const bNum = b.number || 0
        return sortOrder.value === 'desc' ? bNum - aNum : aNum - bNum
      })
      
      // Limitar quantidade (paginação)
      return chapters.slice(0, chapterLimit.value)
    })

    const hasMoreChapters = computed(() => {
      return manga.value?.chapters?.length > chapterLimit.value
    })

    // Methods
    const loadManga = async () => {
      loading.value = true
      error.value = null
      
      try {
        console.log('📖 Carregando mangá:', mangaId.value)
        const mangaData = await libraryStore.fetchManga(mangaId.value)

        manga.value = {
          ...mangaData,
          // Adicionar propriedades de UI
          isFavorite: false, // TODO: Implementar sistema de favoritos
          chapters: mangaData.chapters?.map(chapter => ({
            ...chapter,
            isRead: false, // TODO: Carregar do progresso real
            readProgress: 0, // TODO: Carregar progresso real
            isDownloading: false,
            thumbnail: chapter.pages?.[0]?.path 
              ? `http://localhost:8000${chapter.pages[0].path}` 
              : null
          })) || []
        }
        
        console.log('📚 Capítulos carregados:')
        manga.value.chapters.forEach(ch => {
          console.log(`  - ID: "${ch.id}" | Nome: "${ch.name}"`)
        })

        // Carregar progresso de leitura atual
        loadReadingProgress()
        
      } catch (err) {
        error.value = err.message || 'Erro ao carregar mangá'
        console.error('Erro ao carregar mangá:', err)
      } finally {
        loading.value = false
      }
    }

    const loadReadingProgress = () => {
      // TODO: Implementar carregamento do progresso real
      const savedProgress = localStorage.getItem(`ohara_progress_${mangaId.value}`)
      if (savedProgress) {
        const progress = JSON.parse(savedProgress)
        currentChapterId.value = progress.currentChapterId
        
        // Atualizar progresso dos capítulos
        if (manga.value?.chapters) {
          manga.value.chapters.forEach(chapter => {
            const chapterProgress = progress.chapters?.[chapter.id]
            if (chapterProgress) {
              chapter.isRead = chapterProgress.isRead
              chapter.readProgress = chapterProgress.progress
            }
          })
        }
      }
    }

    const continueReading = () => {
      if (!manga.value?.chapters?.length) return
      
      // Encontrar próximo capítulo não lido
      let nextChapter = manga.value.chapters.find(ch => !ch.isRead)
      
      // Se todos foram lidos, usar o último
      if (!nextChapter) {
        nextChapter = manga.value.chapters[0] // Primeiro da lista (mais recente)
      }
      
      openChapter(nextChapter)
    }

    const openChapter = (chapter) => {
      console.log('📖 Abrindo capítulo:', chapter.name)
      console.log('🔗 ID do capítulo:', chapter.id)
      const chapterId = chapter.id // Usar o ID que vem do backend

      // Salvar como capítulo atual
      currentChapterId.value = chapter.id
      saveReadingProgress()
      
      // Navegar para o leitor
      router.push({
        name: 'MangaReader',
        params: {
          mangaId: mangaId.value,
          chapterId: chapter.id
        }
      })
    }

    const markAsRead = () => {
      if (!manga.value?.chapters) return
      
      const allRead = manga.value.chapters.every(ch => ch.isRead)
      
      // Toggle: se todos lidos, marcar como não lidos; senão marcar todos como lidos
      manga.value.chapters.forEach(chapter => {
        chapter.isRead = !allRead
        chapter.readProgress = allRead ? 0 : 100
      })
      
      saveReadingProgress()
    }

    const addToFavorites = () => {
      if (!manga.value) return
      
      manga.value.isFavorite = !manga.value.isFavorite
      
      // TODO: Implementar sistema de favoritos no backend
      const favorites = JSON.parse(localStorage.getItem('ohara_favorites') || '[]')
      
      if (manga.value.isFavorite) {
        if (!favorites.includes(mangaId.value)) {
          favorites.push(mangaId.value)
        }
      } else {
        const index = favorites.indexOf(mangaId.value)
        if (index > -1) {
          favorites.splice(index, 1)
        }
      }
      
      localStorage.setItem('ohara_favorites', JSON.stringify(favorites))
    }

    const downloadChapter = async (chapter) => {
      chapter.isDownloading = true
      
      try {
        // TODO: Implementar download offline
        await new Promise(resolve => setTimeout(resolve, 2000)) // Simular download
        console.log('📥 Capítulo baixado:', chapter.name)
      } catch (error) {
        console.error('Erro ao baixar capítulo:', error)
      } finally {
        chapter.isDownloading = false
      }
    }

    const toggleChapterRead = (chapter) => {
      chapter.isRead = !chapter.isRead
      chapter.readProgress = chapter.isRead ? 100 : 0
      saveReadingProgress()
    }

    const showChapterMenu = (chapter) => {
      // TODO: Implementar menu de contexto
      const actions = [
        'Marcar como lido',
        'Baixar offline',
        'Compartilhar',
        'Copiar link'
      ]
      
      console.log('Menu do capítulo:', chapter.name, actions)
    }

    const loadMoreChapters = () => {
      chapterLimit.value += 50
    }

    const saveReadingProgress = () => {
      if (!manga.value) return
      
      const progress = {
        currentChapterId: currentChapterId.value,
        lastReadAt: new Date().toISOString(),
        chapters: {}
      }
      
      manga.value.chapters.forEach(chapter => {
        if (chapter.isRead || chapter.readProgress > 0) {
          progress.chapters[chapter.id] = {
            isRead: chapter.isRead,
            progress: chapter.readProgress
          }
        }
      })
      
      localStorage.setItem(`ohara_progress_${mangaId.value}`, JSON.stringify(progress))
    }

    const scrollToTop = () => {
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }

    const formatDate = (dateString) => {
      try {
        const date = new Date(dateString)
        return date.toLocaleDateString('pt-BR', {
          day: '2-digit',
          month: '2-digit',
          year: 'numeric'
        })
      } catch {
        return ''
      }
    }

    // Lifecycle
    onMounted(() => {
      loadManga()
    })

    // Watch route changes
    watch(() => route.params.id, () => {
      if (route.params.id) {
        loadManga()
      }
    })

    return {
      manga,
      loading,
      error,
      viewMode,
      sortOrder,
      searchTerm,
      currentChapterId,
      statusClass,
      readProgress,
      filteredChapters,
      hasMoreChapters,
      loadManga,
      continueReading,
      openChapter,
      markAsRead,
      addToFavorites,
      downloadChapter,
      toggleChapterRead,
      showChapterMenu,
      loadMoreChapters,
      scrollToTop,
      formatDate
    }
  }
}
</script>

<style scoped>
.manga-detail {
  min-height: 100vh;
  background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
  color: white;
}

/* Loading & Error States */
.loading-state, .error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 50vh;
  text-align: center;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255,255,255,0.3);
  border-radius: 50%;
  border-top: 4px solid #4ecdc4;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.retry-btn {
  background: #4ecdc4;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  margin-top: 1rem;
}

/* Manga Header */
.manga-header {
  display: flex;
  gap: 2rem;
  padding: 2rem;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
}

.manga-cover {
  flex-shrink: 0;
  width: 300px;
}

.cover-image {
  width: 100%;
  height: 400px;
  object-fit: cover;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
}

.cover-placeholder {
  width: 100%;
  height: 400px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 6rem;
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 1rem;
}

.quick-actions button {
  padding: 0.75rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
  transition: transform 0.2s;
}

.continue-btn {
  background: linear-gradient(45deg, #4ecdc4, #44a08d);
  color: white;
}

.mark-read-btn {
  background: #f39c12;
  color: white;
}

.favorite-btn {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.quick-actions button:hover {
  transform: scale(1.05);
}

.manga-info {
  flex: 1;
}

.manga-info h1 {
  font-size: 2.5rem;
  margin-bottom: 1rem;
  background: #fff;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.metadata {
  margin-bottom: 2rem;
}

.meta-item {
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.genres {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.genre-tag {
  background: rgba(78, 205, 196, 0.2);
  color: #4ecdc4;
  padding: 0.25rem 0.75rem;
  border-radius: 15px;
  font-size: 0.8rem;
  border: 1px solid rgba(78, 205, 196, 0.3);
}

.status-ongoing { color: #4CAF50; }
.status-completed { color: #2196F3; }
.status-hiatus { color: #FF9800; }

.stats {
  display: flex;
  gap: 2rem;
  margin-bottom: 2rem;
}

.stat-item {
  text-align: center;
}

.stat-number {
  font-size: 2rem;
  font-weight: bold;
  color: #4ecdc4;
}

.stat-label {
  font-size: 0.9rem;
  opacity: 0.8;
}

.description {
  margin-top: 1rem;
}

.description h3 {
  color: #4ecdc4;
  margin-bottom: 0.5rem;
}

/* Chapter Controls */
.chapter-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background: rgba(255, 255, 255, 0.05);
  gap: 1rem;
  flex-wrap: wrap;
}

.view-controls, .sort-controls {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.view-btn {
  padding: 0.5rem 1rem;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 5px;
  background: transparent;
  color: white;
  cursor: pointer;
}

.view-btn.active {
  background: rgba(78, 205, 196, 0.2);
  border-color: #4ecdc4;
}

.sort-select, .search-input {
  padding: 0.5rem;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 5px;
  background: rgba(0, 0, 0, 0.3);
  color: white;
}

.search-input {
  min-width: 200px;
}

/* Chapters Section */
.chapters-section {
  padding: 2rem;
}

.chapters-section h2 {
  color: #4ecdc4;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.chapters-container.list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.chapters-container.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

.chapter-item {
  display: flex;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid transparent;
}

.chapter-item:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-2px);
}

.chapter-item.read {
  opacity: 0.7;
  border-color: rgba(76, 175, 80, 0.5);
}

.chapter-item.current {
  border-color: #4ecdc4;
  box-shadow: 0 0 10px rgba(78, 205, 196, 0.3);
}

.chapter-thumbnail {
  width: 60px;
  height: 80px;
  flex-shrink: 0;
  position: relative;
  margin-right: 1rem;
}

.chapter-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 5px;
}

.chapter-placeholder {
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.chapter-indicators {
  position: absolute;
  top: -5px;
  right: -5px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.chapter-indicators span {
  background: rgba(0, 0, 0, 0.8);
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
}

.chapter-info {
  flex: 1;
}

.chapter-info h3 {
  margin-bottom: 0.5rem;
  color: white;
}

.chapter-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.8rem;
  opacity: 0.8;
  flex-wrap: wrap;
}

.chapter-meta span {
  background: rgba(255, 255, 255, 0.1);
  padding: 0.2rem 0.5rem;
  border-radius: 3px;
}

.reading-progress {
  margin-top: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.progress-bar {
  flex: 1;
  height: 4px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #4ecdc4;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.7rem;
  min-width: 35px;
}

.chapter-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.action-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 5px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.action-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

/* Load More */
.load-more {
  text-align: center;
  margin-top: 2rem;
}

.load-more-btn {
  background: rgba(78, 205, 196, 0.2);
  border: 1px solid #4ecdc4;
  color: #4ecdc4;
  padding: 1rem 2rem;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s;
}

.load-more-btn:hover {
  background: rgba(78, 205, 196, 0.3);
}

/* Floating Actions */
.floating-actions {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.fab {
  width: 56px;
  height: 56px;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  transition: transform 0.2s;
}

.fab:hover {
  transform: scale(1.1);
}

.fab.primary {
  background: linear-gradient(45deg, #4ecdc4, #44a08d);
  color: white;
}

.fab.secondary {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

/* Responsive */
@media (max-width: 768px) {
  .manga-header {
    flex-direction: column;
    text-align: center;
  }
  
  .manga-cover {
    width: 200px;
    margin: 0 auto;
  }
  
  .cover-image, .cover-placeholder {
    height: 280px;
  }
  
  .quick-actions {
    flex-direction: row;
    justify-content: center;
  }
  
  .chapter-controls {
    flex-direction: column;
    gap: 1rem;
  }
  
  .chapters-container.grid {
    grid-template-columns: 1fr;
  }
  
  .chapter-item {
    flex-direction: column;
    text-align: center;
  }
  
  .chapter-thumbnail {
    width: 80px;
    height: 100px;
    margin: 0 auto 1rem;
  }
  
  .floating-actions {
    bottom: 1rem;
    right: 1rem;
  }
}
</style>