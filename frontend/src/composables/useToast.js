import { ref, readonly } from 'vue'

const toasts = ref([])
let toastId = 0

export function useToast() {
  const showToast = (message, type = 'info', duration = 5000) => {
    const id = ++toastId
    const toast = {
      id,
      message,
      type,
      timestamp: Date.now()
    }
    
    toasts.value.push(toast)
    
    setTimeout(() => {
      removeToast(id)
    }, duration)
    
    return id
  }
  
  const removeToast = (id) => {
    const index = toasts.value.findIndex(toast => toast.id === id)
    if (index > -1) {
      toasts.value.splice(index, 1)
    }
  }
  
  const showError = (message, duration = 6000) => {
    return showToast(message, 'error', duration)
  }
  
  const showSuccess = (message, duration = 4000) => {
    return showToast(message, 'success', duration)
  }
  
  const showWarning = (message, duration = 5000) => {
    return showToast(message, 'warning', duration)
  }
  
  const showInfo = (message, duration = 4000) => {
    return showToast(message, 'info', duration)
  }
  
  const clear = () => {
    toasts.value = []
  }
  
  return {
    toasts: readonly(toasts),
    showToast,
    showError,
    showSuccess,
    showWarning,
    showInfo,
    removeToast,
    clear
  }
}