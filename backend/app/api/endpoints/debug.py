import json
import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.core.library_state import library_state
from app.core.services.manga_scanner import MangaScanner
from app.core.utils import create_image_url

router = APIRouter()
logger = logging.getLogger(__name__)
scanner = MangaScanner()


@router.get("/api/debug", tags=["debug"], summary="Informações de debug")
async def debug_info():
    """
    Endpoint de debug para verificar estado do backend.
    
    Returns:
        Informações de debug sobre o estado atual da aplicação
    """
    
    return {
        "current_library_path": library_state.current_path,
        "path_file_exists": Path("last_library_path.txt").exists(),
        "path_file_content": Path("last_library_path.txt").read_text() if Path("last_library_path.txt").exists() else None,
        "path_is_valid": library_state.validate_current_path(),
        "message": "Debug info"
    }


@router.get("/api/debug/performance", tags=["debug"], summary="Debug de performance")
async def debug_performance():
    """
    Fornece informações de performance e cache da biblioteca atual.
    
    Returns:
        dict: Métricas de performance e informações de cache
        
    Raises:
        HTTPException: Se ocorrer erro durante a análise
    """
    
    if not library_state.current_path:
        return {
            "error": "Nenhuma biblioteca configurada",
            "current_library": None
        }
    
    try:
        import time
        from pathlib import Path
        
        library_path = Path(library_state.current_path)
        
        # Contar estrutura rapidamente
        manga_count = len([d for d in library_path.iterdir() if d.is_dir() and not d.name.startswith('.')])
        
        # Verificar cache
        cache_info = scanner.get_cache_info(library_state.current_path)
        
        # Estimativas de performance
        estimated_time_with_cache = 0.1 if cache_info["exists"] else None
        estimated_time_without_cache = manga_count * 0.3  # ~300ms por mangá
        
        return {
            "library_path": library_state.current_path,
            "manga_count": manga_count,
            "cache_info": cache_info,
            "performance_estimates": {
                "with_cache_seconds": estimated_time_with_cache,
                "without_cache_seconds": estimated_time_without_cache,
                "speedup_factor": round(estimated_time_without_cache / 0.1, 1) if estimated_time_with_cache else None
            },
            "cache_enabled": scanner.cache_enabled,
            "max_workers": scanner.max_workers
        }
        
    except Exception as e:
        logger.warning(f"Erro no debug de performance: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro no debug: {str(e)}"
        )


@router.get("/api/debug/thumbnails", tags=["debug"], summary="Debug de thumbnails")
async def debug_thumbnails():
    """
    Fornece informações de debug sobre thumbnails dos mangás.
    
    Returns:
        dict: Informações detalhadas sobre thumbnails
    """
    
    if not library_state.current_path:
        return {"error": "Nenhuma biblioteca configurada"}
    
    try:
        library = scanner.scan_library(library_state.current_path)
        
        debug_info = []
        for manga in library.mangas:
            thumbnail_info = {
                "manga": manga.title,
                "original_thumbnail": manga.thumbnail,
                "file_exists": Path(manga.thumbnail).exists() if manga.thumbnail else False,
                "is_file": Path(manga.thumbnail).is_file() if manga.thumbnail and Path(manga.thumbnail).exists() else False,
                "clean_url": create_image_url(manga.thumbnail) if manga.thumbnail else None
            }
            debug_info.append(thumbnail_info)
        
        return {
            "library_path": library_state.current_path,
            "total_mangas": len(debug_info),
            "thumbnails": debug_info
        }
        
    except Exception as e:
        return {"error": str(e)}


@router.get("/api/debug/reader", tags=["debug"], summary="Debug do leitor")
async def debug_reader_info():
    """
    Fornece informações de debug sobre o sistema de leitura.
    
    Returns:
        dict: Informações sobre configuração e estado do leitor
    """
    
    debug_info = {
        "library_configured": library_state.current_path is not None,
        "library_path": library_state.current_path,
        "cache_entries": len(_chapter_cache) if '_chapter_cache' in globals() else 0,
        "progress_file_exists": Path("reading_progress.json").exists(),
        "available_endpoints": [
            "/api/manga/{manga_id}",
            "/api/manga/{manga_id}/chapters",
            "/api/manga/{manga_id}/chapter/{chapter_id}",
            "/api/progress/{manga_id}",
            "/api/progress/{manga_id}/{chapter_id}",
            "POST /api/progress/{manga_id}/{chapter_id}"
        ]
    }
    
    # Verificar se há dados de progresso
    if Path("reading_progress.json").exists():
        try:
            with open("reading_progress.json", 'r') as f:
                progress_data = json.load(f)
                debug_info["progress_mangas"] = list(progress_data.keys())
                debug_info["total_progress_entries"] = sum(
                    len([k for k in v.keys() if not k.startswith('_')]) 
                    for v in progress_data.values()
                )
        except Exception as e:
            debug_info["progress_error"] = str(e)
    
    return debug_info