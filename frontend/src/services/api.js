import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // Aumentado para 30s (escaneamento pode demorar)
  headers: {
    'Content-Type': 'application/json',
  }
})

api.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    console.error('API Request Error:', error)
    return Promise.reject(error)
  }
)

api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    console.error('API Response Error:', error.response?.status, error.message)
    return Promise.reject(error)
  }
)

export const libraryAPI = {
  // Escanear biblioteca - CORRIGIDO para caminhos com espaços
  scanLibrary: async (libraryPath) => {
    try {
      
      // Usar FormData para encoding correto de caminhos com espaços
      const formData = new FormData()
      formData.append('library_path', libraryPath)
      
      const response = await axios.post(`${API_BASE_URL}/api/scan-library`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        timeout: 60000 // 60 segundos para escaneamento
      })
      
      return response
    } catch (error) {
      console.error('Erro ao escanear biblioteca:', error)
      throw error
    }
  },

  // Outras APIs
  getLibrary: () => api.get('/api/library'),
  getManga: (mangaId) => api.get(`/api/manga/${mangaId}`),
  healthCheck: () => api.get('/health'),
  test: () => api.get('/api/test'),
  validatePath: (path) => api.get('/api/validate-path', { params: { path } }),
  clearLibrary: () => api.post('/api/clear-library')
}

export const apiUtils = {
  // Validação melhorada para caminhos
  validatePathFormat: (path) => {
    if (!path || typeof path !== 'string') {
      return { 
        valid: false, 
        message: 'Caminho deve ser uma string válida' 
      }
    }

    const trimmedPath = path.trim()
    
    if (trimmedPath.length === 0) {
      return { 
        valid: false, 
        message: 'Caminho não pode estar vazio' 
      }
    }

    // Validação mais flexível para diferentes sistemas operacionais
    const isWindows = /^[A-Za-z]:\\/.test(trimmedPath)
    const isUnix = trimmedPath.startsWith('/')
    const isRelative = !isWindows && !isUnix

    if (!isWindows && !isUnix && !isRelative) {
      return {
        valid: false,
        message: 'Formato de caminho inválido. Use /home/user/Mangas (Linux/Mac) ou C:\\Mangas (Windows)'
      }
    }

    // Verificar caracteres proibidos (mais restritivo no Windows)
    const forbiddenChars = isWindows 
      ? /[<>"|?*]/ // Windows: não permite estes caracteres
      : /[\0]/ // Unix: apenas null byte é proibido

    if (forbiddenChars.test(trimmedPath)) {
      return {
        valid: false,
        message: `Caminho contém caracteres inválidos: ${isWindows ? '<>"|?*' : 'caracteres de controle'}`
      }
    }

    // Verificar comprimento (Windows tem limite de 260 caracteres)
    if (isWindows && trimmedPath.length > 260) {
      return {
        valid: false,
        message: 'Caminho muito longo (máximo 260 caracteres no Windows)'
      }
    }

    if (trimmedPath.length > 4096) {
      return {
        valid: false,
        message: 'Caminho muito longo (máximo 4096 caracteres)'
      }
    }

    return { 
      valid: true, 
      message: 'Caminho válido',
      normalized: trimmedPath
    }
  },

  // Verificar se backend está online
  isBackendOnline: async () => {
    try {
      const response = await api.get('/api/test', { timeout: 5000 })
      return response.status === 200
    } catch (error) {
      return false
    }
  },

  // Formatar erros de API
  formatError: (error) => {
    if (error.response) {
      // Erro de resposta do servidor
      const data = error.response.data
      
      if (data && typeof data === 'object') {
        return data.message || data.detail || `Erro ${error.response.status}`
      }
      
      return `Erro ${error.response.status}: ${error.response.statusText}`
    } else if (error.request) {
      // Erro de rede
      return 'Erro de conexão com o servidor. Verifique se o backend está rodando.'
    } else {
      // Erro na configuração da requisição
      return error.message || 'Erro desconhecido'
    }
  }
}

export default api