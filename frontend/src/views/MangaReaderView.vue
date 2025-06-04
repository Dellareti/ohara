<template>
  <div class="manga-reader" :class="{ 'fullscreen': isFullscreen, 'controls-hidden': hideControls }">
    <!-- Loading State -->
    <div v-if="loading" class="reader-loading">
      <div class="spinner"></div>
      <p>Carregando capítulo...</p>
    </div>

    <!-- Error State -->
    <div v-if="error" class="reader-error">
      <h2>❌ Erro ao Carregar Capítulo</h2>
      <p>{{ error }}</p>
      <button @click="loadChapter" class="retry-btn">🔄 Tentar Novamente</button>
    </div>

    <!-- Reader Content -->
    <div v-if="chapter && !loading" class="reader-content">
      <!-- Header Controls (hideable) -->
      <div class="reader-header" :class="{ 'hidden': hideControls }">
        <div class="header-left">
          <button @click="goBack" class="control-btn">
            ← Voltar
          </button>
          <div class="chapter-info">
            <h3>{{ manga?.title }}</h3>
            <p>{{ chapter.name }}</p>
          </div>
        </div>

        <div class="header-right">
          <div class="page-counter">
            {{ currentPage + 1 }} / {{ totalPages }}
          </div>
          <button @click="toggleFullscreen" class="control-btn">
            {{ isFullscreen ? '🗖' : '🗗' }}
          </button>
          <button @click="showSettings = !showSettings" class="control-btn">
            ⚙️
          </button>
        </div>
      </div>

      <!-- Reading Area -->
      <div class="reading-area" ref="readingArea" @click="handlePageClick">
        <!-- Single Page Mode -->
        <div v-if="readingMode === 'single'" class="single-page-container">
          <img
            v-if="currentPageData"
            :src="currentPageData.path"
            :alt="`Página ${currentPage + 1}`"
            class="page-image"
            :style="pageStyle"
            @load="onImageLoad"
            @error="onImageError"
          />
          
          <!-- Page Navigation Zones -->
          <div class="nav-zones">
            <div class="nav-zone prev" @click.stop="previousPage"></div>
            <div class="nav-zone next" @click.stop="nextPage"></div>
          </div>
        </div>

        <!-- Double Page Mode -->
        <div v-if="readingMode === 'double'" class="double-page-container">
          <img
            v-if="currentPageData"
            :src="currentPageData.path"
            :alt="`Página ${currentPage + 1}`"
            class="page-image left"
            :style="pageStyle"
          />
          <img
            v-if="nextPageData && currentPage < totalPages - 1"
            :src="nextPageData.path"
            :alt="`Página ${currentPage + 2}`"
            class="page-image right"
            :style="pageStyle"
          />
        </div>

        <!-- Vertical Continuous Mode -->
        <div v-if="readingMode === 'vertical'" class="vertical-container">
          <img
            v-for="(page, index) in visiblePages"
            :key="page.path"
            :src="page.path"
            :alt="`Página ${index + 1}`"
            class="page-image vertical"
            :style="pageStyle"
            @load="onImageLoad"
            @error="onImageError"
          />
        </div>

        <!-- Webtoon Mode -->
        <div v-if="readingMode === 'webtoon'" class="webtoon-container">
          <div
            v-for="(page, index) in visiblePages"
            :key="page.path"
            class="webtoon-page"
          >
            <img
              :src="page.path"
              :alt="`Página ${index + 1}`"
              class="page-image webtoon"
              :style="pageStyle"
            />
          </div>
        </div>
      </div>

      <!-- Bottom Controls (hideable) -->
      <div class="reader-footer" :class="{ 'hidden': hideControls }">
        <div class="progress-bar">
          <div class="progress-track" @click="seekToPosition">
            <div 
              class="progress-fill" 
              :style="{ width: progressPercentage + '%' }"
            ></div>
            <div 
              class="progress-thumb" 
              :style="{ left: progressPercentage + '%' }"
            ></div>
          </div>
        </div>

        <div class="footer-controls">
          <button @click="previousChapter" :disabled="!hasPreviousChapter" class="control-btn">
            ⏮️ Cap. Anterior
          </button>
          
          <button @click="previousPage" :disabled="currentPage <= 0" class="control-btn">
            ⏪ Anterior
          </button>
          
          <select v-model="readingMode" class="mode-select">
            <option value="single">📄 Página Única</option>
            <option value="double">📖 Página Dupla</option>
            <option value="vertical">📜 Vertical</option>
            <option value="webtoon">📱 Webtoon</option>
          </select>
          
          <button @click="nextPage" :disabled="currentPage >= totalPages - 1" class="control-btn">
            Próxima ⏩
          </button>
          
          <button @click="nextChapter" :disabled="!hasNextChapter" class="control-btn">
            Próx. Cap. ⏭️
          </button>
        </div>
      </div>

      <!-- Settings Panel -->
      <div v-if="showSettings" class="settings-panel">
        <div class="settings-content">
          <h3>⚙️ Configurações de Leitura</h3>
          
          <div class="setting-group">
            <label>📏 Ajuste de Imagem:</label>
            <select v-model="fitMode">
              <option value="width">Ajustar Largura</option>
              <option value="height">Ajustar Altura</option>
              <option value="screen">Ajustar Tela</option>
              <option value="original">Tamanho Original</option>
            </select>
          </div>

          <div class="setting-group">
            <label>📖 Direção de Leitura:</label>
            <select v-model="readingDirection">
              <option value="ltr">Esquerda → Direita</option>
              <option value="rtl">Direita → Esquerda</option>
            </select>
          </div>

          <div class="setting-group">
            <label>👆 Zonas de Toque:</label>
            <select v-model="touchZones">
              <option value="edge">Bordas</option>
              <option value="kindle">Estilo Kindle</option>
              <option value="l-shape">Formato L</option>
              <option value="split">Dividido</option>
            </select>
          </div>

          <div class="setting-group">
            <label>🌙 Tema:</label>
            <select v-model="theme">
              <option value="dark">Escuro</option>
              <option value="light">Claro</option>
              <option value="sepia">Sépia</option>
            </select>
          </div>

          <div class="setting-group">
            <label>⏱️ Auto-scroll (segundos):</label>
            <input 
              v-model.number="autoScrollDelay" 
              type="range" 
              min="0" 
              max="10" 
              step="0.5"
            />
            <span>{{ autoScrollDelay || 'Desativado' }}</span>
          </div>

          <div class="setting-actions">
            <button @click="resetSettings" class="secondary-btn">
              🔄 Redefinir
            </button>
            <button @click="showSettings = false" class="primary-btn">
              ✅ Aplicar
            </button>
          </div>
        </div>
      </div>

      <!-- Keyboard Shortcuts Help -->
      <div v-if="showHelp" class="help-panel">
        <div class="help-content">
          <h3>⌨️ Atalhos do Teclado</h3>
          <div class="shortcuts">
            <div class="shortcut-item">
              <kbd>Space</kbd> / <kbd>→</kbd> - Próxima página
            </div>
            <div class="shortcut-item">
              <kbd>Backspace</kbd> / <kbd>←</kbd> - Página anterior
            </div>
            <div class="shortcut-item">
              <kbd>F</kbd> - Tela cheia
            </div>
            <div class="shortcut-item">
              <kbd>H</kbd> - Mostrar/ocultar controles
            </div>
            <div class="shortcut-item">
              <kbd>S</kbd> - Configurações
            </div>
            <div class="shortcut-item">
              <kbd>Esc</kbd> - Sair da tela cheia
            </div>
          </div>
          <button @click="showHelp = false" class="primary-btn">
            ✅ Entendi
          </button>
        </div>
      </div>
    </div>

    <!-- Floating Action Buttons -->
    <div class="floating-actions" v-if="!hideControls">
      <button @click="showHelp = true" class="fab help">❓</button>
      <button @click="toggleAutoScroll" class="fab auto-scroll" :class="{ active: autoScrollActive }">
        {{ autoScrollActive ? '⏸️' : '▶️' }}
      </button>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useLibraryStore } from '@/store/library'

export default {
  name: 'MangaReaderView',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const libraryStore = useLibraryStore()

    // Reactive data
    const manga = ref(null)
    const chapter = ref(null)
    const loading = ref(true)
    const error = ref(null)
    const currentPage = ref(0)
    const isFullscreen = ref(false)
    const hideControls = ref(false)
    const showSettings = ref(false)
    const showHelp = ref(false)
    const readingArea = ref(null)

    // Reading settings
    const readingMode = ref('single') // single, double, vertical, webtoon
    const fitMode = ref('width') // width, height, screen, original
    const readingDirection = ref('rtl') // ltr, rtl
    const touchZones = ref('edge') // edge, kindle, l-shape, split
    const theme = ref('dark') // dark, light, sepia
    const autoScrollDelay = ref(0)
    const autoScrollActive = ref(false)

    // Auto-hide controls
    let controlsTimeout = null
    let autoScrollInterval = null

    // Computed
    const mangaId = computed(() => route.params.mangaId)
    const chapterId = computed(() => route.params.chapterId)
    
    const totalPages = computed(() => chapter.value?.pages?.length || 0)
    
    const currentPageData = computed(() => {
      if (!chapter.value?.pages || currentPage.value < 0) return null
      return chapter.value.pages[currentPage.value]
    })
    
    const nextPageData = computed(() => {
      if (!chapter.value?.pages || currentPage.value >= totalPages.value - 1) return null
      return chapter.value.pages[currentPage.value + 1]
    })
    
    const visiblePages = computed(() => {
      if (!chapter.value?.pages) return []
      
      if (readingMode.value === 'vertical' || readingMode.value === 'webtoon') {
        // Para modo vertical, mostrar todas as páginas
        return chapter.value.pages
      }
      
      return [currentPageData.value].filter(Boolean)
    })
    
    const progressPercentage = computed(() => {
      if (totalPages.value === 0) return 0
      return (currentPage.value / (totalPages.value - 1)) * 100
    })
    
    const pageStyle = computed(() => {
      const styles = {}
      
      switch (fitMode.value) {
        case 'width':
          styles.width = '100%'
          styles.height = 'auto'
          break
        case 'height':
          styles.height = '100vh'
          styles.width = 'auto'
          break
        case 'screen':
          styles.maxWidth = '100%'
          styles.maxHeight = '100vh'
          styles.objectFit = 'contain'
          break
        case 'original':
          // Tamanho original da imagem
          break
      }
      
      return styles
    })
    
    const hasPreviousChapter = computed(() => {
      // TODO: Implementar verificação de capítulo anterior
      return false
    })
    
    const hasNextChapter = computed(() => {
      // TODO: Implementar verificação de próximo capítulo
      return false
    })

    // Methods
    const loadChapter = async () => {
      loading.value = true
      error.value = null
      
      try {
        // Carregar mangá se não estiver carregado
        if (!manga.value) {
          manga.value = await libraryStore.fetchManga(mangaId.value)
        }
        
        // Encontrar capítulo
        const foundChapter = manga.value.chapters?.find(ch => ch.id === chapterId.value)
        
        if (!foundChapter) {
          throw new Error('Capítulo não encontrado')
        }
        
        chapter.value = foundChapter
        
        // Carregar progresso salvo
        loadReadingProgress()
        
        // Pré-carregar próximas páginas
        preloadPages()
        
      } catch (err) {
        error.value = err.message || 'Erro ao carregar capítulo'
        console.error('Erro ao carregar capítulo:', err)
      } finally {
        loading.value = false
      }
    }

    const loadReadingProgress = () => {
      const savedProgress = localStorage.getItem(`ohara_progress_${mangaId.value}_${chapterId.value}`)
      if (savedProgress) {
        const progress = JSON.parse(savedProgress)
        currentPage.value = progress.currentPage || 0
      }
    }

    const saveReadingProgress = () => {
      const progress = {
        currentPage: currentPage.value,
        totalPages: totalPages.value,
        timestamp: Date.now(),
        percentage: progressPercentage.value
      }
      
      localStorage.setItem(`ohara_progress_${mangaId.value}_${chapterId.value}`, JSON.stringify(progress))
      
      // Também salvar no progresso geral do mangá
      const mangaProgress = JSON.parse(localStorage.getItem(`ohara_progress_${mangaId.value}`) || '{}')
      mangaProgress.currentChapterId = chapterId.value
      mangaProgress.lastReadAt = new Date().toISOString()
      localStorage.setItem(`ohara_progress_${mangaId.value}`, JSON.stringify(mangaProgress))
    }

    const preloadPages = () => {
      if (!chapter.value?.pages) return
      
      // Pré-carregar próximas 5 páginas
      const startIndex = Math.max(0, currentPage.value)
      const endIndex = Math.min(totalPages.value, currentPage.value + 5)
      
      for (let i = startIndex; i < endIndex; i++) {
        const img = new Image()
        img.src = chapter.value.pages[i].path
      }
    }

    const nextPage = () => {
      if (currentPage.value < totalPages.value - 1) {
        currentPage.value++
        saveReadingProgress()
        preloadPages()
        resetControlsTimer()
      } else {
        // Final do capítulo - ir para próximo capítulo
        nextChapter()
      }
    }

    const previousPage = () => {
      if (currentPage.value > 0) {
        currentPage.value--
        saveReadingProgress()
        resetControlsTimer()
      } else {
        // Início do capítulo - ir para capítulo anterior
        previousChapter()
      }
    }

    const nextChapter = () => {
      // TODO: Implementar navegação para próximo capítulo
      console.log('Próximo capítulo')
    }

    const previousChapter = () => {
      // TODO: Implementar navegação para capítulo anterior
      console.log('Capítulo anterior')
    }

    const handlePageClick = (event) => {
      if (showSettings.value || showHelp.value) return
      
      const rect = readingArea.value.getBoundingClientRect()
      const x = event.clientX - rect.left
      const width = rect.width
      
      // Determinar zona de clique baseada nas configurações
      let clickZone = 'next' // default
      
      switch (touchZones.value) {
        case 'edge':
          clickZone = x < width * 0.2 ? 'prev' : x > width * 0.8 ? 'next' : 'menu'
          break
        case 'kindle':
          clickZone = x < width * 0.3 ? 'prev' : x > width * 0.7 ? 'next' : 'menu'
          break
        case 'l-shape':
          clickZone = x < width * 0.5 ? 'prev' : 'next'
          break
        case 'split':
          clickZone = x < width * 0.5 ? 'prev' : 'next'
          break
      }
      
      // Executar ação
      switch (clickZone) {
        case 'prev':
          if (readingDirection.value === 'rtl') {
            nextPage()
          } else {
            previousPage()
          }
          break
        case 'next':
          if (readingDirection.value === 'rtl') {
            previousPage()
          } else {
            nextPage()
          }
          break
        case 'menu':
          toggleControls()
          break
      }
    }

    const toggleControls = () => {
      hideControls.value = !hideControls.value
      resetControlsTimer()
    }

    const resetControlsTimer = () => {
      if (controlsTimeout) {
        clearTimeout(controlsTimeout)
      }
      
      if (!hideControls.value) {
        controlsTimeout = setTimeout(() => {
          hideControls.value = true
        }, 3000) // Esconder após 3 segundos
      }
    }

    const toggleFullscreen = async () => {
      if (!document.fullscreenElement) {
        await document.documentElement.requestFullscreen()
        isFullscreen.value = true
      } else {
        await document.exitFullscreen()
        isFullscreen.value = false
      }
    }

    const toggleAutoScroll = () => {
      if (autoScrollActive.value) {
        stopAutoScroll()
      } else {
        startAutoScroll()
      }
    }

    const startAutoScroll = () => {
      if (autoScrollDelay.value <= 0) return
      
      autoScrollActive.value = true
      autoScrollInterval = setInterval(() => {
        nextPage()
      }, autoScrollDelay.value * 1000)
    }

    const stopAutoScroll = () => {
      autoScrollActive.value = false
      if (autoScrollInterval) {
        clearInterval(autoScrollInterval)
        autoScrollInterval = null
      }
    }

    const seekToPosition = (event) => {
      const rect = event.target.getBoundingClientRect()
      const x = event.clientX - rect.left
      const percentage = x / rect.width
      const targetPage = Math.floor(percentage * totalPages.value)
      
      currentPage.value = Math.max(0, Math.min(totalPages.value - 1, targetPage))
      saveReadingProgress()
    }

    const resetSettings = () => {
      readingMode.value = 'single'
      fitMode.value = 'width'
      readingDirection.value = 'rtl'
      touchZones.value = 'edge'
      theme.value = 'dark'
      autoScrollDelay.value = 0
    }

    const goBack = () => {
      router.back()
    }

    const onImageLoad = () => {
      // Imagem carregada com sucesso
    }

    const onImageError = () => {
      console.error('Erro ao carregar imagem da página')
    }

    // Keyboard shortcuts
    const handleKeydown = (event) => {
      if (showSettings.value || showHelp.value) return
      
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
          showSettings.value = !showSettings.value
          break
        case 'Escape':
          event.preventDefault()
          if (isFullscreen.value) {
            toggleFullscreen()
          } else if (showSettings.value) {
            showSettings.value = false
          } else if (showHelp.value) {
            showHelp.value = false
          }
          break
      }
    }

    // Lifecycle
    onMounted(() => {
      loadChapter()
      document.addEventListener('keydown', handleKeydown)
      resetControlsTimer()
      
      // Detectar mudanças de fullscreen
      document.addEventListener('fullscreenchange', () => {
        isFullscreen.value = !!document.fullscreenElement
      })
    })

    onUnmounted(() => {
      document.removeEventListener('keydown', handleKeydown)
      if (controlsTimeout) {
        clearTimeout(controlsTimeout)
      }
      stopAutoScroll()
    })

    // Watch route changes
    watch(() => route.params, () => {
      if (route.params.chapterId !== chapterId.value) {
        loadChapter()
      }
    })

    // Watch current page changes
    watch(currentPage, () => {
      saveReadingProgress()
    })

    return {
      manga,
      chapter,
      loading,
      error,
      currentPage,
      totalPages,
      isFullscreen,
      hideControls,
      showSettings,
      showHelp,
      readingArea,
      readingMode,
      fitMode,
      readingDirection,
      touchZones,
      theme,
      autoScrollDelay,
      autoScrollActive,
      currentPageData,
      nextPageData,
      visiblePages,
      progressPercentage,
      pageStyle,
      hasPreviousChapter,
      hasNextChapter,
      loadChapter,
      nextPage,
      previousPage,
      nextChapter,
      previousChapter,
      handlePageClick,
      toggleControls,
      toggleFullscreen,
      toggleAutoScroll,
      seekToPosition,
      resetSettings,
      goBack,
      onImageLoad,
      onImageError
    }
  }
}
</script>

<style scoped>
.manga-reader {
  position: relative;
  min-height: 100vh;
  background: #000;
  color: white;
  overflow: hidden;
  user-select: none;
}

.manga-reader.fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 9999;
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
  margin-top: 1rem;
}

/* Header Controls */
.reader-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background: linear-gradient(to bottom, rgba(0,0,0,0.8), transparent);
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
}

.control-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 5px;
  color: white;
  cursor: pointer;
  transition: background 0.2s;
}

.control-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.control-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Reading Area */
.reading-area {
  position: relative;
  width: 100%;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  cursor: pointer;
}

.single-page-container {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.double-page-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  width: 100%;
  height: 100%;
}

.vertical-container {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

.webtoon-container {
  width: 100%;
  max-width: 600px;
  margin: 0 auto;
}

.page-image {
  display: block;
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  transition: transform 0.2s ease;
}

.page-image.vertical {
  width: 100%;
  height: auto;
  margin-bottom: 1rem;
}

.page-image.webtoon {
  width: 100%;
  height: auto;
}

.webtoon-page {
  margin-bottom: 2rem;
}

/* Navigation Zones */
.nav-zones {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  pointer-events: none;
}

.nav-zone {
  flex: 1;
  pointer-events: all;
  cursor: pointer;
}

.nav-zone.prev {
  background: linear-gradient(to right, rgba(255,255,255,0.1), transparent);
}

.nav-zone.next {
  background: linear-gradient(to left, rgba(255,255,255,0.1), transparent);
}

/* Footer Controls */
.reader-footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(to top, rgba(0,0,0,0.8), transparent);
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
  border: none;
  padding: 0.5rem;
  border-radius: 5px;
  color: white;
  cursor: pointer;
}

/* Settings Panel */
.settings-panel {
  position: fixed;
  top: 0;
  right: 0;
  width: 350px;
  height: 100vh;
  background: rgba(0, 0, 0, 0.95);
  backdrop-filter: blur(10px);
  z-index: 200;
  overflow-y: auto;
}

.settings-content {
  padding: 2rem;
}

.settings-content h3 {
  color: #4ecdc4;
  margin-bottom: 2rem;
  text-align: center;
}

.setting-group {
  margin-bottom: 1.5rem;
}

.setting-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
}

.setting-group select,
.setting-group input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 5px;
  background: rgba(0, 0, 0, 0.5);
  color: white;
}

.setting-actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
}

.primary-btn, .secondary-btn {
  flex: 1;
  padding: 0.75rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
}

.primary-btn {
  background: #4ecdc4;
  color: white;
}

.secondary-btn {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

/* Help Panel */
.help-panel {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(0, 0, 0, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 15px;
  padding: 2rem;
  z-index: 200;
  max-width: 400px;
  width: 90%;
}

.help-content h3 {
  color: #4ecdc4;
  margin-bottom: 1rem;
  text-align: center;
}

.shortcuts {
  margin-bottom: 2rem;
}

.shortcut-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

kbd {
  background: rgba(255, 255, 255, 0.2);
  padding: 0.25rem 0.5rem;
  border-radius: 3px;
  font-size: 0.8rem;
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
  transition: transform 0.2s;
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.fab:hover {
  transform: scale(1.1);
}

.fab.auto-scroll.active {
  background: #4ecdc4;
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
  }
  
  .settings-panel {
    width: 100%;
  }
  
  .floating-actions {
    bottom: 1rem;
    right: 1rem;
  }
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
</style>