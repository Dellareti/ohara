<template>
  <div class="library-view">
    <div class="library-header">
      <h1>🏴‍☠️ Biblioteca Ohara</h1>
      <p>Preserve suas histórias favoritas</p>
      <button @click="testAPI" class="test-btn">🧪 Testar API</button>
    </div>

    <!-- Loading -->
    <div v-if="libraryStore.loading" class="loading">
      <div class="spinner"></div>
      <p>Carregando biblioteca...</p>
    </div>

    <!-- Error -->
    <div v-if="libraryStore.error" class="error">
      <p>❌ {{ libraryStore.error }}</p>
      <button @click="loadLibrary">🔄 Tentar novamente</button>
    </div>

    <!-- Library Grid -->
    <div v-if="!libraryStore.loading && !libraryStore.error" class="manga-grid">
      <div 
        v-for="manga in libraryStore.mangas" 
        :key="manga.id"
        class="manga-card"
        @click="selectManga(manga)"
      >
        <div class="manga-thumbnail">
          <div class="placeholder-thumbnail">📚</div>
        </div>
        <div class="manga-info">
          <h3>{{ manga.title }}</h3>
          <p>{{ manga.chapter_count }} capítulos</p>
          <span class="last-chapter">{{ manga.last_chapter }}</span>
        </div>
      </div>
    </div>

    <!-- API Test Results -->
    <div v-if="testResult" class="test-result">
      <h3>🧪 Resultado do Teste:</h3>
      <pre>{{ testResult }}</pre>
    </div>
  </div>
</template>

<script>
import { onMounted, ref } from 'vue'
import { useLibraryStore } from '@/store/library'
import { libraryAPI } from '@/services/api'

export default {
  name: 'LibraryView',
  setup() {
    const libraryStore = useLibraryStore()
    const testResult = ref(null)

    const loadLibrary = async () => {
      await libraryStore.fetchLibrary()
    }

    const selectManga = (manga) => {
      console.log('📖 Mangá selecionado:', manga.title)
      alert(`Você selecionou: ${manga.title}\n\n(Em breve: navegação para detalhes do mangá)`)
    }

    const testAPI = async () => {
      try {
        const response = await libraryAPI.test()
        testResult.value = JSON.stringify(response.data, null, 2)
        console.log('🎉 Teste API bem-sucedido!')
      } catch (error) {
        testResult.value = `Erro: ${error.message}`
        console.error('❌ Erro no teste API:', error)
      }
    }

    onMounted(() => {
      loadLibrary()
    })

    return {
      libraryStore,
      testResult,
      loadLibrary,
      selectManga,
      testAPI
    }
  }
}
</script>

<style scoped>
.library-view {
  padding: 20px;
  min-height: 100vh;
  background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
  color: white;
}

.library-header {
  text-align: center;
  margin-bottom: 40px;
}

.library-header h1 {
  font-size: 3rem;
  margin-bottom: 10px;
  background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.library-header p {
  font-size: 1.2rem;
  opacity: 0.8;
  margin-bottom: 20px;
}

.test-btn {
  background: linear-gradient(45deg, #4ecdc4, #44a08d);
  border: none;
  padding: 10px 20px;
  border-radius: 25px;
  color: white;
  cursor: pointer;
  font-size: 1rem;
  transition: transform 0.2s;
}

.test-btn:hover {
  transform: scale(1.05);
}

.loading {
  text-align: center;
  padding: 60px 20px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255,255,255,0.3);
  border-radius: 50%;
  border-top: 4px solid #4ecdc4;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error {
  text-align: center;
  padding: 40px;
  background: rgba(255, 107, 107, 0.1);
  border-radius: 10px;
  margin: 20px 0;
}

.error button {
  background: #ff6b6b;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  color: white;
  cursor: pointer;
  margin-top: 10px;
}

.manga-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.manga-card {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  padding: 20px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
  cursor: pointer;
}

.manga-card:hover {
  transform: translateY(-5px);
  background: rgba(255, 255, 255, 0.15);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.manga-thumbnail {
  text-align: center;
  margin-bottom: 15px;
}

.placeholder-thumbnail {
  width: 100%;
  height: 200px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 4rem;
}

.manga-info h3 {
  margin: 10px 0;
  color: #4ecdc4;
}

.manga-info p {
  margin: 5px 0;
  opacity: 0.8;
}

.last-chapter {
  font-size: 0.9rem;
  color: #ff6b6b;
}

.test-result {
  margin-top: 30px;
  padding: 20px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 10px;
  border-left: 4px solid #4ecdc4;
}

.test-result h3 {
  color: #4ecdc4;
  margin-bottom: 10px;
}

.test-result pre {
  background: rgba(0, 0, 0, 0.5);
  padding: 15px;
  border-radius: 5px;
  overflow-x: auto;
  white-space: pre-wrap;
}
</style>