<template>
  <div id="app">
    <!-- Header/Navigation -->
    <header class="app-header">
      <nav class="main-nav">
        <div class="nav-brand">
          <h1>🏴‍☠️ Ohara</h1>
          <span class="version">v1.0.0</span>
        </div>
        
        <div class="nav-links">
          <router-link to="/" class="nav-link">📚 Biblioteca</router-link>
          <router-link to="/library-full" class="nav-link">🔧 Versão Completa</router-link>
          <button @click="testAPI" class="test-btn">🧪 Testar API</button>
        </div>
      </nav>
    </header>

    <!-- Main Content Area -->
    <main class="app-main">
      <!-- Vue Router View - aqui as páginas são renderizadas -->
      <router-view />
    </main>

    <!-- Footer -->
    <footer class="app-footer">
      <p>Projeto de Engenharia de Software II - Ohara Manga Reader</p>
      <div v-if="apiStatus" class="api-status">
        API Status: <span :class="apiStatus.ok ? 'status-ok' : 'status-error'">
          {{ apiStatus.message }}
        </span>
      </div>
    </footer>

    <!-- API Test Results Modal -->
    <div v-if="showTestResult" class="test-modal" @click="showTestResult = false">
      <div class="test-content" @click.stop>
        <h3>🧪 Resultado do Teste API</h3>
        <pre>{{ testResult }}</pre>
        <button @click="showTestResult = false">Fechar</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'

export default {
  name: 'App',
  setup() {
    const testResult = ref('')
    const showTestResult = ref(false)
    const apiStatus = ref(null)
    
    const testAPI = async () => {
      try {
        console.log('🔄 Testando comunicação com API...')
        const response = await fetch('http://localhost:8000/api/test')
        const data = await response.json()
        
        testResult.value = JSON.stringify(data, null, 2)
        showTestResult.value = true
        
        apiStatus.value = { ok: true, message: 'Conectado ✅' }
        console.log('✅ API funcionando:', data)
      } catch (error) {
        testResult.value = `❌ Erro: ${error.message}\n\nVerifique se o backend está rodando em http://localhost:8000`
        showTestResult.value = true
        
        apiStatus.value = { ok: false, message: 'Desconectado ❌' }
        console.error('❌ Erro na API:', error)
      }
    }
    
    // Verificar API na inicialização
    onMounted(() => {
      testAPI()
    })
    
    return { 
      testResult, 
      showTestResult, 
      apiStatus,
      testAPI 
    }
  }
}
</script>

<style>
/* Global Styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  min-height: 100vh;
  background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
  color: white;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  display: flex;
  flex-direction: column;
}

/* Header */
.app-header {
  background: rgba(0, 0, 0, 0.2);
  padding: 1rem 2rem;
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.main-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
}

.nav-brand h1 {
  font-size: 1.8rem;
  background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  display: inline;
}

.version {
  font-size: 0.8rem;
  opacity: 0.6;
  margin-left: 0.5rem;
}

.nav-links {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.nav-link {
  color: white;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  transition: all 0.3s;
  border: 1px solid transparent;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

.nav-link.router-link-active {
  background: rgba(78, 205, 196, 0.2);
  border-color: #4ecdc4;
}

.test-btn {
  background: linear-gradient(45deg, #4ecdc4, #44a08d);
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  color: white;
  cursor: pointer;
  font-size: 0.9rem;
  transition: transform 0.2s;
}

.test-btn:hover {
  transform: scale(1.05);
}

/* Main Content */
.app-main {
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  padding: 2rem;
}

/* Footer */
.app-footer {
  background: rgba(0, 0, 0, 0.3);
  padding: 1rem 2rem;
  text-align: center;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  font-size: 0.9rem;
  opacity: 0.8;
}

.api-status {
  margin-top: 0.5rem;
  font-size: 0.8rem;
}

.status-ok { color: #4ecdc4; }
.status-error { color: #ff6b6b; }

/* Test Modal */
.test-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.test-content {
  background: #2d2d44;
  padding: 2rem;
  border-radius: 10px;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.test-content h3 {
  color: #4ecdc4;
  margin-bottom: 1rem;
}

.test-content pre {
  background: rgba(0, 0, 0, 0.5);
  padding: 1rem;
  border-radius: 5px;
  overflow-x: auto;
  white-space: pre-wrap;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.test-content button {
  background: #4ecdc4;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 5px;
  color: white;
  cursor: pointer;
}

/* Responsive */
@media (max-width: 768px) {
  .main-nav {
    flex-direction: column;
    gap: 1rem;
  }
  
  .nav-links {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .app-main {
    padding: 1rem;
  }
}
</style>