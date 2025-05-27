<template>
  <div class="library-simple">
    <h1>🏴‍☠️ Ohara - Biblioteca</h1>
    <p>Versão de teste simples</p>
    
    <div class="test-section">
      <button @click="testBackend" class="test-btn">🧪 Testar Backend</button>
      <div v-if="testResult" class="result">
        <h3>Resultado:</h3>
        <pre>{{ testResult }}</pre>
      </div>
    </div>

    <div class="mock-manga">
      <h2>📚 Mangás Mock:</h2>
      <div class="manga-list">
        <div class="manga-item">📖 One Piece</div>
        <div class="manga-item">📖 Naruto</div>
        <div class="manga-item">📖 Attack on Titan</div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'

export default {
  name: 'LibraryViewSimple',
  setup() {
    const testResult = ref(null)

    const testBackend = async () => {
      try {
        console.log('🔄 Testando backend...')
        const response = await fetch('http://localhost:8000/api/test')
        const data = await response.json()
        testResult.value = JSON.stringify(data, null, 2)
        console.log('✅ Backend funcionando:', data)
      } catch (error) {
        testResult.value = `❌ Erro: ${error.message}`
        console.error('❌ Erro ao testar backend:', error)
      }
    }

    return {
      testResult,
      testBackend
    }
  }
}
</script>

<style scoped>
.library-simple {
  padding: 20px;
  min-height: 100vh;
  background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
  color: white;
  font-family: Arial, sans-serif;
}

h1 {
  text-align: center;
  font-size: 2.5rem;
  margin-bottom: 20px;
  background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.test-section {
  margin: 30px 0;
  text-align: center;
}

.test-btn {
  background: linear-gradient(45deg, #4ecdc4, #44a08d);
  border: none;
  padding: 12px 24px;
  border-radius: 25px;
  color: white;
  cursor: pointer;
  font-size: 1rem;
  font-weight: bold;
}

.test-btn:hover {
  transform: scale(1.05);
}

.result {
  margin-top: 20px;
  padding: 15px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  border-left: 4px solid #4ecdc4;
}

.result pre {
  background: rgba(0, 0, 0, 0.5);
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
  text-align: left;
}

.mock-manga {
  margin-top: 40px;
}

.manga-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-top: 20px;
}

.manga-item {
  background: rgba(255, 255, 255, 0.1);
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  font-size: 1.2rem;
  cursor: pointer;
  transition: transform 0.2s;
}

.manga-item:hover {
  transform: translateY(-3px);
  background: rgba(255, 255, 255, 0.15);
}
</style>