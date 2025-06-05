<template>
  <div class="manga-reader" :class="{ 
    'fullscreen': readerStore.isFullscreen, 
    'controls-hidden': readerStore.hideControls,
    [`theme-${readerStore.theme}`]: true
  }">
    <!-- Loading State -->
    <div v-if="loading || readerStore.loading" class="reader-loading">
      <div class="spinner"></div>
      <p>Carregando capítulo...</p>
    </div>

    <!-- Error State -->
    <div v-if="error || readerStore.error" class="reader-error">
      <h2>❌ Erro ao Carregar Capítulo</h2>
      <p>{{ error || readerStore.error }}</p>
      <button @click="loadChapter" class="retry-btn">🔄 Tentar Novamente</button>
    </div>

    <!-- Reader Content -->
    <div v-if="!loading && !readerStore.loading && !error && !readerStore.error && readerStore.currentChapter" class="reader-content">
      <!-- Header Controls -->
      <div class="reader-header" :class="{ 'hidden': readerStore.hideControls }">
        <div class="header-left">
          <button @click="goBack" class="control-btn">← Voltar</button>
          <div class="chapter-info">
            <h3>{{ readerStore.currentManga?.title || 'Hunter x Hunter' }}</h3>
            <p>{{ readerStore.currentChapter?.chapter?.name || 'Capítulo 410' }}</p>
          </div>
        </div>
        <div class="header-right">
          <div class="page-counter">
            {{ readerStore.currentPage + 1 }} / {{ readerStore.totalPages }}
          </div>
          <button @click="toggleFullscreen" class="control-btn">
            {{ readerStore.isFullscreen ? '🗖' : '🗗' }}
          </button>
          <button @click="toggleSettings" class="control-btn">⚙️</button>
        </div>
      </div>

      <!-- Page Viewer -->
      <div class="page-viewer" :class="`mode-${readerStore.readingMode}`" @click="toggleControls">
        <!-- Modo Página Única -->
        <div v-if="readerStore.readingMode === 'single'" class="single-page-container">
          <img 
            :src="getPageImageUrl(readerStore.currentPage)"
            :alt="`Página ${readerStore.currentPage + 1}`"
            class="manga-page"
            :class="`fit-${readerStore.fitMode}`"
            @error="handleImageError"
            @load="handleImageLoad"
          />
        </div>

        <!-- Modo Página Dupla -->
        <div v-else-if="readerStore.readingMode === 'double'" class="double-page-container">
          <div class="double-pages" :class="`direction-${readerStore.readingDirection}`">
            <template v-if="readerStore.readingDirection === 'rtl'">
              <img 
                v-if="currentDoublePage + 1 < readerStore.totalPages"
                :src="getPageImageUrl(currentDoublePage + 1)"
                :alt="`Página ${currentDoublePage + 2}`"
                class="manga-page right-page"
                :class="`fit-${readerStore.fitMode}`"
                @error="handleImageError"
              />
              <img 
                :src="getPageImageUrl(currentDoublePage)"
                :alt="`Página ${currentDoublePage + 1}`"
                class="manga-page left-page"
                :class="`fit-${readerStore.fitMode}`"
                @error="handleImageError"
              />
            </template>
            <template v-else>
              <img 
                :src="getPageImageUrl(currentDoublePage)"
                :alt="`Página ${currentDoublePage + 1}`"
                class="manga-page left-page"
                :class="`fit-${readerStore.fitMode}`"
                @error="handleImageError"
              />
              <img 
                v-if="currentDoublePage + 1 < readerStore.totalPages"
                :src="getPageImageUrl(currentDoublePage + 1)"
                :alt="`Página ${currentDoublePage + 2}`"
                class="manga-page right-page"
                :class="`fit-${readerStore.fitMode}`"
                @error="handleImageError"
              />
            </template>
          </div>
        </div>

        <!-- Modo Vertical -->
        <div v-else-if="readerStore.readingMode === 'vertical'" class="vertical-container">
          <div class="vertical-pages">
            <div 
              v-for="pageIndex in readerStore.totalPages" 
              :key="pageIndex"
              class="vertical-page-wrapper"
            >
              <img 
                :src="getPageImageUrl(pageIndex - 1)"
                :alt="`Página ${pageIndex}`"
                class="manga-page vertical-page"
                :class="`fit-${readerStore.fitMode}`"
                @error="handleImageError"
                loading="lazy"
              />
            </div>
          </div>
        </div>

        <!-- Modo Webtoon -->
        <div v-else-if="readerStore.readingMode === 'webtoon'" class="webtoon-container">
          <div class="webtoon-pages">
            <div 
              v-for="pageIndex in readerStore.totalPages" 
              :key="pageIndex"
              class="webtoon-page-wrapper"
            >
              <img 
                :src="getPageImageUrl(pageIndex - 1)"
                :alt="`Página ${pageIndex}`"
                class="manga-page webtoon-page"
                :class="`fit-${readerStore.fitMode}`"
                @error="handleImageError"
                loading="lazy"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Footer Controls -->
      <div class="reader-footer" :class="{ 'hidden': readerStore.hideControls }">
        <div class="progress-bar">
          <div class="progress-track" @click="seekToPosition">
            <div class="progress-fill" :style="{ width: progressPercentage + '%' }"></div>
            <div class="progress-thumb" :style="{ left: progressPercentage + '%' }"></div>
          </div>
        </div>

        <div class="footer-controls">
          <button @click="previousChapter" :disabled="!hasPreviousChapter" class="control-btn">
            ⏮️ Cap. Anterior
          </button>
          <button @click="previousPage" :disabled="!canGoPrevious" class="control-btn">
            ⏪ Anterior
          </button>
          <select v-model="readerStore.readingMode" class="mode-select">
            <option value="single">📄 Página Única</option>
            <option value="double">📖 Página Dupla</option>
            <option value="vertical">📜 Vertical</option>
            <option value="webtoon">📱 Webtoon</option>
          </select>
          <button @click="nextPage" :disabled="!canGoNext" class="control-btn">
            Próxima ⏩
          </button>
          <button @click="nextChapter" :disabled="!hasNextChapter" class="control-btn">
            Próx. Cap. ⏭️
          </button>
        </div>
      </div>

      <!-- Settings Panel -->
      <div v-if="readerStore.showSettings" class="settings-panel" @click.stop>
        <div class="settings-content">
          <div class="settings-header">
            <h3>⚙️ Configurações de Leitura</h3>
            <button @click="closeSettings" class="close-btn">✕</button>
          </div>
          
          <div class="setting-group">
            <label class="setting-label">📏 Ajuste de Imagem:</label>
            <select v-model="readerStore.fitMode" class="setting-select">
              <option value="width">Ajustar Largura</option>
              <option value="height">Ajustar Altura</option>
              <option value="screen">Ajustar Tela</option>
              <option value="original">Tamanho Original</option>
            </select>
          </div>

          <div class="setting-group">
            <label class="setting-label">📖 Direção de Leitura:</label>
            <select v-model="readerStore.readingDirection" class="setting-select">
              <option value="ltr">Esquerda → Direita</option>
              <option value="rtl">Direita → Esquerda</option>
            </select>
          </div>

          <div class="setting-group">
            <label class="setting-label">🌙 Tema:</label>
            <select v-model="readerStore.theme" class="setting-select">
              <option value="dark">Escuro</option>
              <option value="light">Claro</option>
              <option value="sepia">Sépia</option>
            </select>
          </div>

          <div class="setting-actions">
            <button @click="resetSettings" class="secondary-btn">🔄 Redefinir</button>
            <button @click="applySettings" class="primary-btn">✅ Aplicar</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Debug Info -->
    <div v-if="showDebug" class="debug-info">
      <h4>🐛 Debug Info:</h4>
      <p>Current Page: {{ readerStore.currentPage }}</p>
      <p>Total Pages: {{ readerStore.totalPages }}</p>
      <p>Chapter: {{ readerStore.currentChapter?.chapter?.id }}</p>
      <p>Manga: {{ readerStore.currentManga?.id }}</p>
      <button @click="showDebug = false" class="debug-close">❌ Fechar</button>
    </div>

    <!-- Floating Actions -->
    <div class="floating-actions" v-if="!readerStore.hideControls">
      <button @click="toggleAutoScroll" class="fab auto-scroll" :class="{ active: readerStore.autoScrollActive }">
        {{ readerStore.autoScrollActive ? '⏸️' : '▶️' }}
      </button>
      <button @click="showDebug = !showDebug" class="fab debug-btn">🐛</button>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useReaderStore } from '@/store/reader'

const API_BASE_URL = 'http://localhost:8000'

export default {
  name: 'MangaReaderView',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const readerStore = useReaderStore()

    // Reactive data
    const loading = ref(false)
    const error = ref(null)
    const showDebug = ref(false)
    
    // Auto-hide controls
    let controlsTimeout = null

    // Computed properties
    const mangaId = computed(() => route.params.mangaId)
    const chapterId = computed(() => route.params.chapterId)
    
    const progressPercentage = computed(() => {
      return readerStore.progressPercentage || 0
    })

    const currentDoublePage = computed(() => {
      return Math.floor(readerStore.currentPage / 2) * 2
    })

    const canGoPrevious = computed(() => {
      return readerStore.currentPage > 0
    })

    const canGoNext = computed(() => {
      return readerStore.currentPage < readerStore.totalPages - 1
    })

    const hasPreviousChapter = computed(() => {
      return readerStore.hasPreviousChapter
    })

    const hasNextChapter = computed(() => {
      return readerStore.hasNextChapter
    })

    // Methods
    const getPageImageUrl = (pageIndex) => {
      console.log('🖼️ Gerando URL para página:', pageIndex)
      
      // Verificar se temos dados do capítulo
      if (!readerStore.currentChapter?.chapter?.pages) {
        console.warn('⚠️ Sem dados de páginas disponíveis')
        return `https://via.placeholder.com/800x1200/333/fff?text=Sem+Dados+Disponíveis`
      }

      // Verificar se a página existe
      const page = readerStore.currentChapter.chapter.pages[pageIndex]
      if (!page) {
        console.warn(`⚠️ Página ${pageIndex} não encontrada`)
        return `https://via.placeholder.com/800x1200/ff6b6b/fff?text=Página+${pageIndex + 1}+Não+Encontrada`
      }

      // Construir URL da API
      let imageUrl = ''
      
      if (page.url) {
        // Se a página já tem URL completa
        imageUrl = page.url
      } else if (page.path) {
        // Se tem caminho relativo
        imageUrl = page.path.startsWith('http') ? page.path : `${API_BASE_URL}${page.path}`
      } else {
        // Construir URL baseada nos parâmetros da rota
        imageUrl = `${API_BASE_URL}/api/manga/${mangaId.value}/chapter/${chapterId.value}/page/${pageIndex}`
      }

      console.log(`✅ URL gerada para página ${pageIndex}:`, imageUrl)
      return imageUrl
    }

    const handleImageError = (event) => {
      console.error('❌ Erro ao carregar imagem:', event.target.src)
      event.target.src = `https://via.placeholder.com/800x1200/ff6b6b/fff?text=Erro+ao+Carregar+Página`
    }

    const handleImageLoad = (event) => {
      console.log('✅ Imagem carregada com sucesso:', event.target.src)
    }

    const loadChapter = async () => {
      if (!mangaId.value || !chapterId.value) {
        error.value = 'Parâmetros de rota inválidos'
        return
      }

      loading.value = true
      error.value = null
      
      try {
        console.log(`📖 Carregando capítulo: ${mangaId.value}/${chapterId.value}`)
        await readerStore.loadChapter(mangaId.value, chapterId.value)
        console.log('✅ Capítulo carregado com sucesso')
        resetControlsTimer()
      } catch (err) {
        error.value = `Erro ao carregar capítulo: ${err.message}`
        console.error('❌ Erro detalhado:', err)
      } finally {
        loading.value = false
      }
    }

    const nextPage = () => {
      if (readerStore.readingMode === 'vertical' || readerStore.readingMode === 'webtoon') {
        const container = document.querySelector('.vertical-container, .webtoon-container')
        if (container) {
          container.scrollBy({ top: window.innerHeight * 0.8, behavior: 'smooth' })
        }
        return
      }
      
      const success = readerStore.nextPage()
      if (!success && hasNextChapter.value) {
        nextChapter()
      }
      resetControlsTimer()
    }

    const previousPage = () => {
      if (readerStore.readingMode === 'vertical' || readerStore.readingMode === 'webtoon') {
        const container = document.querySelector('.vertical-container, .webtoon-container')
        if (container) {
          container.scrollBy({ top: -window.innerHeight * 0.8, behavior: 'smooth' })
        }
        return
      }
      
      const success = readerStore.previousPage()
      if (!success && hasPreviousChapter.value) {
        previousChapter()
      }
      resetControlsTimer()
    }

    const nextChapter = () => {
      if (readerStore.navigation.nextChapter) {
        const nextChapterId = readerStore.navigation.nextChapter.id
        router.push(`/manga/${mangaId.value}/chapter/${nextChapterId}`)
      }
    }

    const previousChapter = () => {
      if (readerStore.navigation.previousChapter) {
        const prevChapterId = readerStore.navigation.previousChapter.id
        router.push(`/manga/${mangaId.value}/chapter/${prevChapterId}`)
      }
    }

    const toggleControls = () => {
      readerStore.toggleControls()
      resetControlsTimer()
    }

    const toggleSettings = () => {
      readerStore.toggleSettings()
    }

    const closeSettings = () => {
      readerStore.showSettings = false
    }

    const resetControlsTimer = () => {
      if (controlsTimeout) {
        clearTimeout(controlsTimeout)
      }
      
      if (!readerStore.hideControls) {
        controlsTimeout = setTimeout(() => {
          readerStore.hideControls = true
        }, 3000)
      }
    }

    const toggleFullscreen = async () => {
      try {
        if (!document.fullscreenElement) {
          await document.documentElement.requestFullscreen()
        } else {
          await document.exitFullscreen()
        }
        readerStore.toggleFullscreen()
      } catch (err) {
        console.error('Erro ao alternar fullscreen:', err)
      }
    }

    const toggleAutoScroll = () => {
      readerStore.toggleAutoScroll()
    }

    const seekToPosition = (event) => {
      const rect = event.target.getBoundingClientRect()
      const x = event.clientX - rect.left
      const percentage = (x / rect.width) * 100
      
      readerStore.seekToProgress(percentage)
      resetControlsTimer()
    }

    const goBack = () => {
      router.push(`/manga/${mangaId.value}`)
    }

    const resetSettings = () => {
      readerStore.resetSettings()
    }

    const applySettings = () => {
      readerStore.saveSettings()
      readerStore.showSettings = false
    }

    // Keyboard shortcuts
    const handleKeydown = (event) => {
      if (readerStore.showSettings) return
      
      switch (event.key) {
        case ' ':
        case 'ArrowRight':
          event.preventDefault()
          nextPage()
          break
        case 'Backspace':
        case 'ArrowLeft':
          event.preventDefault()
          previousPage()
          break
        case 'f':
        case 'F':
          event.preventDefault()
          toggleFullscreen()
          break
        case 'h':
        case 'H':
          event.preventDefault()
          toggleControls()
          break
        case 's':
        case 'S':
          event.preventDefault()
          toggleSettings()
          break
        case 'Escape':
          event.preventDefault()
          if (readerStore.showSettings) {
            closeSettings()
          }
          break
      }
    }

    // Lifecycle
    onMounted(() => {
      console.log('🚀 MangaReaderView montado')
      console.log('📊 Parâmetros da rota:', { mangaId: mangaId.value, chapterId: chapterId.value })
      
      readerStore.loadSettings()
      loadChapter()
      
      document.addEventListener('keydown', handleKeydown)
      document.addEventListener('fullscreenchange', () => {
        readerStore.isFullscreen = !!document.fullscreenElement
      })

      setTimeout(() => {
        console.log('🔍 Estado do store após carregamento:', {
          currentChapter: readerStore.currentChapter,
          totalPages: readerStore.totalPages,
          currentPage: readerStore.currentPage
        })
      }, 2000)
    })

    onUnmounted(() => {
      document.removeEventListener('keydown', handleKeydown)
      if (controlsTimeout) {
        clearTimeout(controlsTimeout)
      }
    })

    // Watch route changes
    watch(() => route.params, (newParams, oldParams) => {
      console.log('🔄 Rota alterada:', { old: oldParams, new: newParams })
      if (newParams.chapterId !== oldParams?.chapterId) {
        loadChapter()
      }
    })

    return {
      readerStore,
      loading,
      error,
      showDebug,
      progressPercentage,
      currentDoublePage,
      canGoPrevious,
      canGoNext,
      hasPreviousChapter,
      hasNextChapter,
      getPageImageUrl,
      handleImageError,
      handleImageLoad,
      loadChapter,
      nextPage,
      previousPage,
      nextChapter,
      previousChapter,
      toggleControls,
      toggleSettings,
      closeSettings,
      toggleFullscreen,
      toggleAutoScroll,
      seekToPosition,
      goBack,
      resetSettings,
      applySettings
    }
  }
}
</script>

<style scoped>
/* Base Styles */
.manga-reader {
  position: relative;
  min-height: 100vh;
  background: #000;
  color: white;
  overflow: hidden;
  user-select: none;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.manga-reader.fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 9999;
}

/* Theme Variations */
.manga-reader.theme-light {
  background: #fff;
  color: #000;
}

.manga-reader.theme-sepia {
  background: #f4e5d3;
  color: #5d4037;
}

/* Loading & Error States */
.reader-loading, .reader-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
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
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #ff6b6b;
  color: white;
}

.setting-group {
  margin-bottom: 1.5rem;
}

.setting-label {
  display: block;
  margin-bottom: 0.75rem;
  font-weight: 600;
  color: #4ecdc4;
  font-size: 1rem;
}

.setting-select {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #4ecdc4;
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s;
}

.setting-select:focus {
  outline: none;
  border-color: #44a08d;
  box-shadow: 0 0 0 3px rgba(78, 205, 196, 0.2);
}

.setting-select option {
  background: #1e1e2e;
  color: white;
  padding: 0.5rem;
}

.setting-actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
}

.primary-btn, .secondary-btn {
  flex: 1;
  padding: 0.75rem;
  border: 2px solid;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 1rem;
  transition: all 0.2s;
}

.primary-btn {
  border-color: #4ecdc4;
  background: #4ecdc4;
  color: white;
}

.primary-btn:hover {
  background: #44a08d;
  border-color: #44a08d;
}

.secondary-btn {
  border-color: #ff6b6b;
  background: rgba(255, 107, 107, 0.2);
  color: #ff6b6b;
}

.secondary-btn:hover {
  background: #ff6b6b;
  color: white;
}

/* Debug Info */
.debug-info {
  position: fixed;
  top: 100px;
  left: 20px;
  background: rgba(0, 0, 0, 0.9);
  color: #4ecdc4;
  padding: 1rem;
  border-radius: 8px;
  border: 2px solid #4ecdc4;
  z-index: 300;
  font-family: monospace;
  font-size: 0.9rem;
}

.debug-info h4 {
  margin: 0 0 0.5rem 0;
  color: #ff6b6b;
}

.debug-info p {
  margin: 0.25rem 0;
}

.debug-close {
  background: #ff6b6b;
  border: none;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
  margin-top: 0.5rem;
}

/* Floating Actions */
.floating-actions {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  z-index: 150;
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
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
  transition: all 0.3s;
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.fab:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.7);
}

.fab.auto-scroll.active {
  background: #4ecdc4;
  box-shadow: 0 4px 12px rgba(78, 205, 196, 0.5);
}

.debug-btn {
  background: rgba(255, 107, 107, 0.7) !important;
}

/* Scrollbar customization */
.vertical-container::-webkit-scrollbar,
.webtoon-container::-webkit-scrollbar {
  width: 8px;
}

.vertical-container::-webkit-scrollbar-track,
.webtoon-container::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
}

.vertical-container::-webkit-scrollbar-thumb,
.webtoon-container::-webkit-scrollbar-thumb {
  background: #4ecdc4;
  border-radius: 4px;
}

.vertical-container::-webkit-scrollbar-thumb:hover,
.webtoon-container::-webkit-scrollbar-thumb:hover {
  background: #44a08d;
}

/* Responsive */
@media (max-width: 768px) {
  .reader-header, .reader-footer {
    padding: 1rem;
  }
  
  .header-left, .header-right {
    gap: 0.5rem;
  }
  
  .footer-controls {
    gap: 0.5rem;
    font-size: 0.9rem;
  }
  
  .settings-panel {
    width: 100%;
  }
  
  .floating-actions {
    bottom: 1rem;
    right: 1rem;
  }
  
  .control-btn {
    padding: 0.4rem 0.8rem;
    font-size: 0.9rem;
  }
  
  .double-pages {
    gap: 5px;
  }
  
  .manga-page.fit-width {
    max-width: 95vw;
  }
}

@media (max-width: 480px) {
  .settings-content {
    padding: 1rem;
  }
  
  .footer-controls {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .chapter-info h3 {
    margin: 0;
    font-size: 1rem;
    font-weight: 600;
  }
  
  .debug-info {
    left: 10px;
    right: 10px;
    width: auto;
  }
}

/* Animations */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.reader-content {
  animation: fadeIn 0.3s ease-in;
}

.settings-panel {
  animation: slideUp 0.3s ease-out;
}

/* Hover effects */
.control-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(78, 205, 196, 0.3);
}

.setting-select:hover {
  border-color: #44a08d;
}

.mode-select:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* Loading animation */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.reader-loading p {
  animation: pulse 2s infinite;
}
.retry-btn {
  background: #4ecdc4;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  margin-top: 1rem;
  font-weight: 500;
  transition: background 0.2s;
}

.retry-btn:hover {
  background: #44a08d;
}

/* Header Controls */
.reader-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background: linear-gradient(to bottom, rgba(0,0,0,0.9), transparent);
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 100;
  transition: transform 0.3s ease;
}

.reader-header.hidden {
  transform: translateY(-100%);
}

.header-left, .header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.chapter-info h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.chapter-info p {
  margin: 0;
  opacity: 0.8;
  font-size: 0.9rem;
}

.page-counter {
  background: rgba(255, 255, 255, 0.2);
  padding: 0.25rem 0.75rem;
  border-radius: 15px;
  font-size: 0.9rem;
  font-weight: 500;
}

.control-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}

.control-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-1px);
}

.control-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* Page Viewer */
.page-viewer {
  position: relative;
  width: 100%;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
}

/* Single Page Mode */
.single-page-container {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
}

/* Double Page Mode */
.double-page-container {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
}

.double-pages {
  display: flex;
  gap: 10px;
  align-items: center;
  max-height: 100vh;
}

.double-pages.direction-rtl {
  flex-direction: row-reverse;
}

/* Vertical Mode */
.vertical-container, .webtoon-container {
  width: 100%;
  height: 100vh;
  overflow-y: auto;
  overflow-x: hidden;
}

.vertical-pages, .webtoon-pages {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 0;
}

.vertical-page-wrapper {
  margin-bottom: 10px;
}

.webtoon-page-wrapper {
  margin-bottom: 20px;
}

/* Image Fitting */
.manga-page {
  max-width: 100%;
  max-height: 100vh;
  object-fit: contain;
  transition: all 0.3s ease;
}

.manga-page.fit-width {
  width: 100%;
  height: auto;
  max-height: 100vh;
}

.manga-page.fit-height {
  height: 100vh;
  width: auto;
  max-width: 100%;
}

.manga-page.fit-screen {
  max-width: 100%;
  max-height: 100vh;
  object-fit: contain;
}

.manga-page.fit-original {
  width: auto;
  height: auto;
  max-width: none;
  max-height: none;
}

/* Footer Controls */
.reader-footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(to top, rgba(0,0,0,0.9), transparent);
  padding: 1rem 2rem;
  z-index: 100;
  transition: transform 0.3s ease;
}

.reader-footer.hidden {
  transform: translateY(100%);
}

.progress-bar {
  margin-bottom: 1rem;
}

.progress-track {
  position: relative;
  height: 6px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 3px;
  cursor: pointer;
}

.progress-fill {
  height: 100%;
  background: #4ecdc4;
  border-radius: 3px;
  transition: width 0.3s ease;
}

.progress-thumb {
  position: absolute;
  top: -3px;
  width: 12px;
  height: 12px;
  background: #4ecdc4;
  border-radius: 50%;
  transform: translateX(-50%);
  cursor: grab;
}

.footer-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.mode-select {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  font-weight: 500;
}

.mode-select option {
  background: #1e1e2e;
  color: white;
}

/* Settings Panel */
.settings-panel {
  position: fixed;
  top: 0;
  right: 0;
  width: 380px;
  height: 100vh;
  background: rgba(30, 30, 46, 0.98);
  backdrop-filter: blur(15px);
  border-left: 2px solid #4ecdc4;
  z-index: 200;
  overflow-y: auto;
  box-shadow: -10px 0 30px rgba(0, 0, 0, 0.5);
}

.settings-content {
  padding: 2rem;
}

.settings-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #4ecdc4;
}

.settings-header h3 {
  color: #4ecdc4;
  margin: 0;
  font-size: 1.3rem;
  font-weight: 600;
}

.close-btn {
  background: rgba(255, 107, 107, 0.2);
  border: 2px solid #ff6b6b;
  color: #ff6b6b;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #ff6b6b;
  color: white;
}

.setting-group {
  margin-bottom: 1.5rem;
}

.setting-label {
  display: block;
  margin-bottom: 0.75rem;
  font-weight: 600;
  color: #4ecdc4;
  font-size: 1rem;
}

.setting-select {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #4ecdc4;
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s;
}

.setting-select:focus {
  outline: none;
  border-color: #44a08d;
  box-shadow: 0 0 0 3px rgba(78, 205, 196, 0.2);
}

.setting-select option {
  background: #1e1e2e;
  color: white;
  padding: 0.5rem;
}

.setting-actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
}

.primary-btn, .secondary-btn {
  flex: 1;
  padding: 0.75rem;
  border: 2px solid;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 1rem;
  transition: all 0.2s;
}

.primary-btn {
  border-color: #4ecdc4;
  background: #4ecdc4;
  color: white;
}

.primary-btn:hover {
  background: #44a08d;
  border-color: #44a08d;
}

.secondary-btn {
  border-color: #ff6b6b;
  background: rgba(255, 107, 107, 0.2);
  color: #ff6b6b;
}

.secondary-btn:hover {
  background: #ff6b6b;
  color: white;
}

/* Debug Info */
.debug-info {
  position: fixed;
  top: 100px;
  left: 20px;
  background: rgba(0, 0, 0, 0.9);
  color: #4ecdc4;
  padding: 1rem;
  border-radius: 8px;
  border: 2px solid #4ecdc4;
  z-index: 300;
  font-family: monospace;
  font-size: 0.9rem;
}

.debug-info h4 {
  margin: 0 0 0.5rem 0;
  color: #ff6b6b;
}

.debug-info p {
  margin: 0.25rem 0;
}

.debug-close {
  background: #ff6b6b;
  border: none;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
  margin-top: 0.5rem;
}

/* Floating Actions */
.floating-actions {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  z-index: 150;
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
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
  transition: all 0.3s;
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.fab:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.7);
}

.fab.auto-scroll.active {
  background: #4ecdc4;
  box-shadow: 0 4px 12px rgba(78, 205, 196, 0.5);
}

.debug-btn {
  background: rgba(255, 107, 107, 0.7) !important;
}

/* Scrollbar customization */
.vertical-container::-webkit-scrollbar,
.webtoon-container::-webkit-scrollbar {
  width: 8px;
}

.vertical-container::-webkit-scrollbar-track,
.webtoon-container::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
}

.vertical-container::-webkit-scrollbar-thumb,
.webtoon-container::-webkit-scrollbar-thumb {
  background: #4ecdc4;
  border-radius: 4px;
}

.vertical-container::-webkit-scrollbar-thumb:hover,
.webtoon-container::-webkit-scrollbar-thumb:hover {
  background: #44a08d;
}

/* Responsive */
@media (max-width: 768px) {
  .reader-header, .reader-footer {
    padding: 1rem;
  }
  
  .header-left, .header-right {
    gap: 0.5rem;
  }
  
  .footer-controls {
    gap: 0.5rem;
    font-size: 0.9rem;
  }
  
  .settings-panel {
    width: 100%;
  }
  
  .floating-actions {
    bottom: 1rem;
    right: 1rem;
  }
  
  .control-btn {
    padding: 0.4rem 0.8rem;
    font-size: 0.9rem;
  }
  
  .double-pages {
    gap: 5px;
  }
  
  .manga-page.fit-width {
    max-width: 95vw;
  }
}

@media (max-width: 480px) {
  .settings-content {
    padding: 1rem;
  }
  
  .footer-controls {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .chapter-info h3 {
    margin: 0;
    font-size: 1rem;
    font-weight: 600;
  }
  
  .debug-info {
    left: 10px;
    right: 10px;
    width: auto;
  }
}

/* Animations */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.reader-content {
  animation: fadeIn 0.3s ease-in;
}

.settings-panel {
  animation: slideUp 0.3s ease-out;
}

/* Hover effects */
.control-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(78, 205, 196, 0.3);
}

.setting-select:hover {
  border-color: #44a08d;
}

.mode-select:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* Loading animation */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.reader-loading p {
  animation: pulse 2s infinite;
}
</style>