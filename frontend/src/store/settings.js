import { defineStore } from 'pinia'
import { useReaderStore } from './reader'

export const useSettingsStore = defineStore('settings', {
  state: () => ({
    // Interface Settings
    interface: {
      cardSize: 'medium', // small, medium, large
      itemsPerPage: 50 // 20, 50, 100
    },
    
    // Performance Settings
    performance: {
      cacheSize: 100, // MB
      preloadPages: 5, // number of pages
      enableCache: true,
      compressImages: false,
      maxCacheSize: 50 // for reader store sync
    },
    
    // System Settings
    system: {
      autoSaveProgress: true,
      version: '1.0.0'
    }
  }),

  getters: {
    // Combined settings for export
    allSettings: (state) => {
      const readerStore = useReaderStore()
      return {
        reader: {
          readingMode: readerStore.readingMode,
          fitMode: readerStore.fitMode,
          theme: readerStore.theme
        },
        interface: { ...state.interface },
        performance: { ...state.performance },
        system: { ...state.system }
      }
    },

    // Get cache usage simulation
    cacheUsed: (state) => {
      const readerStore = useReaderStore()
      return Math.min(readerStore.pageCache.size * 2, state.performance.cacheSize)
    }
  },

  actions: {
    // Load all settings
    loadSettings() {
      try {
        // Load interface settings
        const interfaceSettings = localStorage.getItem('ohara_interface_settings')
        if (interfaceSettings) {
          Object.assign(this.interface, JSON.parse(interfaceSettings))
        }

        // Load performance settings
        const performanceSettings = localStorage.getItem('ohara_performance_settings')
        if (performanceSettings) {
          Object.assign(this.performance, JSON.parse(performanceSettings))
        }

        // Load system settings
        const systemSettings = localStorage.getItem('ohara_system_settings')
        if (systemSettings) {
          Object.assign(this.system, JSON.parse(systemSettings))
        }

        // Sync performance settings with reader store
        this.syncWithReaderStore()

      } catch (error) {
        console.error('Error loading settings:', error)
      }
    },

    // Save all settings
    saveSettings() {
      try {
        localStorage.setItem('ohara_interface_settings', JSON.stringify(this.interface))
        localStorage.setItem('ohara_performance_settings', JSON.stringify(this.performance))
        localStorage.setItem('ohara_system_settings', JSON.stringify(this.system))
        
        // Sync with reader store
        this.syncWithReaderStore()
        
        return true
      } catch (error) {
        console.error('Error saving settings:', error)
        return false
      }
    },

    // Update interface settings
    updateInterfaceSettings(settings) {
      Object.assign(this.interface, settings)
      this.saveSettings()
    },

    // Update performance settings
    updatePerformanceSettings(settings) {
      Object.assign(this.performance, settings)
      this.saveSettings()
    },

    // Sync performance settings with reader store
    syncWithReaderStore() {
      const readerStore = useReaderStore()
      readerStore.maxCacheSize = this.performance.maxCacheSize
    },

    // Reset to defaults
    resetToDefaults() {
      // Reset interface settings
      this.interface = {
        cardSize: 'medium',
        itemsPerPage: 50
      }

      // Reset performance settings
      this.performance = {
        cacheSize: 100,
        preloadPages: 5,
        enableCache: true,
        compressImages: false,
        maxCacheSize: 50
      }

      // Reset system settings
      this.system = {
        autoSaveProgress: true,
        version: '1.0.0'
      }

      // Reset reader settings
      const readerStore = useReaderStore()
      readerStore.resetSettings()

      this.saveSettings()
    },

    // Export settings
    exportSettings() {
      return JSON.stringify(this.allSettings, null, 2)
    },

    // Import settings
    importSettings(settingsJson) {
      try {
        const settings = JSON.parse(settingsJson)
        
        // Import interface settings
        if (settings.interface) {
          Object.assign(this.interface, settings.interface)
        }
        
        // Import performance settings
        if (settings.performance) {
          Object.assign(this.performance, settings.performance)
        }
        
        // Import system settings
        if (settings.system) {
          Object.assign(this.system, settings.system)
        }
        
        // Import reader settings
        if (settings.reader) {
          const readerStore = useReaderStore()
          readerStore.updateReadingSettings(settings.reader)
        }
        
        this.saveSettings()
        return true
      } catch (error) {
        console.error('Error importing settings:', error)
        return false
      }
    },

    // Clear cache
    clearCache() {
      const readerStore = useReaderStore()
      readerStore.pageCache.clear()
      readerStore.preloadedPages.clear()
    }
  }
})