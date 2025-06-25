export function formatError(error) {
  if (error.response) {
    const status = error.response.status
    const data = error.response.data
    
    if (data?.detail) {
      return data.detail
    }
    
    switch (status) {
      case 400:
        return 'Dados inválidos fornecidos'
      case 401:
        return 'Não autorizado - verifique suas credenciais'
      case 403:
        return 'Acesso negado - permissões insuficientes'
      case 404:
        return 'Recurso não encontrado'
      case 422:
        return 'Dados de entrada inválidos'
      case 500:
        return 'Erro interno do servidor'
      case 502:
        return 'Servidor indisponível temporariamente'
      case 503:
        return 'Serviço temporariamente indisponível'
      default:
        return `Erro do servidor (${status})`
    }
  } else if (error.request) {
    return 'Erro de conexão - verifique sua internet'
  } else if (error.code) {
    switch (error.code) {
      case 'ENOENT':
        return 'Arquivo ou diretório não encontrado'
      case 'EACCES':
        return 'Permissão negada para acessar o arquivo'
      case 'ENOTDIR':
        return 'Caminho especificado não é um diretório'
      case 'TIMEOUT':
        return 'Operação expirou - tente novamente'
      default:
        return error.message || 'Erro desconhecido'
    }
  }
  
  return error.message || 'Erro desconhecido'
}

export function formatFileError(error) {
  if (error.code) {
    switch (error.code) {
      case 'ENOENT':
        return 'Arquivo ou pasta não encontrada'
      case 'EACCES':
        return 'Sem permissão para acessar este local'
      case 'ENOTDIR':
        return 'O caminho não é uma pasta válida'
      case 'EISDIR':
        return 'O caminho é uma pasta, não um arquivo'
      case 'EMFILE':
      case 'ENFILE':
        return 'Muitos arquivos abertos - tente novamente'
      case 'ENOSPC':
        return 'Espaço em disco insuficiente'
      default:
        return `Erro de arquivo: ${error.message}`
    }
  }
  
  return formatError(error)
}

export function isRetryableError(error) {
  if (error.request && !error.response) {
    return true
  }
  
  if (error.response) {
    const status = error.response.status
    return status >= 500 || status === 408 || status === 429
  }
  
  if (error.code) {
    const retryableCodes = ['EMFILE', 'ENFILE', 'EAGAIN', 'EBUSY']
    return retryableCodes.includes(error.code)
  }
  
  return false
}

export function getErrorSeverity(error) {
  if (error.response) {
    const status = error.response.status
    if (status >= 500) return 'critical'
    if (status === 404 || status === 403) return 'high'
    if (status >= 400) return 'medium'
  }
  
  if (error.request && !error.response) {
    return 'high'
  }
  
  if (error.code) {
    const criticalCodes = ['ENOSPC', 'EACCES']
    if (criticalCodes.includes(error.code)) return 'critical'
    
    const highCodes = ['ENOENT', 'ENOTDIR']
    if (highCodes.includes(error.code)) return 'high'
  }
  
  return 'medium'
}