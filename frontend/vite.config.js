import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  
  // Configurações do servidor de desenvolvimento
  server: {
    host: true,
    port: 5173,
    open: true, // Abre automaticamente no browser
    strictPort: true, // Falha se a porta estiver em uso
    
    // Proxy para API do backend
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => {
          console.log(`Proxy: ${path} -> http://localhost:8000${path}`)
          return path
        }
      }
    }
  },
  
  // Resolve alias
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  
  // Build configurações
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html')
      }
    }
  },
  
  // Root do projeto (importante para SPAs)
  root: './',
  publicDir: 'public',
  
  // Configurações específicas para SPA
  appType: 'spa'
})