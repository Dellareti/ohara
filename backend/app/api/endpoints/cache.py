import logging
from fastapi import APIRouter, HTTPException

from app.core.library_state import library_state
from app.core.services.manga_scanner import MangaScanner

router = APIRouter()
logger = logging.getLogger(__name__)
scanner = MangaScanner()


@router.get("/api/cache/info", tags=["cache"], summary="Informações do cache")
async def get_cache_info():
    """
    Retorna informações sobre o estado atual do cache.
    
    Returns:
        dict: Informações detalhadas sobre o cache
    """
    
    if not library_state.current_path:
        return {
            "cache_enabled": True,
            "current_library": None,
            "cache_info": {"exists": False}
        }
    
    try:
        cache_info = scanner.get_cache_info(library_state.current_path)
        
        return {
            "cache_enabled": scanner.cache_enabled,
            "current_library": library_state.current_path,
            "cache_info": cache_info,
            "scanner_version": "Cache Simples v2.0"
        }
        
    except Exception as e:
        return {
            "cache_enabled": scanner.cache_enabled,
            "current_library": library_state.current_path,
            "cache_info": {"exists": False, "error": str(e)},
            "scanner_version": "Cache Simples v2.0"
        }


@router.post("/api/cache/clear", tags=["cache"], summary="Limpar cache")
async def clear_cache():
    """
    Limpa o cache da biblioteca atual.
    
    Returns:
        dict: Resultado da operação de limpeza
        
    Raises:
        HTTPException: Se nenhuma biblioteca estiver configurada
    """
    
    if not library_state.current_path:
        raise HTTPException(
            status_code=400,
            detail="Nenhuma biblioteca configurada"
        )
    
    try:
        success = scanner.clear_cache(library_state.current_path)
        
        if success:
            return {
                "message": "Cache limpo com sucesso",
                "library_path": library_state.current_path,
                "status": "cleared"
            }
        else:
            return {
                "message": "Nenhum cache encontrado para limpar",
                "library_path": library_state.current_path,
                "status": "no_cache"
            }
            
    except Exception as e:
        logger.warning(f"Erro ao limpar cache: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao limpar cache: {str(e)}"
        )


@router.post("/api/cache/disable", tags=["cache"], summary="Desabilitar cache")
async def disable_cache():
    """
    Desabilita o sistema de cache.
    
    Returns:
        dict: Confirmação da desabilitação
        
    Raises:
        HTTPException: Se ocorrer erro durante a operação
    """
    
    try:
        scanner.disable_cache()
        
        return {
            "message": "Cache desabilitado",
            "cache_enabled": False,
            "status": "disabled"
        }
        
    except Exception as e:
        logger.warning(f"Erro ao desabilitar cache: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao desabilitar cache: {str(e)}"
        )


@router.post("/api/cache/enable", tags=["cache"], summary="Habilitar cache")
async def enable_cache():
    """
    Habilita o sistema de cache.
    
    Returns:
        dict: Confirmação da habilitação
        
    Raises:
        HTTPException: Se ocorrer erro durante a operação
    """
    
    try:
        scanner.enable_cache()
        
        return {
            "message": "Cache habilitado",
            "cache_enabled": True,
            "status": "enabled"
        }
        
    except Exception as e:
        logger.warning(f"Erro ao habilitar cache: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao habilitar cache: {str(e)}"
        )