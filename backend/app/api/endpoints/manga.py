import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.core.library_state import library_state
from app.core.services.manga_scanner import MangaScanner
from app.core.utils import create_image_url

router = APIRouter()
logger = logging.getLogger(__name__)
scanner = MangaScanner()


@router.get("/api/manga/{manga_id}", tags=["manga"], summary="Obter detalhes do mangá")
async def get_manga(manga_id: str):
    """
    Retorna detalhes completos de um mangá específico incluindo capítulos.
    
    Args:
        manga_id: ID único do mangá
        
    Returns:
        Dados completos do mangá com capítulos e metadados
        
    Raises:
        HTTPException: Se o mangá não for encontrado
    """
    
    # Se não há biblioteca configurada, retornar erro
    if library_state.current_path is None:
        raise HTTPException(
            status_code=400,
            detail="Nenhuma biblioteca configurada. Configure uma biblioteca primeiro."
        )
    
    try:
        library = scanner.scan_library(library_state.current_path)
        manga = library.get_manga(manga_id)
        
        if not manga:
            raise HTTPException(
                status_code=404,
                detail=f"Mangá '{manga_id}' não encontrado na biblioteca"
            )
        
        # Preparar dados do mangá com serialização adequada de datetime
        manga_data = {
            "id": manga.id,
            "title": manga.title,
            "path": manga.path,
            "thumbnail": create_image_url(manga.thumbnail) if manga.thumbnail else None,
            "chapter_count": manga.chapter_count,
            "total_pages": manga.total_pages,
            "author": manga.author,
            "artist": manga.artist,
            "status": manga.status,
            "genres": manga.genres,
            "description": manga.description,
            "date_added": manga.date_added.isoformat() if manga.date_added else None,
            "date_modified": manga.date_modified.isoformat() if manga.date_modified else None
        }
        
        # Preparar capítulos com thumbnails
        chapters_with_thumbnails = []
        for chapter in manga.chapters:
            chapter_summary = {
                "id": chapter.id,
                "name": chapter.name,
                "number": chapter.number,
                "volume": chapter.volume,
                "page_count": chapter.page_count,
                "date_added": chapter.date_added.isoformat() if chapter.date_added else None,
                "thumbnail_url": None
            }
            
            # Adicionar thumbnail da primeira página
            if chapter.pages:
                first_page_path = chapter.pages[0].path
                chapter_summary['thumbnail_url'] = create_image_url(first_page_path)
            
            chapters_with_thumbnails.append(chapter_summary)
        
        manga_data['chapters'] = chapters_with_thumbnails
        
        return JSONResponse(content={
            "manga": manga_data,
            "message": f"Detalhes do mangá '{manga.title}' carregados",
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Erro ao buscar mangá {manga_id}: {str(e)}")
        
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao buscar mangá: {str(e)}"
        )