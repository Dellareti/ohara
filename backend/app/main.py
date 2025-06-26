import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints.reader import router as reader_router
from app.api.endpoints.library import router as library_router
from app.api.endpoints.manga import router as manga_router
from app.api.endpoints.cache import router as cache_router
from app.api.endpoints.debug import router as debug_router
from app.api.endpoints.image import router as image_router
from app.core.library_state import library_state
from app.core.services.manga_scanner import MangaScanner
from log_config import log_config

logger = logging.getLogger(__name__)

# Inicializar o MangaScanner e carregar configurações
scanner = MangaScanner()
library_state.load_from_file()

# Configuração da aplicação FastAPI
app = FastAPI(
    title="Ohara Manga Reader API",
    description="""
    API para gerenciamento e leitura de mangás.
    
    ## Funcionalidades
    
    * **Biblioteca**: Escaneamento e gerenciamento de bibliotecas de mangás
    * **Mangás**: Visualização de detalhes e capítulos de mangás
    * **Leitura**: Sistema de progresso de leitura e navegação
    * **Cache**: Sistema de cache híbrido para melhor performance
    * **Imagens**: Servidor de imagens com validação de segurança
    * **Debug**: Ferramentas de debug e monitoramento
    
    ## Estrutura de Dados
    
    Os mangás são organizados em:
    - **Biblioteca** → contém múltiplos mangás
    - **Mangá** → contém múltiplos capítulos  
    - **Capítulo** → contém múltiplas páginas
    - **Página** → arquivo de imagem individual
    
    ## Configuração
    
    Para usar a API:
    1. Configure uma biblioteca com `POST /api/scan-library`
    2. Navegue pelos mangás disponíveis com `GET /api/library`
    3. Leia mangás específicos com `GET /api/manga/{manga_id}`
    """,
    version="2.0.0",
    contact={
        "name": "Ohara Development Team",
        "url": "https://github.com/seu-usuario/ohara",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers dos módulos
app.include_router(reader_router, prefix="", tags=["reader"])
app.include_router(library_router, prefix="", tags=["library"])
app.include_router(manga_router, prefix="", tags=["manga"])
app.include_router(cache_router, prefix="", tags=["cache"])
app.include_router(debug_router, prefix="", tags=["debug"])
app.include_router(image_router, prefix="", tags=["assets"])


@app.get("/", tags=["root"], summary="Informações da API")
async def root():
    """
    Endpoint raiz com informações básicas da API.
    
    Returns:
        dict: Informações sobre a API e seu status
    """
    
    return {
        "name": "Ohara Manga Reader API",
        "version": "2.0.0",
        "description": "API para gerenciamento e leitura de mangás",
        "status": "online",
        "library_configured": library_state.current_path is not None,
        "current_library": library_state.current_path,
        "endpoints": {
            "library": "/api/library",
            "scan": "/api/scan-library", 
            "manga": "/api/manga/{manga_id}",
            "reader": "/api/manga/{manga_id}/chapters",
            "cache": "/api/cache/info",
            "debug": "/api/debug"
        }
    }


@app.get("/health", tags=["health"], summary="Health check")
async def health_check():
    """
    Endpoint de health check para monitoramento.
    
    Returns:
        dict: Status da aplicação e dependências
    """
    
    return {
        "status": "healthy",
        "library_state": "configured" if library_state.current_path else "not_configured",
        "scanner_enabled": True,
        "cache_enabled": scanner.cache_enabled
    }


@app.get("/api/test", tags=["test"], summary="Teste da API")
async def test_api():
    """
    Endpoint de teste para verificar funcionamento básico da API.
    
    Returns:
        dict: Confirmação de funcionamento
    """
    
    return {
        "message": "API funcionando corretamente!",
        "timestamp": "2024-01-01T00:00:00Z",
        "test": "success"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config=log_config,
        log_level="info"
    )