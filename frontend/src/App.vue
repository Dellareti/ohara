<template>
  <div id="app">
    <h1>🏴‍☠️ Ohara Test</h1>
    <p>Se você está vendo isto, o Vue está funcionando!</p>
    <button @click="testAPI">Testar API</button>
    <div v-if="result">{{ result }}</div>
  </div>
</template>

<script>
import { ref } from 'vue'

export default {
  name: 'App',
  setup() {
    const result = ref('')
    
    const testAPI = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/test')
        const data = await response.json()
        result.value = JSON.stringify(data, null, 2)
      } catch (error) {
        result.value = 'Erro: ' + error.message
      }
    }
    
    return { result, testAPI }
  }
}
</script>

<style>
#app {
  padding: 20px;
  background: #1e1e2e;
  color: white;
  min-height: 100vh;
}
button {
  background: #4ecdc4;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
}
</style>