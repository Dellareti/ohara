<template>
  <div class="settings-view">
    <div class="settings-header">
      <h1>Configurações do Sistema</h1>
      <p>Personalize sua experiência de leitura e configurações gerais</p>
    </div>

    <div class="settings-content">
      <!-- Configurações de Leitura -->
      <div class="settings-section">
        <h2>Configurações de Leitura</h2>
        <div class="settings-grid">
          <div class="setting-item">
            <label>Modo de Leitura Padrão:</label>
            <select v-model="readerSettings.defaultReadingMode" class="setting-input">
              <option value="single">Página Única</option>
              <option value="double">Página Dupla</option>
              <option value="vertical">Vertical</option>
              <option value="webtoon">Webtoon</option>
            </select>
          </div>

          <div class="setting-item">
            <label>Ajuste de Imagem Padrão:</label>
            <select v-model="readerSettings.defaultFitMode" class="setting-input">
              <option value="width">Ajustar Largura</option>
              <option value="height">Ajustar Altura</option>
              <option value="screen">Ajustar Tela</option>
              <option value="original">Tamanho Original</option>
            </select>
          </div>

          <div class="setting-item">
            <label>Direção de Leitura:</label>
            <select v-model="readerSettings.defaultDirection" class="setting-input">
              <option value="rtl">Direita → Esquerda (Mangá)</option>
              <option value="ltr">Esquerda → Direita (HQ)</option>
            </select>
          </div>

          <div class="setting-item">
            <label>Tema Padrão:</label>
            <select v-model="readerSettings.defaultTheme" class="setting-input">
              <option value="dark">Escuro</option>
              <option value="light">Claro</option>
              <option value="sepia">Sépia</option>
            </select>
          </div>

          <div class="setting-item">
            <label>Zonas de Toque:</label>
            <select v-model="readerSettings.defaultTouchZones" class="setting-input">
              <option value="edge">Bordas</option>
              <option value="kindle">Estilo Kindle</option>
              <option value="l-shape">Formato L</option>
              <option value="split">Dividido</option>
            </select>
          </div>

          <div class="setting-item">
            <label>Auto-scroll Padrão (segundos):</label>
            <div class="range-container">
              <input 
                type="range" 
                v-model.number="readerSettings.defaultAutoScroll" 
                min="0" 
                max="10" 
                step="0.5"
                class="range-input"
              />
              <span class="range-value">{{ readerSettings.defaultAutoScroll || 'Desativado' }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Configurações da Interface -->
      <div class="settings-section">
        <h2>Interface</h2>
        <div class="settings-grid">
          <div class="setting-item">
            <label>Tamanho dos Cards da Biblioteca:</label>
            <select v-model="interfaceSettings.cardSize" class="setting-input">
              <option value="small">Pequeno</option>
              <option value="medium">Médio</option>
              <option value="large">Grande</option>
            </select>
          </div>

          <div class="setting-item">
            <label>Itens por Página:</label>
            <select v-model="interfaceSettings.itemsPerPage" class="setting-input">
              <option value="20">20 items</option>
              <option value="50">50 items</option>
              <option value="100">100 items</option>
            </select>
          </div>

          <div class="setting-item checkbox-item">
            <label>
              <input type="checkbox" v-model="interfaceSettings.showThumbnails" />
              Mostrar Thumbnails dos Mangás
            </label>
          </div>

          <div class="setting-item checkbox-item">
            <label>
              <input type="checkbox" v-model="interfaceSettings.showProgress" />
              Mostrar Progresso de Leitura
            </label>
          </div>

          <div class="setting-item checkbox-item">
            <label>
              <input type="checkbox" v-model="interfaceSettings.darkMode" />
              Modo Escuro Global
            </label>
          </div>
        </div>
      </div>

      <!-- Configurações de Performance -->
      <div class="settings-section">
        <h2>Performance</h2>
        <div class="settings-grid">
          <div class="setting-item">
            <label>Cache de Imagens (MB):</label>
            <select v-model="performanceSettings.cacheSize" class="setting-input">
              <option value="50">50 MB</option>
              <option value="100">100 MB</option>
              <option value="200">200 MB</option>
              <option value="500">500 MB</option>
            </select>
          </div>

          <div class="setting-item">
            <label>Pré-carregamento de Páginas:</label>
            <select v-model="performanceSettings.preloadPages" class="setting-input">
              <option value="1">1 página</option>
              <option value="3">3 páginas</option>
              <option value="5">5 páginas</option>
              <option value="10">10 páginas</option>
            </select>
          </div>

          <div class="setting-item checkbox-item">
            <label>
              <input type="checkbox" v-model="performanceSettings.enableCache" />
              Habilitar Cache de Biblioteca
            </label>
          </div>

          <div class="setting-item checkbox-item">
            <label>
              <input type="checkbox" v-model="performanceSettings.compressImages" />
              Comprimir Imagens Automaticamente
            </label>
          </div>
        </div>
      </div>

      <!-- Configurações de Backup -->
      <div class="settings-section">
        <h2>Backup e Dados</h2>
        <div class="settings-grid">
          <div class="setting-item checkbox-item">
            <label>
              <input type="checkbox" v-model="backupSettings.autoSaveProgress" />
              Salvar Progresso Automaticamente
            </label>
          </div>

          <div class="setting-item">
            <label>Frequência de Backup:</label>
            <select v-model="backupSettings.backupFrequency" class="setting-input">
              <option value="never">Nunca</option>
              <option value="daily">Diário</option>
              <option value="weekly">Semanal</option>
              <option value="monthly">Mensal</option>
            </select>
          </div>

          <div class="setting-item">
            <label>Local do Backup:</label>
            <div class="input-group">
              <input 
                type="text" 
                v-model="backupSettings.backupPath" 
                placeholder="Caminho para backup"
                class="setting-input"
              />
              <button class="browse-btn">Navegar</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Ações -->
      <div class="settings-actions">
        <button @click="exportSettings" class="action-btn secondary">
          Exportar Configurações
        </button>
        <button @click="importSettings" class="action-btn secondary">
          Importar Configurações
        </button>
        <button @click="resetToDefaults" class="action-btn danger">
          Restaurar Padrões
        </button>
        <button @click="saveSettings" class="action-btn primary">
          Salvar Configurações
        </button>
      </div>

      <!-- Informações do Sistema -->
      <div class="settings-section">
        <h2>Informações do Sistema</h2>
        <div class="system-info">
          <div class="info-item">
            <span class="info-label">Versão do Ohara:</span>
            <span class="info-value">v1.0.0</span>
          </div>
          <div class="info-item">
            <span class="info-label">Backend Status:</span>
            <span class="info-value" :class="{ 'status-online': backendOnline, 'status-offline': !backendOnline }">
              {{ backendOnline ? 'Online' : 'Offline' }}
            </span>
          </div>
          <div class="info-item">
            <span class="info-label">Biblioteca Configurada:</span>
            <span class="info-value">{{ libraryPath || 'Não configurada' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Cache Usado:</span>
            <span class="info-value">{{ cacheUsed }} MB</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useLibraryStore } from '@/store/library'

export default {
  name: 'SettingsView',
  setup() {
    const libraryStore = useLibraryStore()

    // Estados reativos para as configurações
    const readerSettings = reactive({
      defaultReadingMode: 'single',
      defaultFitMode: 'width',
      defaultDirection: 'rtl',
      defaultTheme: 'dark',
      defaultTouchZones: 'edge',
      defaultAutoScroll: 0
    })

    const interfaceSettings = reactive({
      cardSize: 'medium',
      itemsPerPage: 50,
      showThumbnails: true,
      showProgress: true,
      darkMode: true
    })

    const performanceSettings = reactive({
      cacheSize: 100,
      preloadPages: 5,
      enableCache: true,
      compressImages: false
    })

    const backupSettings = reactive({
      autoSaveProgress: true,
      backupFrequency: 'weekly',
      backupPath: ''
    })

    // Estados de informação
    const backendOnline = ref(false)
    const libraryPath = ref('')
    const cacheUsed = ref(0)

    // Métodos
    const loadSettings = () => {
      try {
        const savedSettings = localStorage.getItem('ohara_system_settings')
        if (savedSettings) {
          const settings = JSON.parse(savedSettings)
          
          Object.assign(readerSettings, settings.reader || {})
          Object.assign(interfaceSettings, settings.interface || {})
          Object.assign(performanceSettings, settings.performance || {})
          Object.assign(backupSettings, settings.backup || {})
        }
      } catch (error) {
        console.error('Erro ao carregar configurações:', error)
      }
    }

    const saveSettings = () => {
      try {
        const settings = {
          reader: { ...readerSettings },
          interface: { ...interfaceSettings },
          performance: { ...performanceSettings },
          backup: { ...backupSettings }
        }
        
        localStorage.setItem('ohara_system_settings', JSON.stringify(settings))
        
        // Mostrar feedback
        alert('✅ Configurações salvas com sucesso!')
        
        console.log('✅ Configurações salvas:', settings)
      } catch (error) {
        console.error('Erro ao salvar configurações:', error)
        alert('❌ Erro ao salvar configurações')
      }
    }

    const resetToDefaults = () => {
      if (confirm('Tem certeza que deseja restaurar todas as configurações para os valores padrão?')) {
        // Resetar para valores padrão
        Object.assign(readerSettings, {
          defaultReadingMode: 'single',
          defaultFitMode: 'width',
          defaultDirection: 'rtl',
          defaultTheme: 'dark',
          defaultTouchZones: 'edge',
          defaultAutoScroll: 0
        })

        Object.assign(interfaceSettings, {
          cardSize: 'medium',
          itemsPerPage: 50,
          showThumbnails: true,
          showProgress: true,
          darkMode: true
        })

        Object.assign(performanceSettings, {
          cacheSize: 100,
          preloadPages: 5,
          enableCache: true,
          compressImages: false
        })

        Object.assign(backupSettings, {
          autoSaveProgress: true,
          backupFrequency: 'weekly',
          backupPath: ''
        })

        saveSettings()
      }
    }

    const exportSettings = () => {
      try {
        const settings = {
          reader: { ...readerSettings },
          interface: { ...interfaceSettings },
          performance: { ...performanceSettings },
          backup: { ...backupSettings }
        }
        
        const dataStr = JSON.stringify(settings, null, 2)
        const dataBlob = new Blob([dataStr], { type: 'application/json' })
        
        const link = document.createElement('a')
        link.href = URL.createObjectURL(dataBlob)
        link.download = 'ohara_settings.json'
        link.click()
        
        console.log('✅ Configurações exportadas')
      } catch (error) {
        console.error('Erro ao exportar configurações:', error)
        alert('❌ Erro ao exportar configurações')
      }
    }

    const importSettings = () => {
      const input = document.createElement('input')
      input.type = 'file'
      input.accept = '.json'
      
      input.onchange = (event) => {
        const file = event.target.files[0]
        if (!file) return
        
        const reader = new FileReader()
        reader.onload = (e) => {
          try {
            const settings = JSON.parse(e.target.result)
            
            if (settings.reader) Object.assign(readerSettings, settings.reader)
            if (settings.interface) Object.assign(interfaceSettings, settings.interface)
            if (settings.performance) Object.assign(performanceSettings, settings.performance)
            if (settings.backup) Object.assign(backupSettings, settings.backup)
            
            saveSettings()
            alert('✅ Configurações importadas com sucesso!')
          } catch (error) {
            console.error('Erro ao importar configurações:', error)
            alert('❌ Erro ao importar configurações: arquivo inválido')
          }
        }
        reader.readAsText(file)
      }
      
      input.click()
    }

    const checkSystemInfo = async () => {
      // Verificar status do backend
      try {
        const response = await fetch('http://localhost:8000/api/test')
        backendOnline.value = response.ok
      } catch {
        backendOnline.value = false
      }

      // Informações da biblioteca
      libraryPath.value = libraryStore.libraryPath || 'Não configurada'

      // Calcular cache usado (simulado)
      cacheUsed.value = Math.round(Math.random() * 50) + 10
    }

    // Lifecycle
    onMounted(() => {
      loadSettings()
      checkSystemInfo()
    })

    return {
      readerSettings,
      interfaceSettings,
      performanceSettings,
      backupSettings,
      backendOnline,
      libraryPath,
      cacheUsed,
      saveSettings,
      resetToDefaults,
      exportSettings,
      importSettings
    }
  }
}
</script>

<style scoped>
.settings-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
  color: white;
  padding: 20px;
}

.settings-header {
  text-align: center;
  margin-bottom: 40px;
}

.settings-header h1 {
  font-size: 2.5rem;
  margin-bottom: 10px;
  color: white;
}

.settings-header p {
  font-size: 1.2rem;
  opacity: 0.8;
}

.settings-content {
  max-width: 1000px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.settings-section {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 15px;
  padding: 25px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.settings-section h2 {
  color: #4ecdc4;
  margin-bottom: 20px;
  font-size: 1.3rem;
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.setting-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.setting-item.checkbox-item {
  flex-direction: row;
  align-items: center;
  gap: 10px;
}

.setting-item label {
  font-weight: 500;
  color: white;
  display: flex;
  align-items: center;
  gap: 8px;
}

.setting-input {
  padding: 10px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.3);
  color: white;
  font-size: 1rem;
}

.setting-input:focus {
  outline: none;
  border-color: #4ecdc4;
}

.range-container {
  display: flex;
  align-items: center;
  gap: 15px;
}

.range-input {
  flex: 1;
  height: 6px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 3px;
  outline: none;
  cursor: pointer;
}

.range-value {
  min-width: 80px;
  text-align: right;
  font-weight: 500;
  color: #4ecdc4;
}

.input-group {
  display: flex;
  gap: 10px;
}

.browse-btn {
  padding: 10px 15px;
  background: linear-gradient(45deg, #4ecdc4, #44a08d);
  border: none;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  font-size: 0.9rem;
}

.settings-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  flex-wrap: wrap;
}

.action-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 500;
  font-size: 1rem;
  transition: transform 0.2s ease;
}

.action-btn:hover {
  transform: translateY(-2px);
}

.action-btn.primary {
  background: linear-gradient(45deg, #4ecdc4, #44a08d);
  color: white;
}

.action-btn.secondary {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.action-btn.danger {
  background: linear-gradient(45deg, #ff6b6b, #ee5a52);
  color: white;
}

.system-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
}

.info-label {
  font-weight: 500;
}

.info-value {
  font-weight: bold;
}

.status-online {
  color: #4caf50;
}

.status-offline {
  color: #f44336;
}

@media (max-width: 768px) {
  .settings-grid {
    grid-template-columns: 1fr;
  }
  
  .settings-actions {
    flex-direction: column;
  }
  
  .system-info {
    grid-template-columns: 1fr;
  }
}
</style>