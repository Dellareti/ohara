import { defineStore } from 'pinia'
import { libraryAPI, apiUtils } from '@/services/api'

export const useLibraryStore = defineStore('library', {
  state: () => ({
    // Dados da biblioteca
    mangas: [],
    currentManga: null,
    libraryPath: null,
    totalMangas: 0,
    totalChapters: 0,
    totalPages: 0,
    lastUpdated: null,
    
    // Estados de carregamento
    loading: false,
    scanning: false,
    error: null,
    
    // Configurações
    backendOnline: false,
    
    // Cache control
    lastLoadTime: null,
    cacheTimeout: 5 * 60 * 1000, // 5 minutos
    isInitialized: false
  }),

  getters: {
    // Mangás organizados por ordem alfabética
    sortedMangas: (state) => {
      return [...state.mangas].sort((a, b) => a.title.localeCompare(b.title))
    },
    
    // Estatísticas da biblioteca
    libraryStats: (state) => ({
      totalMangas: state.totalMangas,
      totalChapters: state.totalChapters,
      totalPages: state.totalPages,
      averageChaptersPerManga: state.totalMangas > 0 ? 
        Math.round(state.totalChapters / state.totalMangas) : 0,
      averagePagesPerChapter: state.totalChapters > 0 ? 
        Math.round(state.totalPages / state.totalChapters) : 0
    }),
    
    // Status da biblioteca
    libraryStatus: (state) => {
      if (state.scanning) return 'scanning'
      if (state.loading) return 'loading'
      if (state.error) return 'error'
      if (!state.libraryPath) return 'not-configured'
      if (state.mangas.length === 0) return 'empty'
      return 'ready'
    },
    
    // Check if cache is valid
    isCacheValid: (state) => {
      if (!state.lastLoadTime) return false
      return (Date.now() - state.lastLoadTime) < state.cacheTimeout
    },
    
    // Verificar se biblioteca está configurada
    isLibraryConfigured: (state) => {
      return state.libraryPath && state.libraryPath.trim().length > 0
    }
  },

  actions: {
    // Verificar se o backend está online
    async checkBackendStatus() {
      try {
        this.backendOnline = await apiUtils.isBackendOnline()
        console.log('🌐 Backend status:', this.backendOnline ? 'Online' : 'Offline')
        return this.backendOnline
      } catch (error) {
        this.backendOnline = false
        console.error('❌ Erro ao verificar backend:', error)
        return false
      }
    },

    // Limpar biblioteca no backend
    async clearBackendLibrary() {
      try {
        console.log('🧹 Limpando biblioteca no backend...')
        const response = await fetch('http://localhost:8000/api/clear-library', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        })
        
        if (response.ok) {
          console.log('Backend limpo com sucesso')
        } else {
          console.warn('Erro ao limpar backend:', response.status)
        }
      } catch (error) {
        console.warn('Erro na comunicação com backend:', error.message)
      }
    },

    // Escanear biblioteca
    async scanLibrary() {
      if (!this.libraryPath) {
        throw new Error('Caminho da biblioteca não configurado')
      }
      
      console.log('Escaneando biblioteca:', this.libraryPath)
      this.loading = true
      this.scanning = true
      this.error = null
      
      try {
        // Usar POST com FormData como o backend espera
        const formData = new FormData()
        formData.append('library_path', this.libraryPath)
        
        const response = await fetch('http://localhost:8000/api/scan-library', {
          method: 'POST',
          body: formData
        })
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }
        
        const data = await response.json()
        
        if (data.library) {
          this.mangas = data.library.mangas || []
          this.totalMangas = data.library.total_mangas || this.mangas.length
          this.totalChapters = data.library.total_chapters || 0
          this.totalPages = data.library.total_pages || 0
          this.lastUpdated = new Date(data.library.last_updated || Date.now())
          this.lastLoadTime = Date.now()
          
          // Salvar configuração no localStorage
          this.saveLibraryConfig()
          
          console.log(`📚 Biblioteca escaneada: ${this.mangas.length} mangás`)
          console.log('📊 Response message:', data.message)
          return true
        } else {
          throw new Error(data.message || 'Erro ao escanear biblioteca')
        }
        
      } catch (error) {
        console.error('❌ Erro no scan:', error)
        this.error = error.message
        throw error
      } finally {
        this.loading = false
        this.scanning = false
      }
    },

    // Carregar biblioteca atual
    async fetchLibrary(forceRefresh = false) {
      // Se já foi inicializado e cache é válido, não recarregar
      if (this.isInitialized && !forceRefresh && this.isCacheValid && this.mangas.length > 0) {
        console.log('📋 Cache válido, usando dados em memória')
        return { mangas: this.mangas }
      }
      
      if (this.scanning) return // Evitar chamadas simultâneas
      
      this.loading = true
      this.error = null
      
      try {
        console.log('📚 Carregando biblioteca do servidor...')
        
        const response = await libraryAPI.getLibrary()
        const data = response.data
        
        // Atualizar estado
        this.mangas = data.mangas || []
        this.totalMangas = data.total_mangas || data.mangas?.length || 0
        this.totalChapters = data.total_chapters || 0
        this.totalPages = data.total_pages || 0
        this.lastLoadTime = Date.now()
        this.isInitialized = true
        
        if (data.last_updated) {
          this.lastUpdated = new Date(data.last_updated)
        }
        
        if (data.scanned_path) {
          this.libraryPath = data.scanned_path
        }
        
        // Salvar cache se há dados reais
        if (this.mangas.length > 0) {
          this.saveLibraryConfig()
        }
        
        console.log('Biblioteca carregada:', {
          mangas: this.totalMangas,
          fromCache: false
        })
        
        return data
        
      } catch (error) {
        this.error = apiUtils.formatError(error)
        console.error('❌ Erro ao carregar biblioteca:', this.error)
        throw error
      } finally {
        this.loading = false
      }
    },

    // Carregar mangá específico
    async fetchManga(mangaId) {
      this.loading = true
      this.error = null
      
      try {
        console.log('📖 Carregando mangá:', mangaId)
        
        const response = await libraryAPI.getManga(mangaId)
        const data = response.data
        
        this.currentManga = data.manga || data
        
        console.log('Mangá carregado:', this.currentManga.title)
        return this.currentManga
        
      } catch (error) {
        this.error = apiUtils.formatError(error)
        console.error('❌ Erro ao carregar mangá:', this.error)
        throw error
      } finally {
        this.loading = false
      }
    },

    // Atualizar biblioteca atual (força refresh)
    async refreshLibrary() {
      console.log('🔄 Forçando atualização da biblioteca...')
      
      if (this.libraryPath) {
        // Se tem biblioteca configurada, fazer scan
        return await this.scanLibrary()
      } else {
        // Se não tem biblioteca, tentar carregar do servidor
        return await this.fetchLibrary(true)
      }
    },

    // Buscar mangás
    searchMangas(query) {
      if (!query || typeof query !== 'string') {
        return this.mangas
      }
      
      const searchTerm = query.toLowerCase().trim()
      return this.mangas.filter(manga => 
        manga.title.toLowerCase().includes(searchTerm) ||
        manga.id.toLowerCase().includes(searchTerm) ||
        (manga.author && manga.author.toLowerCase().includes(searchTerm))
      )
    },

    // Limpar biblioteca completamente
    async clearLibrary() {
      console.log('🗑️ Limpando biblioteca completamente...')
      
      // 1. Limpar estado local
      this.mangas = []
      this.currentManga = null
      this.libraryPath = null
      this.totalMangas = 0
      this.totalChapters = 0
      this.totalPages = 0
      this.lastUpdated = null
      this.lastLoadTime = null
      this.isInitialized = false
      this.error = null
      
      // 2. Limpar localStorage
      this.clearLibraryConfig()
      
      // 3. Notificar backend para limpar cache
      await this.clearBackendLibrary()
      
      console.log('Biblioteca limpa completamente')
    },

    // Configurar caminho da biblioteca
    async setLibraryPath(path) {
      console.log('Configurando caminho da biblioteca:', path)
      
      try {
        // Validar caminho primeiro
        const validation = await this.validatePath(path)
        if (!validation.valid) {
          throw new Error(validation.message)
        }
        
        // Configurar no backend
        const response = await fetch('http://localhost:8000/api/set-library-path', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ path })
        })
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }
        
        const data = await response.json()
        
        if (data.success) {
          this.libraryPath = path
          this.isInitialized = true
          
          // Salvar no localStorage
          this.saveLibraryConfig()
          
          console.log('Biblioteca configurada:', data.message)
          return true
        } else {
          throw new Error(data.message)
        }
        
      } catch (error) {
        console.error('❌ Erro ao configurar biblioteca:', error)
        throw error
      }
    },

    // Salvar configuração no localStorage
    saveLibraryConfig() {
      try {
        if (this.libraryPath) {
          localStorage.setItem('ohara_library_path', this.libraryPath)
          localStorage.setItem('ohara_last_load', this.lastLoadTime?.toString() || '')
          localStorage.setItem('ohara_last_updated', this.lastUpdated?.toISOString() || '')
          console.log('💾 Configuração salva no localStorage')
        }
      } catch (error) {
        console.warn('Erro ao salvar no localStorage:', error)
      }
    },

    // Carregar configuração do localStorage
    loadLibraryConfig() {
      try {
        const savedPath = localStorage.getItem('ohara_library_path')
        const savedLastLoad = localStorage.getItem('ohara_last_load')
        const savedLastUpdated = localStorage.getItem('ohara_last_updated')
        
        if (savedPath) {
          this.libraryPath = savedPath
          if (savedLastLoad) {
            this.lastLoadTime = parseInt(savedLastLoad)
          }
          if (savedLastUpdated) {
            this.lastUpdated = new Date(savedLastUpdated)
          }
          console.log('📂 Configuração carregada do localStorage:', savedPath)
          return savedPath
        }
      } catch (error) {
        console.warn('Erro ao carregar do localStorage:', error)
      }
      
      return null
    },

    // Limpar configuração do localStorage
    clearLibraryConfig() {
      try {
        const keysToRemove = [
          'ohara_library_path',
          'ohara_last_load', 
          'ohara_last_updated',
          'ohara_mangas_cache',
          'ohara_settings'
        ]
        
        keysToRemove.forEach(key => {
          localStorage.removeItem(key)
        })
        
        console.log('🗑️ Configuração limpa do localStorage')
      } catch (error) {
        console.warn('Erro ao limpar localStorage:', error)
      }
    },

    // Inicializar store (chamado uma vez)
    async initialize() {
      // Evitar múltiplas inicializações
      if (this.isInitialized) {
        console.log('🛑 Store já inicializado, usando cache')
        return
      }
      
      console.log('🚀 Inicializando biblioteca store...')
      
      // Verificar backend
      await this.checkBackendStatus()
      
      if (!this.backendOnline) {
        this.error = 'Backend não está acessível. Verifique se está rodando em http://localhost:8000'
        return
      }
      
      // Carregar configuração do localStorage
      const savedPath = this.loadLibraryConfig()
      
      // Se tem dados em cache válidos, usar eles
      if (savedPath && this.isCacheValid && this.mangas.length > 0) {
        console.log('📋 Usando dados em cache válidos')
        this.isInitialized = true
        return
      }
      
      // Tentar carregar biblioteca atual
      try {
        await this.fetchLibrary()
        
        // Se carregou biblioteca vazia e tem caminho salvo, tentar reescanear
        if (this.mangas.length === 0 && savedPath) {
          console.log('📂 Tentando reescanear biblioteca salva:', savedPath)
          try {
            await this.scanLibrary()
          } catch (error) {
            console.warn('Erro ao reescanear biblioteca salva:', error)
            this.clearLibraryConfig()
          }
        }
        
        this.isInitialized = true
      } catch (error) {
        console.error('❌ Erro na inicialização:', error)
        this.error = 'Erro ao inicializar biblioteca'
      }
    },
    
    // Validar caminho de biblioteca
    async validatePath(path) {
      try {
        console.log('Validando caminho:', path)
        
        // Validação local primeiro
        const localValidation = apiUtils.validatePathFormat(path)
        if (!localValidation.valid) {
          return {
            valid: false,
            message: localValidation.message
          }
        }
        
        // Validação no servidor
        const response = await libraryAPI.validatePath(path)
        return response.data
        
      } catch (error) {
        console.error('❌ Erro na validação:', error)
        return {
          valid: false,
          message: apiUtils.formatError(error)
        }
      }
    },

    // Preview dos mangás que seriam encontrados
    async previewLibrary(path) {
      try {
        console.log('Fazendo preview da biblioteca:', path)
        
        const response = await fetch(`http://localhost:8000/api/preview-library?path=${encodeURIComponent(path)}`)
        const data = await response.json()
        
        return {
          valid: data.valid,
          mangas: data.mangas || [],
          totalFound: data.total_found || 0,
          message: data.message
        }
        
      } catch (error) {
        console.error('❌ Erro no preview:', error)
        return {
          valid: false,
          mangas: [],
          totalFound: 0,
          message: apiUtils.formatError(error)
        }
      }
    }
  }
})