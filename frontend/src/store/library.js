import { defineStore } from 'pinia'
import { libraryAPI, apiUtils } from '@/services/api'
import { formatError } from '@/utils/errorUtils'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

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
        return this.backendOnline
      } catch (error) {
        this.backendOnline = false
        console.error('Erro ao verificar backend:', error)
        return false
      }
    },

    // Limpar biblioteca no backend
    async clearBackendLibrary() {
      try {
        const response = await fetch(`${API_BASE_URL}/api/clear-library`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        })
        
        if (response.ok) {
          // Backend limpo com sucesso
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
      
      this.loading = true
      this.scanning = true
      this.error = null
      
      try {
        const formData = new FormData()
        formData.append('library_path', this.libraryPath)
        
        const response = await fetch(`${API_BASE_URL}/api/scan-library`, {
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
          
          this.saveLibraryConfig()
          
          return true
        } else {
          throw new Error(data.message || 'Erro ao escanear biblioteca')
        }
        
      } catch (error) {
        console.error('Erro no scan:', error)
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
        return { mangas: this.mangas }
      }
      
      if (this.scanning) return
      
      this.loading = true
      this.error = null
      
      try {
        // Carregando biblioteca do servidor...
        
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
        
        // Biblioteca carregada
        
        return data
        
      } catch (error) {
        this.error = formatError(error)
        console.error('Erro ao carregar biblioteca:', this.error)
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
        // Carregando mangá
        
        const response = await libraryAPI.getManga(mangaId)
        const data = response.data
        
        this.currentManga = data.manga || data
        
        // Mangá carregado
        return this.currentManga
        
      } catch (error) {
        this.error = formatError(error)
        console.error('Erro ao carregar mangá:', this.error)
        throw error
      } finally {
        this.loading = false
      }
    },

    // Atualizar biblioteca atual (força refresh)
    async refreshLibrary() {
      // Forçando atualização da biblioteca...
      
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
      // Limpando biblioteca completamente...
      
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
      
      // Biblioteca limpa completamente
    },

    // Configurar caminho da biblioteca
    async setLibraryPath(path) {
      
      try {
        // Validar caminho primeiro
        const validation = await this.validatePath(path)
        if (!validation.valid && !validation.is_valid) {
          throw new Error(validation.message)
        }
        
        // Configurar no backend
        const formData = new FormData()
        formData.append('library_path', path)
        
        const response = await fetch(`${API_BASE_URL}/api/set-library-path`, {
          method: 'POST',
          body: formData
        })
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }
        
        const data = await response.json()
        
        if (data.status === 'configured') {
          this.libraryPath = path
          this.isInitialized = true
          
          // Salvar no localStorage
          this.saveLibraryConfig()
          
          return true
        } else {
          throw new Error(data.message || 'Erro ao configurar biblioteca')
        }
        
      } catch (error) {
        console.error('Erro ao configurar biblioteca:', error)
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
          // Configuração carregada do localStorage
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
        
        // Configuração limpa do localStorage
      } catch (error) {
        console.warn('Erro ao limpar localStorage:', error)
      }
    },

    // Inicializar store (chamado uma vez)
    async initialize() {
      // Evitar múltiplas inicializações
      if (this.isInitialized) {
        // Store já inicializado, usando cache
        return
      }
      
      // Inicializando biblioteca store...
      
      // Verificar backend
      await this.checkBackendStatus()
      
      if (!this.backendOnline) {
        this.error = `Backend não está acessível. Verifique se está rodando em ${API_BASE_URL}`
        return
      }
      
      // Carregar configuração do localStorage
      const savedPath = this.loadLibraryConfig()
      
      // Se tem dados em cache válidos, usar eles
      if (savedPath && this.isCacheValid && this.mangas.length > 0) {
        // Usando dados em cache válidos
        this.isInitialized = true
        return
      }
      
      // Tentar carregar biblioteca atual
      try {
        await this.fetchLibrary()
        
        // Se carregou biblioteca vazia e tem caminho salvo, tentar reescanear
        if (this.mangas.length === 0 && savedPath) {
          // Tentando reescanear biblioteca salva
          try {
            await this.scanLibrary()
          } catch (error) {
            console.warn('Erro ao reescanear biblioteca salva:', error)
            this.clearLibraryConfig()
          }
        }
        
        this.isInitialized = true
      } catch (error) {
        console.error('Erro na inicialização:', error)
        this.error = 'Erro ao inicializar biblioteca'
      }
    },
    
    // Validar caminho de biblioteca
    async validatePath(path) {
      try {
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
        const data = response.data
        
        // Garantir compatibilidade de campos
        return {
          valid: data.is_valid,
          is_valid: data.is_valid,
          message: data.message,
          path: data.path
        }
        
      } catch (error) {
        console.error('Erro na validação:', error)
        return {
          valid: false,
          message: formatError(error)
        }
      }
    },

    // Preview dos mangás que seriam encontrados
    async previewLibrary(path) {
      try {
        // Fazendo preview da biblioteca
        
        const response = await fetch(`${API_BASE_URL}/api/preview-library?path=${encodeURIComponent(path)}`)
        const data = await response.json()
        
        return {
          valid: data.valid,
          mangas: data.mangas || [],
          totalFound: data.total_found || 0,
          message: data.message
        }
        
      } catch (error) {
        console.error('Erro no preview:', error)
        return {
          valid: false,
          mangas: [],
          totalFound: 0,
          message: formatError(error)
        }
      }
    }
  }
})