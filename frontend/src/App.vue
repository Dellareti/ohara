<template>
  <div id="app">
    <!-- Header/Navigation -->
    <header class="app-header">
      <nav class="main-nav">
        <div class="nav-brand">
          <router-link to="/library" class="brand-link">
            <h1>🏴‍☠️ Ohara</h1>
          </router-link>
          <span class="version">v1.0.0</span>
        </div>
        
        <div class="nav-links">
          <router-link to="/" class="nav-link">Biblioteca</router-link>
          <router-link to="/setup" class="nav-link">Setup</router-link>
          <router-link to="/settings" class="nav-link">Configurações</router-link>
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
      <p>Ohara Manga Reader - Leia suas histórias favoritas</p>
    </footer>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'

export default {
  name: 'App',
  setup() {
    const isConnected = ref(false)
    
    const checkConnection = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/test')
        if (response.ok) {
          isConnected.value = true
          console.log('Sistema online')
        } else {
          isConnected.value = false
          console.log('Sistema com erro:', response.status)
        }
      } catch (error) {
        isConnected.value = false
        console.log('Sistema offline:', error.message)
      }
    }
    
    // Verificar API na inicialização
    onMounted(() => {
      checkConnection()
      
      // Verificar conexão periodicamente
      setInterval(checkConnection, 30000)
    })
    
    return { 
      isConnected
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

body:has(.manga-reader) .app-header,
body:has(.manga-reader) .app-footer {
  display: none !important;
}

.manga-reader ~ * .app-header,
.manga-reader ~ * .app-footer,
.manga-reader + * .app-header,
.manga-reader + * .app-footer {
  display: none !important;
}

/* Quando a página é de leitura, remover padding do main */
body:has(.manga-reader) .app-main {
  padding: 0;
  margin: 0;
  max-width: none;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
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

.nav-brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.brand-link {
  text-decoration: none;
  color: white;
  cursor: pointer;
  transition: opacity 0.3s ease;
}

.brand-link:hover {
  opacity: 0.8;
}

.nav-brand h1 {
  font-size: 1.8rem;
  color: white;
  margin: 0;
}

.version {
  font-size: 0.8rem;
  opacity: 0.6;
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
  font-weight: 500;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

.nav-link.router-link-active {
  background: rgba(78, 205, 196, 0.2);
  border-color: #4ecdc4;
}

/* Connection Status */
.connection-status {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 15px;
  font-size: 0.8rem;
  font-weight: 500;
  transition: all 0.3s ease;
}

.connection-status.connected {
  background: rgba(76, 175, 80, 0.15);
  color: #4CAF50;
  border: 1px solid rgba(76, 175, 80, 0.3);
}

.connection-status.disconnected {
  background: rgba(244, 67, 54, 0.15);
  color: #F44336;
  border: 1px solid rgba(244, 67, 54, 0.3);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
  animation: pulse 2s infinite;
}

.status-text {
  font-size: 0.75rem;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}

/* Main Content */
.app-main {
  flex: 1;
  max-width: auto;
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
  
  .connection-status {
    order: -1;
    margin-bottom: 0.5rem;
  }
}
</style>