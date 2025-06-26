import json
import logging
import os
from pathlib import Path

from fastapi import APIRouter, HTTPException, Form
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.core.library_state import library_state
from app.core.services.manga_scanner import MangaScanner
from app.models.manga import LibraryResponse

router = APIRouter()
logger = logging.getLogger(__name__)
scanner = MangaScanner()


def manga_to_dict(manga):
    """
    Converte um objeto Manga para dicionário, tratando campos especiais como datetime
    """
    manga_dict = {
        "id": manga.id,
        "title": manga.title,
        "path": manga.path,
        "thumbnail": manga.thumbnail,
        "chapter_count": manga.chapter_count,
        "total_pages": manga.total_pages,
        "author": manga.author,
        "artist": manga.artist,
        "status": manga.status,
        "description": manga.description,
        "genres": manga.genres,
        "date_added": manga.date_added.isoformat() if manga.date_added else None,
        "date_modified": manga.date_modified.isoformat() if manga.date_modified else None,
        "chapters": []
    }
    
    for chapter in manga.chapters:
        chapter_dict = {
            "id": chapter.id,
            "name": chapter.name,
            "number": chapter.number,
            "volume": chapter.volume,
            "path": chapter.path,
            "page_count": chapter.page_count,
            "date_added": chapter.date_added.isoformat() if chapter.date_added else None,
            "pages": []
        }
        manga_dict["chapters"].append(chapter_dict)
    
    return manga_dict


def _scan_library_common(library_path: str, method: str = "POST"):
    """
    Lógica comum para escanear biblioteca (usada por POST e GET)
    """

    # Limpar e normalizar o caminho
    library_path = library_path.strip()
    
    # Log para debug
    logger.info(f"[{method}] Caminho recebido: '{library_path}'")
    if method == "POST":
        logger.info(f"Comprimento: {len(library_path)} caracteres")
        logger.info(f"Encoding: {library_path.encode('utf-8')}")
    
    if library_state.current_path != library_path:
        logger.info(f"[{method}] Mudando biblioteca de '{library_state.current_path}' para '{library_path}'")
        library_state.clear()
    
    # Validar se o caminho existe - com tratamento melhor de Unicode para POST
    if method == "POST":
        try:
            path_obj = Path(library_path)
            logger.info(f"Path object criado: {path_obj}")
            logger.info(f"Absolute path: {path_obj.absolute()}")
            
        except Exception as path_error:
            logger.warning(f"Erro ao criar Path object: {path_error}")
            raise HTTPException(
                status_code=400,
                detail=f"Caminho inválido (erro de encoding): {library_path}"
            )
    else:
        path_obj = Path(library_path)
        logger.info(f"[{method}] Path object criado: {path_obj}")
    
    if not path_obj.exists():
        if method == "POST":
            # Tentar variações comuns de encoding
            alternative_paths = [
                Path(library_path.encode('utf-8').decode('utf-8')),
                Path(library_path.encode('latin-1').decode('utf-8', errors='ignore')),
            ]
            
            path_found = False
            for alt_path in alternative_paths:
                try:
                    if alt_path.exists():
                        path_obj = alt_path
                        library_path = str(alt_path)
                        path_found = True
                        logger.info(f"Caminho encontrado com encoding alternativo: {library_path}")
                        break
                except:
                    continue
            
            if not path_found:
                raise HTTPException(
                    status_code=400,
                    detail=f"Caminho não encontrado: {library_path}"
                )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Caminho não encontrado: {library_path}"
            )
    
    if not path_obj.is_dir():
        raise HTTPException(
            status_code=400,
            detail=f"Caminho não é um diretório: {library_path}"
        )
    
    # Validar permissões de leitura
    if not os.access(str(path_obj), os.R_OK):
        raise HTTPException(
            status_code=403,
            detail=f"Sem permissão de leitura: {library_path}"
        )
    
    # Verificar se existem subpastas (indicativo de mangás)
    subdirs = [d for d in path_obj.iterdir() if d.is_dir()]
    if len(subdirs) == 0:
        raise HTTPException(
            status_code=400,
            detail=f"Pasta não contém subdiretórios (mangás): {library_path}"
        )
    
    logger.info(f"Escaneando biblioteca: {library_path}")
    
    library = scanner.scan_library(str(path_obj))
    
    
    # Atualizar caminho atual SOMENTE após sucesso
    library_state.current_path = str(path_obj)
    
    logger.info(f"Biblioteca escaneada: {library.total_mangas} mangás encontrados")
    
    # Converter para resposta da API
    response_data = {
        "library": {
            "mangas": [manga_to_dict(manga) for manga in library.mangas],
            "total_mangas": library.total_mangas,
            "total_chapters": library.total_chapters,
            "total_pages": library.total_pages,
            "last_updated": library.last_updated.isoformat()
        },
        "message": f"Biblioteca escaneada com sucesso! {library.total_mangas} mangás encontrados.",
        "scanned_path": str(path_obj),
        "timestamp": library.last_updated.isoformat()
    }
    
    if method == "GET":
        response_data["method"] = "GET"
    
    return response_data


@router.post("/api/clear-library")
async def clear_library():
    try:
        logger.info("Limpando biblioteca no backend...")
        
        library_state.clear()
        
        logger.info("Biblioteca limpa no backend")
        
        return {
            "message": "Biblioteca limpa com sucesso",
            "current_path": None,
            "status": "cleared"
        }
        
    except Exception as e:
        logger.warning(f"Erro ao limpar biblioteca: {str(e)}")
        return {
            "message": f"Erro ao limpar biblioteca: {str(e)}",
            "status": "error"
        }


@router.post("/api/scan-library", tags=["library"], summary="Escanear biblioteca")
async def scan_library_path(library_path: str = Form(...)):
    """
    Escaneia uma pasta do sistema para encontrar mangás organizados.
    
    Args:
        library_path: Caminho absoluto para a pasta da biblioteca
    
    Returns:
        LibraryResponse: Biblioteca escaneada com mangás encontrados
        
    Raises:
        HTTPException: Se o caminho não existir ou não tiver permissões
    """
    
    try:
        response_data = _scan_library_common(library_path, "POST")
        return JSONResponse(content=jsonable_encoder(response_data))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Erro ao escanear biblioteca: {str(e)}")
        logger.warning(f"Tipo do erro: {type(e).__name__}")
        import traceback
        logger.warning(f"Traceback: {traceback.format_exc()}")
        
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao escanear biblioteca: {str(e)}"
        )


@router.get("/api/scan-library", tags=["library"], summary="Escanear biblioteca salva")
async def scan_saved_library():
    """
    Escaneia a biblioteca salva anteriormente.
    
    Returns:
        LibraryResponse: Biblioteca escaneada com mangás encontrados
        
    Raises:
        HTTPException: Se não houver biblioteca configurada
    """
    
    current_path = library_state.current_path
    
    if not current_path:
        raise HTTPException(
            status_code=400,
            detail="Nenhuma biblioteca configurada. Use POST /api/scan-library para configurar."
        )
    
    try:
        response_data = _scan_library_common(current_path, "GET")
        return JSONResponse(content=jsonable_encoder(response_data))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Erro ao escanear biblioteca salva: {str(e)}")
        
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao escanear biblioteca: {str(e)}"
        )


@router.get("/api/library", tags=["library"], summary="Obter biblioteca atual")
async def get_library():
    """
    Retorna a biblioteca atualmente configurada.
    
    Returns:
        dict: Informações sobre a biblioteca atual
        
    Raises:
        HTTPException: Se nenhuma biblioteca estiver configurada
    """
    
    current_path = library_state.current_path
    
    if not current_path:
        raise HTTPException(
            status_code=400,
            detail="Nenhuma biblioteca configurada"
        )
    
    if not library_state.validate_current_path():
        raise HTTPException(
            status_code=400,
            detail=f"Caminho da biblioteca inválido: {current_path}"
        )
    
    try:
        library = scanner.scan_library(current_path)
        
        response_data = {
            "library": {
                "mangas": [manga_to_dict(manga) for manga in library.mangas],
                "total_mangas": library.total_mangas,
                "total_chapters": library.total_chapters,
                "total_pages": library.total_pages,
                "last_updated": library.last_updated.isoformat()
            },
            "current_path": current_path,
            "message": f"Biblioteca carregada: {library.total_mangas} mangás encontrados"
        }
        
        return JSONResponse(content=jsonable_encoder(response_data))
        
    except Exception as e:
        logger.warning(f"Erro ao carregar biblioteca: {str(e)}")
        
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao carregar biblioteca: {str(e)}"
        )


@router.get("/api/validate-path", tags=["library"], summary="Validar caminho da biblioteca")
async def validate_library_path(path: str):
    """
    Valida se um caminho pode ser usado como biblioteca de mangás.
    
    Args:
        path: Caminho a ser validado
    
    Returns:
        dict: Resultado da validação
    """
    
    try:
        is_valid, message = scanner.validate_library_path(path)
        
        return {
            "path": path,
            "is_valid": is_valid,
            "message": message,
            "current_library": library_state.current_path
        }
        
    except Exception as e:
        logger.warning(f"Erro ao validar caminho: {str(e)}")
        
        return {
            "path": path,
            "is_valid": False,
            "message": f"Erro ao validar: {str(e)}",
            "current_library": library_state.current_path
        }


@router.get("/api/preview-library", tags=["library"], summary="Preview da biblioteca")
async def preview_library(path: str):
    """
    Faz uma prévia rápida de uma biblioteca sem configurá-la.
    
    Args:
        path: Caminho da biblioteca para preview
    
    Returns:
        dict: Preview com informações básicas da biblioteca
    """
    
    try:
        path_obj = Path(path)
        
        if not path_obj.exists():
            raise HTTPException(status_code=404, detail="Caminho não encontrado")
        
        if not path_obj.is_dir():
            raise HTTPException(status_code=400, detail="Caminho não é um diretório")
        
        subdirs = [d for d in path_obj.iterdir() if d.is_dir()]
        
        # Contagem básica
        total_folders = len(subdirs)
        
        # Estimativa rápida de capítulos (apenas primeiros 10 mangás para não ser lento)
        estimated_chapters = 0
        sampled_mangas = 0
        
        for manga_dir in subdirs[:10]:
            try:
                chapter_dirs = [d for d in manga_dir.iterdir() if d.is_dir()]
                estimated_chapters += len(chapter_dirs)
                sampled_mangas += 1
            except:
                continue
        
        # Extrapolar estimativa para todos os mangás
        if sampled_mangas > 0:
            avg_chapters_per_manga = estimated_chapters / sampled_mangas
            estimated_total_chapters = int(avg_chapters_per_manga * total_folders)
        else:
            estimated_total_chapters = 0
        
        return {
            "path": str(path_obj),
            "total_manga_folders": total_folders,
            "estimated_chapters": estimated_total_chapters,
            "sampled_mangas": sampled_mangas,
            "is_valid": total_folders > 0,
            "message": f"Preview: {total_folders} pastas de mangá encontradas"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Erro no preview da biblioteca: {str(e)}")
        
        raise HTTPException(
            status_code=500,
            detail=f"Erro no preview: {str(e)}"
        )


@router.post("/api/set-library-path", tags=["library"], summary="Configurar caminho da biblioteca")
async def set_library_path(library_path: str = Form(...)):
    """
    Configura o caminho da biblioteca sem escaneá-la.
    
    Args:
        library_path: Caminho da biblioteca
    
    Returns:
        dict: Confirmação da configuração
    """
    
    try:
        library_path = library_path.strip()
        path_obj = Path(library_path)
        
        if not path_obj.exists():
            raise HTTPException(status_code=404, detail="Caminho não encontrado")
        
        if not path_obj.is_dir():
            raise HTTPException(status_code=400, detail="Caminho não é um diretório")
        
        library_state.current_path = str(path_obj)
        
        return {
            "message": "Caminho da biblioteca configurado com sucesso",
            "library_path": str(path_obj),
            "status": "configured"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Erro ao configurar biblioteca: {str(e)}")
        
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao configurar biblioteca: {str(e)}"
        )