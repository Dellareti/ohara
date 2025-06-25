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
      
      <!-- Navigation zones -->
      <div class="nav-zones" :class="`zones-${touchZones}`">
        <div class="nav-zone previous" @click.stop="$emit('previous-page')"></div>
        <div class="nav-zone menu" @click.stop="$emit('toggle-controls')"></div>
        <div class="nav-zone next" @click.stop="$emit('next-page')"></div>
      </div>
    </div>

    <!-- Double Page Mode -->
    <div v-if="readingMode === 'double'" class="double-page-container">
      <div class="page-wrapper left" :class="{ 'rtl': readingDirection === 'rtl' }">
        <img
          v-if="leftPageData"
          :src="leftPageData.url"
          :alt="`Página ${leftPageIndex + 1}`"
          class="page-image"
          :style="pageImageStyle"
          @load="onImageLoad"
          @error="onImageError"
        />
      </div>
      
      <div class="page-wrapper right" :class="{ 'rtl': readingDirection === 'rtl' }">
        <img
          v-if="rightPageData"
          :src="rightPageData.url"
          :alt="`Página ${rightPageIndex + 1}`"
          class="page-image"
          :style="pageImageStyle"
          @load="onImageLoad"
          @error="onImageError"
        />
      </div>
      
      <!-- Navigation zones for double page -->
      <div class="nav-zones double">
        <div class="nav-zone previous" @click.stop="$emit('previous-page')"></div>
        <div class="nav-zone menu" @click.stop="$emit('toggle-controls')"></div>
        <div class="nav-zone next" @click.stop="$emit('next-page')"></div>
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

    <!-- Webtoon Mode -->
    <div v-if="readingMode === 'webtoon'" class="webtoon-container" ref="webtoonContainer">
      <div 
        v-for="(page, index) in visiblePages" 
        :key="page.url"
        class="webtoon-page"
        :data-page-index="index"
      >
        <img
          :src="page.url"
          :alt="`Página ${index + 1}`"
          class="page-image webtoon"
          :style="webtoonPageStyle"
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
    readingDirection: String,
    touchZones: String,
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
    const webtoonContainer = ref(null)
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

    const webtoonPageStyle = computed(() => ({
      width: '100%',
      height: 'auto',
      display: 'block',
      marginBottom: '2rem'
    }))

    // Double page logic
    const leftPageData = computed(() => {
      if (props.readingDirection === 'rtl') {
        return props.nextPageData || props.currentPageData
      } else {
        return props.currentPageData
      }
    })

    const rightPageData = computed(() => {
      if (props.readingDirection === 'rtl') {
        return props.currentPageData
      } else {
        return props.nextPageData
      }
    })

    const leftPageIndex = computed(() => {
      if (props.readingDirection === 'rtl') {
        return props.currentPage + 1
      } else {
        return props.currentPage
      }
    })

    const rightPageIndex = computed(() => {
      if (props.readingDirection === 'rtl') {
        return props.currentPage
      } else {
        return props.currentPage + 1
      }
    })

    // Methods
    const handleClick = (event) => {
      if (props.readingMode === 'vertical' || props.readingMode === 'webtoon') {
        return // Não usar cliques em modos de scroll
      }

      const rect = viewerContainer.value.getBoundingClientRect()
      const x = event.clientX - rect.left
      const y = event.clientY - rect.top
      const width = rect.width
      const height = rect.height

      // Determinar zona de clique
      let zone = 'menu'
      
      switch (props.touchZones) {
        case 'edge':
          if (x < width * 0.15) zone = 'previous'
          else if (x > width * 0.85) zone = 'next'
          else zone = 'menu'
          break
        case 'kindle':
          if (x < width * 0.25) zone = 'previous'
          else if (x > width * 0.75) zone = 'next'
          else zone = 'menu'
          break
        case 'l-shape':
          if (x < width * 0.5 || y < height * 0.25) zone = 'previous'
          else zone = 'next'
          break
        case 'split':
          zone = x < width * 0.5 ? 'previous' : 'next'
          break
      }

      // Executar ação baseada na direção de leitura
      executeZoneAction(zone)
    }

    const executeZoneAction = (zone) => {
      if (zone === 'menu') {
        emit('toggle-controls')
        return
      }

      // Ajustar para direção de leitura
      if (props.readingDirection === 'rtl') {
        if (zone === 'previous') emit('next-page')
        else if (zone === 'next') emit('previous-page')
      } else {
        if (zone === 'previous') emit('previous-page')
        else if (zone === 'next') emit('next-page')
      }

      // Mostrar efeito de transição
      showPageTransition(zone)
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
          // Swipe para direita
          if (props.readingDirection === 'rtl') {
            emit('next-page')
          } else {
            emit('previous-page')
          }
        } else {
          // Swipe para esquerda
          if (props.readingDirection === 'rtl') {
            emit('previous-page')
          } else {
            emit('next-page')
          }
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

    // Scroll handling for vertical modes
    const handleVerticalScroll = () => {
      if (props.readingMode !== 'vertical' && props.readingMode !== 'webtoon') return

      const container = props.readingMode === 'vertical' ? verticalContainer.value : webtoonContainer.value
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
      
      // Auto-scroll em modo vertical
      if ((props.readingMode === 'vertical' || props.readingMode === 'webtoon') && newPage >= 0) {
        nextTick(() => {
          const container = props.readingMode === 'vertical' ? verticalContainer.value : webtoonContainer.value
          const pageElement = container?.querySelector(`[data-page-index="${newPage}"]`)
          
          if (pageElement) {
            pageElement.scrollIntoView({ behavior: 'smooth', block: 'start' })
          }
        })
      }
    })

    // Lifecycle
    onMounted(() => {
      // Adicionar listeners para scroll em modos verticais
      if (props.readingMode === 'vertical' || props.readingMode === 'webtoon') {
        const container = props.readingMode === 'vertical' ? verticalContainer.value : webtoonContainer.value
        container?.addEventListener('scroll', handleVerticalScroll)
      }
    })

    onUnmounted(() => {
      // Remover listeners
      const container = props.readingMode === 'vertical' ? verticalContainer.value : webtoonContainer.value
      container?.removeEventListener('scroll', handleVerticalScroll)
    })

    return {
      viewerContainer,
      verticalContainer,
      webtoonContainer,
      imageLoading,
      pageTransition,
      zoomLevel,
      panOffset,
      pageImageStyle,
      verticalPageStyle,
      webtoonPageStyle,
      leftPageData,
      rightPageData,
      leftPageIndex,
      rightPageIndex,
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

/* Double page mode */
.double-page-container {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 1rem;
}

.page-wrapper.left,
.page-wrapper.right {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.page-wrapper.rtl {
  order: -1;
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

/* Webtoon mode */
.webtoon-container {
  height: 100vh;
  overflow-y: auto;
  overflow-x: hidden;
  scroll-behavior: smooth;
  max-width: 600px;
  margin: 0 auto;
}

.webtoon-page {
  margin-bottom: 2rem;
}

.page-image.webtoon {
  width: 100%;
  height: auto;
}

/* Navigation zones */
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
  pointer-events: all;
  cursor: pointer;
  transition: background 0.2s ease;
}

/* Zone layouts */
.nav-zones.zones-edge {
  flex-direction: row;
}
.nav-zones.zones-edge .nav-zone.previous { flex: 0 0 15%; }
.nav-zones.zones-edge .nav-zone.menu { flex: 1; }
.nav-zones.zones-edge .nav-zone.next { flex: 0 0 15%; }

.nav-zones.zones-kindle {
  flex-direction: row;
}
.nav-zones.zones-kindle .nav-zone.previous { flex: 0 0 25%; }
.nav-zones.zones-kindle .nav-zone.menu { flex: 1; }
.nav-zones.zones-kindle .nav-zone.next { flex: 0 0 25%; }

.nav-zones.zones-split {
  flex-direction: row;
}
.nav-zones.zones-split .nav-zone.previous { flex: 1; }
.nav-zones.zones-split .nav-zone.next { flex: 1; }
.nav-zones.zones-split .nav-zone.menu { display: none; }

.nav-zones.zones-l-shape {
  flex-direction: column;
}
.nav-zones.zones-l-shape .nav-zone.previous { flex: 0 0 25%; width: 50%; }
.nav-zones.zones-l-shape .nav-zone.next { flex: 1; }
.nav-zones.zones-l-shape .nav-zone.menu { display: none; }

/* Hover effects for navigation zones */
.nav-zone:hover {
  background: rgba(255, 255, 255, 0.1);
}

/* Double page navigation */
.nav-zones.double {
  flex-direction: row;
}
.nav-zones.double .nav-zone.previous { flex: 0 0 20%; }
.nav-zones.double .nav-zone.menu { flex: 1; }
.nav-zones.double .nav-zone.next { flex: 0 0 20%; }

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