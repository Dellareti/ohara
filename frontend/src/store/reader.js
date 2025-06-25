import { defineStore } from 'pinia'
import axios from 'axios'
import { formatError } from '@/utils/errorUtils'

const API_BASE_URL = 'http://localhost:8000'

export const useReaderStore = defineStore('reader', {
  state: () => ({
    // Dados do capítulo atual
    currentManga: null,
    currentChapter: null,
    currentPage: 0,
    totalPages: 0,
    
    // Estados de carregamento
    loading: false,
    error: null,
    
    // Configurações de leitura
    readingMode: 'single', // single, double, vertical, webtoon
    fitMode: 'width', // width, height, screen, original
    readingDirection: 'rtl', // ltr, rtl (right-to-left para mangás japoneses)
    touchZones: 'edge', // edge, kindle, l-shape, split
    theme: 'dark', // dark, light, sepia
    autoScrollDelay: 0, // segundos (0 = desabilitado)
    
    // Interface
    isFullscreen: false,
    hideControls: false,
    showSettings: false,
    
    navigation: {
      previousChapter: null,
      nextChapter: null,
      chapterIndex: { current: 0, total: 0 },
      allChapters: [] 
    },
    
    // Progresso
    readingProgress: {},
    readingStartTime: null,
    
    // Cache e Performance
    preloadedPages: new Set(),
    pageCache: new Map(),
    maxCacheSize: 50,
    
    // Internal
    _saveProgressTimeout: null
  }),

  getters: {
    // Página atual
    currentPageData: (state) => {
      if (!state.currentChapter?.chapter?.pages || state.currentPage < 0) return null
      return state.currentChapter.chapter.pages[state.currentPage]
    },
    
    // Próxima página (para modo duplo)
    nextPageData: (state) => {
      if (!state.currentChapter?.chapter?.pages || state.currentPage >= state.totalPages - 1) return null
      return state.currentChapter.chapter.pages[state.currentPage + 1]
    },
    
    // Páginas visíveis (para modo vertical/webtoon)
    visiblePages: (state) => {
      if (!state.currentChapter?.chapter?.pages) return []
      
      if (state.readingMode === 'vertical' || state.readingMode === 'webtoon') {
        return state.currentChapter.chapter.pages
      }
      
      const pages = [state.currentChapter.chapter.pages[state.currentPage]]
      if (state.readingMode === 'double' && state.currentPage < state.totalPages - 1) {
        pages.push(state.currentChapter.chapter.pages[state.currentPage + 1])
      }
      
      return pages.filter(Boolean)
    },
    
    // Progresso percentual
    progressPercentage: (state) => {
      if (state.totalPages === 0) return 0
      return Number(((state.currentPage / Math.max(state.totalPages - 1, 1)) * 100).toFixed(2))
    },
    
    // Verificar navegação baseada na lista completa
    hasPreviousChapter: (state) => {
      // Verificando capítulo anterior
      return state.navigation.previousChapter !== null
    },
    
    hasNextChapter: (state) => {
      // Verificando próximo capítulo
      return state.navigation.nextChapter !== null
    },
    
    // Tempo de leitura atual
    currentReadingTime: (state) => {
      if (!state.readingStartTime) return 0
      return Math.floor((Date.now() - state.readingStartTime) / 1000)
    }
  },

  actions: {
    // Carregar capítulo
    async loadChapter(mangaId, chapterId) {
      this.loading = true
      this.error = null
      
      try {
        // Carregando capítulo
        
        // 1. Carregar dados do capítulo
        const response = await axios.get(`${API_BASE_URL}/api/manga/${mangaId}/chapter/${chapterId}`)
        const data = response.data
        
        // Dados recebidos do backend
        
        // 2. Atualizar estado básico
        this.currentManga = data.manga
        this.currentChapter = data
        this.totalPages = data.chapter.pages.length
        
        // 3. Carregar lista completa de capítulos para navegação
        await this.loadChapterNavigation(mangaId, chapterId)
        
        // 4. Carregar progresso salvo
        await this.loadChapterProgress(mangaId, chapterId)
        
        // 5. Iniciar timer de leitura
        this.readingStartTime = Date.now()
        
        // 6. Pré-carregar páginas
        this.preloadPages()
        
        // Capítulo carregado
        // Navegação final
        
        return data
        
      } catch (error) {
        this.error = formatError(error)
        console.error('❌ Erro ao carregar capítulo:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    // Método para carregar navegação entre capítulos
    async loadChapterNavigation(mangaId, currentChapterId) {
      try {
        // Carregando navegação
        
        // Buscar lista de todos os capítulos do mangá
        const chaptersResponse = await axios.get(`${API_BASE_URL}/api/manga/${mangaId}/chapters`)
        const chaptersData = chaptersResponse.data
        
        // Lista de capítulos recebida
        
        if (!chaptersData.chapters || !Array.isArray(chaptersData.chapters)) {
          console.warn('Lista de capítulos inválida')
          this.navigation = {
            previousChapter: null,
            nextChapter: null,
            chapterIndex: { current: 0, total: 0 },
            allChapters: []
          }
          return
        }
        
        const allChapters = chaptersData.chapters
        this.navigation.allChapters = allChapters
        
        // Encontrar índice do capítulo atual
        const currentIndex = allChapters.findIndex(ch => 
          ch.id === currentChapterId || 
          ch.id.includes(currentChapterId) ||
          currentChapterId.includes(ch.id)
        )
        
        // Capítulo atual encontrado no índice
        // Procurando por ID
        // IDs disponíveis
        
        if (currentIndex === -1) {
          console.warn('Capítulo atual não encontrado na lista')
          // Tentar busca mais flexível
          const flexibleIndex = this.findChapterFlexible(allChapters, currentChapterId)
          if (flexibleIndex !== -1) {
            // Capítulo encontrado com busca flexível
            this.setupNavigation(allChapters, flexibleIndex)
          } else {
            this.navigation = {
              previousChapter: null,
              nextChapter: null,
              chapterIndex: { current: 0, total: allChapters.length },
              allChapters: allChapters
            }
          }
          return
        }
        
        this.setupNavigation(allChapters, currentIndex)
        
      } catch (error) {
        console.error('❌ Erro ao carregar navegação:', error)
        this.navigation = {
          previousChapter: null,
          nextChapter: null,
          chapterIndex: { current: 0, total: 0 },
          allChapters: []
        }
      }
    },

    // Busca flexível para IDs de capítulos
    findChapterFlexible(chapters, targetId) {
      // Busca flexível
      
      // Tentar várias estratégias de busca
      const strategies = [
        // 1. Busca exata
        (id) => chapters.findIndex(ch => ch.id === id),
        
        // 2. Busca parcial (contém)
        (id) => chapters.findIndex(ch => ch.id.includes(id) || id.includes(ch.id)),
        
        // 3. Busca por número de capítulo extraído
        (id) => {
          const match = id.match(/(\d+(?:\.\d+)?)/);
          if (match) {
            const number = parseFloat(match[1]);
            return chapters.findIndex(ch => ch.number === number);
          }
          return -1;
        },
        
        // 4. Busca por nome normalizado
        (id) => {
          const normalizedId = id.toLowerCase().replace(/[^a-z0-9]/g, '');
          return chapters.findIndex(ch => {
            const normalizedChId = ch.id.toLowerCase().replace(/[^a-z0-9]/g, '');
            return normalizedChId.includes(normalizedId) || normalizedId.includes(normalizedChId);
          });
        }
      ];
      
      for (let i = 0; i < strategies.length; i++) {
        const index = strategies[i](targetId);
        if (index !== -1) {
          // Estratégia encontrou capítulo;
          return index;
        }
      }
      
      console.warn('❌ Nenhuma estratégia encontrou o capítulo');
      return -1;
    },

    // Configurar navegação baseada no índice
    setupNavigation(allChapters, currentIndex) {
      const total = allChapters.length;
      
      // Capítulo anterior (índice maior, pois lista está em ordem decrescente)
      const previousChapter = currentIndex < total - 1 ? allChapters[currentIndex + 1] : null;
      
      // Próximo capítulo (índice menor)
      const nextChapter = currentIndex > 0 ? allChapters[currentIndex - 1] : null;
      
      this.navigation = {
        previousChapter: previousChapter ? {
          id: previousChapter.id,
          name: previousChapter.name,
          number: previousChapter.number
        } : null,
        nextChapter: nextChapter ? {
          id: nextChapter.id,
          name: nextChapter.name,
          number: nextChapter.number
        } : null,
        chapterIndex: {
          current: currentIndex + 1,
          total: total
        },
        allChapters: allChapters
      };
      
      // Navegação configurada;
    },

    // Carregar progresso do capítulo
    async loadChapterProgress(mangaId, chapterId) {
      try {
        const response = await axios.get(`${API_BASE_URL}/api/progress/${mangaId}/${chapterId}`)
        const progressData = response.data.progress
        
        if (progressData) {
          this.currentPage = progressData.current_page || 0
          this.readingProgress[chapterId] = progressData
        } else {
          this.currentPage = 0
        }
        
      } catch (error) {
        console.warn('Erro ao carregar progresso:', error)
        this.currentPage = 0
      }
    },

    // Salvar progresso
    async saveProgress(mangaId, chapterId) {
      if (!mangaId || !chapterId) return
      
      try {
        const readingTime = this.currentReadingTime
        
        const response = await axios.post(`${API_BASE_URL}/api/progress/${mangaId}/${chapterId}`, {
          current_page: this.currentPage,
          total_pages: this.totalPages,
          reading_time_seconds: readingTime
        })
        
        // Atualizar cache local
        this.readingProgress[chapterId] = response.data.progress
                
      } catch (error) {
        console.error('Erro ao salvar progresso:', error)
      }
    },

    // Navegação de páginas
    nextPage() {
      if (this.currentPage < this.totalPages - 1) {
        this.currentPage++
        this.saveProgressDebounced()
        this.preloadPages()
        return true
      }
      return false // Chegou ao final
    },

    previousPage() {
      if (this.currentPage > 0) {
        this.currentPage--
        this.saveProgressDebounced()
        return true
      }
      return false // Chegou ao início
    },

    // Ir para página específica
    goToPage(pageNumber) {
      const page = Math.max(0, Math.min(pageNumber, this.totalPages - 1))
      this.currentPage = page
      this.saveProgressDebounced()
      this.preloadPages()
    },

    // Navegar para porcentagem específica
    seekToProgress(percentage) {
      const targetPage = Math.floor((percentage / 100) * this.totalPages)
      this.goToPage(targetPage)
    },

    // Pré-carregar páginas
    preloadPages() {
      if (!this.currentChapter?.chapter?.pages) return
      
      // Pré-carregar próximas 5 páginas
      const startIndex = this.currentPage
      const endIndex = Math.min(this.totalPages, this.currentPage + 5)
      
      for (let i = startIndex; i < endIndex; i++) {
        const page = this.currentChapter.chapter.pages[i]
        if (page && !this.preloadedPages.has(page.url)) {
          this.preloadImage(page.url)
          this.preloadedPages.add(page.url)
        }
      }
      
      // Limpar cache se muito grande
      if (this.preloadedPages.size > this.maxCacheSize) {
        const oldPages = Array.from(this.preloadedPages).slice(0, 10)
        oldPages.forEach(url => {
          this.preloadedPages.delete(url)
          this.pageCache.delete(url)
        })
      }
    },

    // Pré-carregar imagem
    preloadImage(url) {
      return new Promise((resolve, reject) => {
        if (this.pageCache.has(url)) {
          resolve(this.pageCache.get(url))
          return
        }
        
        const img = new Image()
        img.onload = () => {
          this.pageCache.set(url, img)
          resolve(img)
        }
        img.onerror = reject
        img.src = url
      })
    },

    // Configurações de leitura
    updateReadingSettings(settings) {
      Object.assign(this, settings)
      this.saveSettings()
    },

    // Salvar configurações no localStorage
    saveSettings() {
      const settings = {
        readingMode: this.readingMode,
        fitMode: this.fitMode,
        readingDirection: this.readingDirection,
        touchZones: this.touchZones,
        theme: this.theme,
        autoScrollDelay: this.autoScrollDelay
      }
      
      localStorage.setItem('ohara_reader_settings', JSON.stringify(settings))
    },

    // Carregar configurações do localStorage
    loadSettings() {
      try {
        const saved = localStorage.getItem('ohara_reader_settings')
        if (saved) {
          const settings = JSON.parse(saved)
          Object.assign(this, settings)
        }
      } catch (error) {
        console.warn('Erro ao carregar configurações:', error)
      }
    },

    // Reset configurações
    resetSettings() {
      this.readingMode = 'single'
      this.fitMode = 'width'
      this.readingDirection = 'rtl'
      this.touchZones = 'edge'
      this.theme = 'dark'
      this.autoScrollDelay = 0
      this.saveSettings()
    },

    // Controles de interface
    toggleFullscreen() {
      this.isFullscreen = !this.isFullscreen
    },

    toggleControls() {
      this.hideControls = !this.hideControls
    },

    toggleSettings() {
      this.showSettings = !this.showSettings
    },

    // Limpar dados do leitor
    clearReader() {
      this.currentManga = null
      this.currentChapter = null
      this.currentPage = 0
      this.totalPages = 0
      this.navigation = {
        previousChapter: null,
        nextChapter: null,
        chapterIndex: { current: 0, total: 0 },
        allChapters: []
      }
      this.readingStartTime = null
      this.preloadedPages.clear()
      this.pageCache.clear()
    },

    saveProgressDebounced() {
      if (this._saveProgressTimeout) {
        clearTimeout(this._saveProgressTimeout)
      }
      
      this._saveProgressTimeout = setTimeout(() => {
        if (this.currentManga && this.currentChapter) {
          this.saveProgress(this.currentManga.id, this.currentChapter.chapter.id)
        }
      }, 1000)
    }
  }
})