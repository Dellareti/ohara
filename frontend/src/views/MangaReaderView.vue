<!-- frontend/src/views/MangaReaderView.vue -->
<template>
  <div class="manga-reader" :class="{ 
    'fullscreen': readerStore.isFullscreen, 
    'controls-hidden': readerStore.hideControls,
    [`theme-${readerStore.theme}`]: true
  }">
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
    <div v-if="readerStore.currentChapter && !loading" class="reader-content">
      <!-- Header Controls (hideable) -->
      <div class="reader-header" :class="{ 'hidden': readerStore.hideControls }">
        <div class="header-left">
          <button @click="goBack" class="control-btn">
            ← Voltar
          </button>
          <div class="chapter-info">
            <h3>{{ readerStore.currentManga?.title }}</h3>
            <p>{{ readerStore.currentChapter?.chapter?.name }}</p>
          </div>
        </div>

        <div class="header-right">
          <div class="page-counter">
            {{ readerStore.currentPage + 1 }} / {{ readerStore.totalPages }}
          </div>
          <button @click="toggleFullscreen" class="control-btn">
            {{ readerStore.isFullscreen ? '🗖' : '🗗' }}
          </button>
          <button @click="readerStore.toggleSettings" class="control-btn">
            ⚙️
          </button>
        </div>
      </div>

      <!-- Page Viewer Component -->
      <PageViewer
        :current-page-data="readerStore.currentPageData"
        :next-page-data="readerStore.nextPageData"
        :visible-pages="readerStore.visiblePages"
        :current-page="readerStore.currentPage"
        :total-pages="readerStore.totalPages"
        :reading-mode="readerStore.readingMode"
        :fit-mode="readerStore.fitMode"
        :reading-direction="readerStore.readingDirection"
        :touch-zones="readerStore.touchZones"
        :theme="readerStore.theme"
        :is-fullscreen="readerStore.isFullscreen"
        @next-page="nextPage"
        @previous-page="previousPage"
        @toggle-controls="toggleControls"
        @page-changed="onPageChanged"
        @zoom-changed="onZoomChanged"
      />

      <!-- Bottom Controls (hideable) -->
      <div class="reader-footer" :class="{ 'hidden': readerStore.hideControls }">
        <div class="progress-bar">
          <div class="progress-track" @click="seekToPosition">
            <div 
              class="progress-fill" 
              :style="{ width: readerStore.progressPercentage + '%' }"
            ></div>
            <div 
              class="progress-thumb" 
              :style="{ left: readerStore.progressPercentage + '%' }"
            ></div>
          </div>
        </div>

        <div class="footer-controls">
          <button 
            @click="previousChapter" 
            :disabled="!readerStore.hasPreviousChapter" 
            class="control-btn"
          >
            ⏮️ Cap. Anterior
          </button>
          
          <button 
            @click="previousPage" 
            :disabled="readerStore.currentPage <= 0" 
            class="control-btn"
          >
            ⏪ Anterior
          </button>
          
          <select v-model="readerStore.readingMode" class="mode-select">
            <option value="single">📄 Página Única</option>
            <option value="double">📖 Página Dupla</option>
            <option value="vertical">📜 Vertical</option>
            <option value="webtoon">📱 Webtoon</option>
          </select>
          
          <button 
            @click="nextPage" 
            :disabled="readerStore.currentPage >= readerStore.totalPages - 1" 
            class="control-btn"
          >
            Próxima ⏩
          </button>
          
          <button 
            @click="nextChapter" 
            :disabled="!readerStore.hasNextChapter" 
            class="control-btn"
          >
            Próx. Cap. ⏭️
          </button>
        </div>
      </div>

      <!-- Settings Panel -->
      <div v-if="readerStore.showSettings" class="settings-panel">
        <div class="settings-content">
          <h3>⚙️ Configurações de Leitura</h3>
          
          <div class="setting-group">
            <label>📏 Ajuste de Imagem:</label>
            <select v-model="readerStore.fitMode">
              <option value="width">Ajustar Largura</option>
              <option value="height">Ajustar Altura</option>
              <option value="screen">Ajustar Tela</option>
              <option value="original">Tamanho Original</option>
            </select>
          </div>

          <div class="setting-group">
            <label>📖 Direção de Leitura:</label>
            <select v-model="readerStore.readingDirection">
              <option value="ltr">Esquerda → Direita</option>
              <option value="rtl">Direita → Esquerda</option>
            </select>
          </div>

          <div class="setting-group">
            <label>👆 Zonas de Toque:</label>
            <select v-model="readerStore.touchZones">
              <option value="edge">Bordas</option>
              <option value="kindle">Estilo Kindle</option>
              <option value="l-shape">Formato L</option>
              <option value="split">Dividido</option>
            </select>
          </div>

          <div class="setting-group">
            <label>🌙 Tema:</label>
            <select v-model="readerStore.theme">
              <option value="dark">Escuro</option>
              <option value="light">Claro</option>
              <option value="sepia">Sépia</option>
            </select>
          </div>

          <div class="setting-group">
            <label>⏱️ Auto-scroll (segundos):</label>
            <input 
              v-model.number="readerStore.autoScrollDelay" 
              type="range" 
              min="0" 
              max="10" 
              step="0.5"
            />
            <span>{{ readerStore.autoScrollDelay || 'Desativado' }}</span>
          </div>

          <div class="setting-actions">
            <button @click="readerStore.resetSettings" class="secondary-btn">
              🔄 Redefinir
            </button>
            <button @click="readerStore.showSettings = false" class="primary-btn">
              ✅ Aplicar
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Floating Action Buttons -->
    <div class="floating-actions" v-if="!readerStore.hideControls">
      <button @click="toggleAutoScroll" class="fab auto-scroll" :class="{ active: readerStore.autoScrollActive }">
        {{ readerStore.autoScrollActive ? '⏸️' : '▶️' }}
      </button>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useLibraryStore } from '@/store/library'
import { useReaderStore } from '@/store/reader'
import PageViewer from '@/components/Reader/PageViewer.vue'

export default {
  name: 'MangaReaderView',
  components: {
    PageViewer
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const libraryStore = useLibraryStore()
    const readerStore = useReaderStore()

    // Reactive data
    const loading = ref(true)
    const error = ref(null)
    const readingArea = ref(null)

    // Auto-hide controls
    let controlsTimeout = null
    let autoScrollInterval = null

    // Computed
    const mangaId = computed(() => route.params.mangaId)
    const chapterId = computed(() => route.params.chapterId)

    // Methods
    const loadChapter = async () => {
      loading.value = true
      error.value = null
      
      try {
        await readerStore.loadChapter(mangaId.value, chapterId.value)
        resetControlsTimer()
      } catch (err) {
        error.value = err.message || 'Erro ao carregar capítulo'
        console.error('Erro ao carregar capítulo:', err)
      } finally {
        loading.value = false
      }
    }

    const nextPage = () => {
      const hasNext = readerStore.nextPage()
      if (!hasNext) {
        // Final do capítulo - ir para próximo capítulo
        nextChapter()
      }
      resetControlsTimer()
    }

    const previousPage = () => {
      const hasPrev = readerStore.previousPage()
      if (!hasPrev) {
        // Início do capítulo - ir para capítulo anterior
        previousChapter()
      }
      resetControlsTimer()
    }

    const nextChapter = () => {
      if (readerStore.navigation.nextChapter) {
        router.push({
          name: 'MangaReader',
          params: {
            mangaId: mangaId.value,
            chapterId: readerStore.navigation.nextChapter.id
          }
        })
      }
    }

    const previousChapter = () => {
      if (readerStore.navigation.previousChapter) {
        router.push({
          name: 'MangaReader',
          params: {
            mangaId: mangaId.value,
            chapterId: readerStore.navigation.previousChapter.id
          }
        })
      }
    }

    const toggleControls = () => {
      readerStore.toggleControls()
      resetControlsTimer()
    }

    const resetControlsTimer = () => {
      if (controlsTimeout) {
        clearTimeout(controlsTimeout)
      }
      
      if (!readerStore.hideControls) {
        controlsTimeout = setTimeout(() => {
          readerStore.hideControls = true
        }, 3000) // Esconder após 3 segundos
      }
    }

    const toggleFullscreen = async () => {
      if (!document.fullscreenElement) {
        await document.documentElement.requestFullscreen()
        readerStore.isFullscreen = true
      } else {
        await document.exitFullscreen()
        readerStore.isFullscreen = false
      }
    }

    const toggleAutoScroll = () => {
      if (readerStore.autoScrollActive) {
        stopAutoScroll()
      } else {
        startAutoScroll()
      }
    }

    const startAutoScroll = () => {
      if (readerStore.autoScrollDelay <= 0) return
      
      readerStore.autoScrollActive = true
      autoScrollInterval = setInterval(() => {
        nextPage()
      }, readerStore.autoScrollDelay * 1000)
    }

    const stopAutoScroll = () => {
      readerStore.autoScrollActive = false
      if (autoScrollInterval) {
        clearInterval(autoScrollInterval)
        autoScrollInterval = null
      }
    }

    const seekToPosition = (event) => {
      const rect = event.target.getBoundingClientRect()
      const x = event.clientX - rect.left
      const percentage = (x / rect.width) * 100
      
      readerStore.seekToProgress(percentage)
      resetControlsTimer()
    }

    const goBack = () => {
      router.push({
        name: 'MangaDetail',
        params: { id: mangaId.value }
      })
    }

    const onPageChanged = (pageIndex) => {
      readerStore.currentPage = pageIndex
    }

    const onZoomChanged = (zoomLevel) => {
      console.log('🔍 Zoom alterado:', zoomLevel)
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
          readerStore.toggleSettings()
          break
        case 'Escape':
          event.preventDefault()
          if (readerStore.isFullscreen) {
            toggleFullscreen()
          } else if (readerStore.showSettings) {
            readerStore.showSettings = false
          }
          break
      }
    }

    // Lifecycle
    onMounted(() => {
      // Carregar configurações do leitor
      readerStore.loadSettings()
      
      // Carregar capítulo
      loadChapter()
      
      // Adicionar listeners
      document.addEventListener('keydown', handleKeydown)
      resetControlsTimer()
      
      // Detectar mudanças de fullscreen
      document.addEventListener('fullscreenchange', () => {
        readerStore.isFullscreen = !!document.fullscreenElement
      })
    })

    onUnmounted(() => {
      document.removeEventListener('keydown', handleKeydown)
      if (controlsTimeout) {
        clearTimeout(controlsTimeout)
      }
      stopAutoScroll()
      
      // Limpar store do leitor
      readerStore.clearReader()
    })

    // Watch route changes
    watch(() => route.params, () => {
      if (route.params.chapterId !== chapterId.value) {
        loadChapter()
      }
    })

    return {
      // Store states
      readerStore,
      loading,
      error,
      readingArea,
      
      // Methods
      loadChapter,
      nextPage,
      previousPage,
      nextChapter,
      previousChapter,
      toggleControls,
      toggleFullscreen,
      toggleAutoScroll,
      seekToPosition,
      goBack,
      onPageChanged,
      onZoomChanged
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

/* Theme variations */
.manga-reader.theme-light {
  background: #fff;
  color: #000;
}

.manga-reader.theme-sepia {
  background: #f4e5d3;
  color: #5d4037;
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
</style>