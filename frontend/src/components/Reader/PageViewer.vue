<template>
  <div 
    class="page-viewer" 
    :class="[
      `mode-${readingMode}`, 
      `fit-${fitMode}`, 
      `theme-${theme}`,
      { 'fullscreen': isFullscreen }
    ]"
    ref="viewerContainer"
    @click="handleClick"
    @wheel="handleWheel"
    @touchstart="handleTouchStart"
    @touchend="handleTouchEnd"
  >
    <!-- Single Page Mode -->
    <div v-if="readingMode === 'single'" class="single-page-container">
      <div v-if="currentPageData" class="page-wrapper">
        <img
          :src="currentPageData.url"
          :alt="`Página ${currentPage + 1}`"
          class="page-image"
          :style="pageImageStyle"
          @load="onImageLoad"
          @error="onImageError"
        />
        
        <!-- Loading placeholder -->
        <div v-if="imageLoading" class="image-loading">
          <div class="spinner"></div>
          <p>Carregando página...</p>
        </div>
      </div>
      
    </div>


    <!-- Vertical Continuous Mode -->
    <div v-if="readingMode === 'vertical'" class="vertical-container" ref="verticalContainer">
      <div 
        v-for="(page, index) in visiblePages" 
        :key="page.url"
        class="page-wrapper vertical"
        :data-page-index="index"
      >
        <img
          :src="page.url"
          :alt="`Página ${index + 1}`"
          class="page-image vertical"
          :style="verticalPageStyle"
          @load="onImageLoad"
          @error="onImageError"
        />
      </div>
    </div>


    <!-- Page transition effects -->
    <transition name="page-fade">
      <div v-if="pageTransition" class="page-transition">
        <div class="transition-content">
          <span v-if="pageTransition === 'next'">→</span>
          <span v-if="pageTransition === 'previous'">←</span>
        </div>
      </div>
    </transition>

    <!-- Zoom controls (para modo original) -->
    <div v-if="fitMode === 'original' && readingMode === 'single'" class="zoom-controls">
      <button @click="zoomIn" class="zoom-btn">🔍+</button>
      <button @click="zoomOut" class="zoom-btn">🔍-</button>
      <button @click="resetZoom" class="zoom-btn">⚏</button>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'

export default {
  name: 'PageViewer',
  props: {
    currentPageData: Object,
    nextPageData: Object,
    visiblePages: Array,
    currentPage: Number,
    totalPages: Number,
    readingMode: String,
    fitMode: String,
    theme: String,
    isFullscreen: Boolean
  },

  emits: [
    'next-page',
    'previous-page',
    'toggle-controls',
    'page-changed',
    'zoom-changed'
  ],

  setup(props, { emit }) {
    // Reactive data
    const viewerContainer = ref(null)
    const verticalContainer = ref(null)
    const imageLoading = ref(false)
    const pageTransition = ref(null)
    const zoomLevel = ref(1)
    const panOffset = ref({ x: 0, y: 0 })
    
    // Touch handling
    const touchStart = ref({ x: 0, y: 0, time: 0 })
    const touchEnd = ref({ x: 0, y: 0, time: 0 })

    // Computed styles
    const pageImageStyle = computed(() => {
      const style = {}
      
      switch (props.fitMode) {
        case 'width':
          style.width = '100%'
          style.height = 'auto'
          style.maxHeight = '100vh'
          break
        case 'height':
          style.height = '100vh'
          style.width = 'auto'
          style.maxWidth = '100%'
          break
        case 'screen':
          style.maxWidth = '100%'
          style.maxHeight = '100vh'
          style.objectFit = 'contain'
          break
        case 'original':
          style.transform = `scale(${zoomLevel.value}) translate(${panOffset.value.x}px, ${panOffset.value.y}px)`
          style.transformOrigin = 'center center'
          break
      }
      
      return style
    })

    const verticalPageStyle = computed(() => ({
      width: '100%',
      height: 'auto',
      display: 'block',
      marginBottom: '1rem'
    }))



    // Methods
    const handleClick = (event) => {
      if (props.readingMode === 'vertical') {
        return // Não usar cliques em modo scroll
      }

      // Clique simples no centro da tela para toggle de controles
      emit('toggle-controls')
    }


    const showPageTransition = (direction) => {
      pageTransition.value = direction
      setTimeout(() => {
        pageTransition.value = null
      }, 200)
    }

    const handleWheel = (event) => {
      if (props.fitMode === 'original') {
        // Zoom com scroll wheel
        event.preventDefault()
        const delta = event.deltaY > 0 ? -0.1 : 0.1
        zoomLevel.value = Math.max(0.5, Math.min(3, zoomLevel.value + delta))
        emit('zoom-changed', zoomLevel.value)
      }
    }

    const handleTouchStart = (event) => {
      const touch = event.touches[0]
      touchStart.value = {
        x: touch.clientX,
        y: touch.clientY,
        time: Date.now()
      }
    }

    const handleTouchEnd = (event) => {
      const touch = event.changedTouches[0]
      touchEnd.value = {
        x: touch.clientX,
        y: touch.clientY,
        time: Date.now()
      }

      // Detectar swipe
      const deltaX = touchEnd.value.x - touchStart.value.x
      const deltaY = touchEnd.value.y - touchStart.value.y
      const deltaTime = touchEnd.value.time - touchStart.value.time

      // Swipe mínimo: 50px em menos de 300ms
      if (deltaTime < 300 && Math.abs(deltaX) > 50) {
        if (deltaX > 0) {
          // Swipe para direita = página anterior
          emit('previous-page')
        } else {
          // Swipe para esquerda = próxima página
          emit('next-page')
        }
        
        showPageTransition(deltaX > 0 ? 'previous' : 'next')
      }
    }

    // Zoom controls
    const zoomIn = () => {
      zoomLevel.value = Math.min(3, zoomLevel.value + 0.25)
      emit('zoom-changed', zoomLevel.value)
    }

    const zoomOut = () => {
      zoomLevel.value = Math.max(0.5, zoomLevel.value - 0.25)
      emit('zoom-changed', zoomLevel.value)
    }

    const resetZoom = () => {
      zoomLevel.value = 1
      panOffset.value = { x: 0, y: 0 }
      emit('zoom-changed', zoomLevel.value)
    }

    const onImageLoad = () => {
      imageLoading.value = false
    }

    const onImageError = (event) => {
      imageLoading.value = false
      console.error('Erro ao carregar imagem:', event.target.src)
      
      // Substituir por placeholder
      event.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjQwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjMzMzIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIyMCIgZmlsbD0iI2ZmZiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkVycm8gYW8gY2FycmVnYXI8L3RleHQ+PC9zdmc+'
    }

    // Scroll handling for vertical mode
    const handleVerticalScroll = () => {
      if (props.readingMode !== 'vertical') return

      const container = verticalContainer.value
      if (!container) return

      // Determinar página atual baseada no scroll
      const scrollTop = container.scrollTop
      const pageElements = container.querySelectorAll('[data-page-index]')
      
      let currentPageIndex = 0
      for (let element of pageElements) {
        const rect = element.getBoundingClientRect()
        const containerRect = container.getBoundingClientRect()
        
        if (rect.top <= containerRect.top + containerRect.height / 2) {
          currentPageIndex = parseInt(element.dataset.pageIndex)
        }
      }
      
      if (currentPageIndex !== props.currentPage) {
        emit('page-changed', currentPageIndex)
      }
    }

    // Watchers
    watch(() => props.currentPage, (newPage) => {
      imageLoading.value = true
      
      // Auto-navegação em modo vertical
      if (props.readingMode === 'vertical' && newPage >= 0) {
        nextTick(() => {
          const container = verticalContainer.value
          const pageElement = container?.querySelector(`[data-page-index="${newPage}"]`)
          
          if (pageElement) {
            pageElement.scrollIntoView({ behavior: 'smooth', block: 'start' })
          }
        })
      }
    })

    // Lifecycle
    onMounted(() => {
      // Adicionar listeners para scroll em modo vertical
      if (props.readingMode === 'vertical') {
        const container = verticalContainer.value
        container?.addEventListener('scroll', handleVerticalScroll)
      }
    })

    onUnmounted(() => {
      // Remover listeners
      if (props.readingMode === 'vertical') {
        const container = verticalContainer.value
        container?.removeEventListener('scroll', handleVerticalScroll)
      }
    })

    return {
      viewerContainer,
      verticalContainer,
      imageLoading,
      pageTransition,
      zoomLevel,
      panOffset,
      pageImageStyle,
      verticalPageStyle,
      handleClick,
      handleWheel,
      handleTouchStart,
      handleTouchEnd,
      zoomIn,
      zoomOut,
      resetZoom,
      onImageLoad,
      onImageError
    }
  }
}
</script>

<style scoped>
.page-viewer {
  position: relative;
  width: 100%;
  height: 100vh;
  overflow: hidden;
  background: #000;
  user-select: none;
}

.page-viewer.fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  z-index: 9999;
}

/* Theme variations */
.page-viewer.theme-light {
  background: #fff;
}

.page-viewer.theme-sepia {
  background: #f4e5d3;
}

/* Single page mode */
.single-page-container {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.page-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  max-width: 100%;
  max-height: 100%;
}

.page-image {
  display: block;
  transition: transform 0.2s ease;
}



/* Vertical mode */
.vertical-container {
  height: 100vh;
  overflow-y: auto;
  overflow-x: hidden;
  scroll-behavior: smooth;
  padding: 1rem;
  max-width: 800px;
  margin: 0 auto;
}

.page-wrapper.vertical {
  margin-bottom: 1rem;
}

.page-image.vertical {
  width: 100%;
  height: auto;
}



/* Loading state */
.image-loading {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  color: white;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255,255,255,0.3);
  border-radius: 50%;
  border-top: 3px solid #4ecdc4;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Page transition effect */
.page-transition {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 100;
  pointer-events: none;
}

.transition-content {
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 1rem 2rem;
  border-radius: 50px;
  font-size: 2rem;
  backdrop-filter: blur(10px);
}

.page-fade-enter-active, .page-fade-leave-active {
  transition: opacity 0.2s;
}
.page-fade-enter-from, .page-fade-leave-to {
  opacity: 0;
}

/* Zoom controls */
.zoom-controls {
  position: absolute;
  bottom: 2rem;
  right: 2rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  z-index: 50;
}

.zoom-btn {
  width: 48px;
  height: 48px;
  border: none;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  transition: all 0.2s;
}

.zoom-btn:hover {
  background: rgba(0, 0, 0, 0.9);
  transform: scale(1.1);
}

/* Responsive */
@media (max-width: 768px) {
  .vertical-container {
    padding: 0.5rem;
  }
  
  .double-page-container {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .zoom-controls {
    bottom: 1rem;
    right: 1rem;
  }
  
  .zoom-btn {
    width: 40px;
    height: 40px;
    font-size: 0.9rem;
  }
}
</style>