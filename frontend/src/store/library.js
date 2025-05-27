import { defineStore } from 'pinia'
import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

export const useLibraryStore = defineStore('library', {
  state: () => ({
    mangas: [],
    currentManga: null,
    loading: false,
    error: null
  }),

  actions: {
    async fetchLibrary() {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.get(`${API_BASE_URL}/api/library`)
        this.mangas = response.data.mangas
        console.log('📚 Biblioteca carregada:', response.data.message)
      } catch (error) {
        this.error = 'Erro ao carregar biblioteca'
        console.error('❌ Erro:', error)
      } finally {
        this.loading = false
      }
    },

    async fetchManga(mangaId) {
      this.loading = true
      this.error = null
      
      try {
        const response = await axios.get(`${API_BASE_URL}/api/manga/${mangaId}`)
        this.currentManga = response.data
        console.log('📖 Mangá carregado:', response.data.message)
      } catch (error) {
        this.error = 'Erro ao carregar mangá'
        console.error('❌ Erro:', error)
      } finally {
        this.loading = false
      }
    }
  }
})