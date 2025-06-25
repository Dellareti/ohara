import json
import logging
import mimetypes
import os
import urllib.parse
import urllib.parse
from pathlib import Path

from fastapi import FastAPI, HTTPException, Form
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse

from app.api.endpoints.reader import router as reader_router
from app.core.library_state import library_state
from app.core.services.manga_scanner import MangaScanner
from app.models.manga import LibraryResponse
from log_config import log_config

logger = logging.getLogger(__name__)

def manga_to_dict(manga) -> dict:
    """Converte um objeto Manga para dict com serialização adequada de datetime"""
    return {
        "id": manga.id,
        "title": manga.title,
        "path": manga.path,
        "thumbnail": manga.thumbnail,
        "chapter_count": manga.chapter_count,
        "total_pages": manga.total_pages,
        "author": manga.author,
        "artist": manga.artist,
        "status": manga.status,
        "genres": manga.genres,
        "description": manga.description,
        "date_added": manga.date_added.isoformat() if manga.date_added else None,
        "date_modified": manga.date_modified.isoformat() if manga.date_modified else None,
        "chapters": [
            {
                "id": chapter.id,
                "name": chapter.name,
                "number": chapter.number,
                "volume": chapter.volume,
                "page_count": chapter.page_count,
                "date_added": chapter.date_added.isoformat() if chapter.date_added else None
            }
            for chapter in manga.chapters
        ]
    }

def create_image_url(file_path: str) -> str:
    """
    Args:
        file_path: Caminho absoluto do arquivo
        
    Returns:
        str: URL da API para servir a imagem ou None
    """
    if not file_path:
        return None
    
    # Se já é uma URL da API, retornar como está
    if file_path.startswith('/api/image'):
        logger.info(f"URL da API reutilizada: {file_path[:50]}...")
        return file_path 
    
    # Se é URL externa, retornar como está
    if file_path.startswith('http'):
        logger.info(f"URL externa detectada: {file_path[:50]}...")
        return file_path
    
    # Validar se é um caminho de arquivo válido
    try:
        file_obj = Path(file_path)
        if not file_obj.exists() or not file_obj.is_file():
            logger.warning(f"Arquivo não existe: {file_path}")
            return None
            
        # Verificar se é imagem
        mime_type, _ = mimetypes.guess_type(str(file_obj))
        if not mime_type or not mime_type.startswith('image/'):
            logger.warning(f"Não é imagem: {file_path} (MIME: {mime_type})")
            return None
            
    except Exception as e:
        logger.warning(f"Erro ao validar arquivo {file_path}: {e}")
        return None
    
    # Converter caminho absoluto para URL da API
    try:
        encoded_path = urllib.parse.quote(file_path, safe='')
        clean_url = f"/api/image?path={encoded_path}"
        logger.info(f"URL criada: {file_obj.name} -> {clean_url[:50]}...")
        return clean_url
    except Exception as e:
        logger.warning(f"Erro ao criar URL para {file_path}: {e}")
        return None

# Criar aplicação FastAPI
app = FastAPI(
    title="Ohara - Manga Reader API",
    description="API para leitor de mangás local",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://127.0.0.1:5173",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.include_router(reader_router, prefix="/api", tags=["reader"])

# Instância global do scanner
scanner = MangaScanner()

# Carregar caminho salvo na inicialização
library_state.load_from_file()

@app.get("/")
async def root():
    return {
        "message": "🏴‍☠️ Ohara - Manga Reader API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/api/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "ohara-manga-reader",
        "message": "API funcionando perfeitamente!"
    }

@app.get("/api/test")
async def test_endpoint():
    return {
        "message": "API Ohara funcionando!",
        "backend": "FastAPI",
        "scanner": "MangaScanner",
        "status": "OK",
        "tip": "Use /api/scan-library para escanear uma pasta real"
    }

@app.post("/api/clear-library")
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
    
    logger.info(f"[{method}] Escaneando biblioteca: {library_path}")
    logger.info(f"[{method}] Subpastas encontradas: {len(subdirs)}")
    
    library = scanner.scan_library(str(path_obj))
    
    for manga in library.mangas:
        if manga.thumbnail:
            logger.info(f"Mantendo thumbnails como caminhos absolutos")
    
    # Atualizar caminho atual SOMENTE após sucesso
    library_state.current_path = str(path_obj)
    
    if method == "GET":
        # Salvar caminho para próximas execuções
        save_library_path(str(path_obj))
    
    logger.info(f"[{method}] Biblioteca escaneada: {library.total_mangas} mangás encontrados")
    
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


@app.post("/api/scan-library")
async def scan_library_path(library_path: str = Form(...)):
    """
    Args:
        library_path: Caminho absoluto para a pasta da biblioteca
    
    Returns:
        LibraryResponse: Biblioteca escaneada com mangás encontrados
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
        logger.info(f"Traceback completo:\n{traceback.format_exc()}")
        
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Erro interno do servidor",
                "message": str(e),
                "tip": "Verifique se o caminho existe e você tem permissões de leitura. Caracteres especiais podem causar problemas.",
                "received_path": library_path
            }
        )

@app.get("/api/scan-library")
async def scan_library_get(path: str):
    """
    Endpoint GET para escanear biblioteca (compatibilidade com frontend)
    Redireciona para a implementação POST principal
    """
    try:
        response_data = _scan_library_common(path, "GET")
        return JSONResponse(content=jsonable_encoder(response_data))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"[GET] Erro ao escanear biblioteca: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Erro interno do servidor",
                "message": str(e),
                "received_path": path,
                "method": "GET"
            }
        )

@app.get("/api/library")
async def get_library():
    """
    Retorna a biblioteca atual 
    """
    
    # Se há uma biblioteca configurada, reescanear
    if library_state.current_path and Path(library_state.current_path).exists():
        try:
            library = scanner.scan_library(library_state.current_path)
            
            optimized_mangas = []
            for manga in library.mangas:
                thumbnail_url = None
                if manga.thumbnail:
                    thumbnail_url = create_image_url(manga.thumbnail)
                    if thumbnail_url:
                        logger.info(f"Thumbnail URL criada: {manga.title}")
                    else:
                        logger.info(f"Thumbnail inválida para {manga.title}: {manga.thumbnail}")
                else:
                    logger.info(f"Thumbnail não encontrada para {manga.title}: {manga.thumbnail}")
                
                optimized_manga = {
                    "id": manga.id,
                    "title": manga.title,
                    "chapter_count": manga.chapter_count,
                    "total_pages": manga.total_pages,
                    "thumbnail": thumbnail_url,  
                    "path": manga.path
                }
                optimized_mangas.append(optimized_manga)

            response_data = {
                "mangas": optimized_mangas,
                "total_mangas": library.total_mangas,
                "total_chapters": library.total_chapters,
                "total_pages": library.total_pages,
                "message": f"Biblioteca com {library.total_mangas} mangás",
                "scanned_path": library_state.current_path,
                "last_updated": library.last_updated.isoformat(),
            }
            
            return JSONResponse(content=jsonable_encoder(response_data))
            
        except Exception as e:
            logger.warning(f"Erro ao recarregar biblioteca: {str(e)}")
            library_state.clear()
            library_state.clear()
    
    # Se não há biblioteca, retornar biblioteca vazia
    return JSONResponse(content={
        "mangas": [],
        "total_mangas": 0,
        "total_chapters": 0,
        "total_pages": 0,
        "message": "Configure uma biblioteca para começar",
    })

@app.get("/api/manga/{manga_id}")
async def get_manga(manga_id: str):
    """
    Retorna detalhes completos de um mangá específico
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
            detail=f"Erro ao buscar mangá: {str(e)}"
        )

@app.get("/api/validate-path")
async def validate_library_path(path: str):
    """
    Valida se um caminho é válido para biblioteca
    """
    try:
        is_valid, message = scanner.validate_library_path(path)
        
        return {
            "valid": is_valid,
            "message": message,
            "path": path,
            "exists": Path(path).exists(),
            "is_directory": Path(path).is_dir() if Path(path).exists() else False,
            "readable": os.access(path, os.R_OK) if Path(path).exists() else False
        }
        
    except Exception as e:
        return {
            "valid": False,
            "message": f"Erro ao validar caminho: {str(e)}",
            "path": path,
            "exists": False,
            "is_directory": False,
            "readable": False
        }

@app.get("/api/image")
async def serve_image(path: str):
    try:
        logger.info(f"[IMAGE] Path recebido: {path}")
        
        if not library_state.current_path:
            raise HTTPException(status_code=400, detail="Biblioteca não configurada")
        
        decoded_path = urllib.parse.unquote(path)
        logger.info(f"[IMAGE] Path decodificado: {decoded_path}")
        
        # Detectar e corrigir duplo encoding
        if "/api/image?path=" in decoded_path:
            logger.info("[IMAGE] Corrigindo duplo encoding...")
            import urllib.parse as urlparse
            parsed = urlparse.urlparse(decoded_path)
            if parsed.query:
                query_params = urlparse.parse_qs(parsed.query)
                if 'path' in query_params:
                    decoded_path = query_params['path'][0]
                    logger.info(f"[IMAGE] Caminho real extraído: {decoded_path}")
                else:
                    raise HTTPException(status_code=400, detail="Parâmetro 'path' não encontrado")
        
        # Resolver caminhos absolutos
        file_path = Path(decoded_path).resolve()
        library_root = Path(library_state.current_path).resolve()
        
        logger.info(f"[IMAGE] Arquivo: {file_path}")
        logger.info(f"[IMAGE] Biblioteca: {library_root}")
        
        # Validar que está dentro da biblioteca
        if not str(file_path).startswith(str(library_root)):
            logger.info(f"Path fora da biblioteca: {file_path}")
            raise HTTPException(status_code=404, detail="Arquivo não encontrado")
        
        # Validar que existe e é arquivo
        if not file_path.exists() or not file_path.is_file():
            logger.info(f"Arquivo não encontrado: {file_path}")
            raise HTTPException(status_code=404, detail="Arquivo não encontrado")
        
        logger.info(f"Servindo imagem: {file_path.name}")
        return FileResponse(path=str(file_path))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Erro inesperado: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.get("/api/debug")
async def debug_info():
    """
    Endpoint de debug para verificar estado do backend
    """
    
    return {
        "current_library_path": library_state.current_path,
        "path_file_exists": Path(last_library_path.txt).exists(),
        "path_file_content": Path(last_library_path.txt).read_text() if Path(last_library_path.txt).exists() else None,
        "path_is_valid": library_state.validate_current_path(),
        "message": "Debug info"
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

# === ENDPOINTS DE CACHE  ===

@app.get("/api/cache/info")
async def get_cache_info():
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
            "scanner_version": "Cache Híbrido v1.0"
        }
        
    except Exception as e:
        return {
            "cache_enabled": scanner.cache_enabled,
            "current_library": library_state.current_path,
            "cache_info": {"exists": False, "error": str(e)},
            "scanner_version": "Cache Híbrido v1.0"
        }

@app.post("/api/cache/clear")
async def clear_cache():
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

@app.post("/api/cache/disable")
async def disable_cache():
    try:
        scanner.disable_cache()
        
        return {
            "message": "Cache híbrido desabilitado",
            "cache_enabled": False,
            "status": "disabled"
        }
        
    except Exception as e:
        logger.warning(f"Erro ao desabilitar cache: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao desabilitar cache: {str(e)}"
        )

@app.post("/api/cache/enable")
async def enable_cache():
    try:
        scanner.enable_cache()
        
        return {
            "message": "Cache híbrido habilitado",
            "cache_enabled": True,
            "status": "enabled"
        }
        
    except Exception as e:
        logger.warning(f"Erro ao habilitar cache: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao habilitar cache: {str(e)}"
        )

@app.get("/api/debug/performance")
async def debug_performance():
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
    
@app.get("/api/preview-library")
async def preview_library(path: str):
    try:
        # Validar primeiro
        is_valid, message = scanner.validate_library_path(path)
        
        if not is_valid:
            return {
                "valid": False,
                "message": message,
                "mangas": []
            }
        
        # Buscar diretórios que parecem mangás
        library_path = Path(path)
        potential_mangas = []
        
        for item in library_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                # Verificar se tem subpastas (capítulos) ou imagens
                has_chapters = any(sub.is_dir() for sub in item.iterdir() if not sub.name.startswith('.'))
                has_images = any(
                    sub.is_file() and sub.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp']
                    for sub in item.iterdir()
                )
                
                if has_chapters or has_images:
                    potential_mangas.append({
                        "name": item.name,
                        "title": item.name,
                        "path": str(item),
                        "has_chapters": has_chapters,
                        "has_images": has_images
                    })
        
        return {
            "valid": True,
            "message": f"Encontrados {len(potential_mangas)} mangás",
            "mangas": potential_mangas[:20],  # Limitar a 20 para preview
            "total_found": len(potential_mangas)
        }
        
    except Exception as e:
        return {
            "valid": False,
            "message": f"Erro ao fazer preview: {str(e)}",
            "mangas": []
        }

@app.post("/api/set-library-path")
async def set_library_path(data: dict):
    try:
        path = data.get("path")
        if not path:
            return {"success": False, "message": "Caminho não fornecido"}
        
        # Validar caminho
        is_valid, message = scanner.validate_library_path(path)
        if not is_valid:
            return {"success": False, "message": message}
        
        # Futuramente será salvo a configuração (arquivo, banco, etc.)
        # Por enquanto, apenas validação
        return {
            "success": True,
            "message": "Biblioteca configurada com sucesso",
            "path": path
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Erro ao configurar biblioteca: {str(e)}"
        }
    
@app.get("/api/debug/thumbnails")
async def debug_thumbnails():
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
    

@app.get("/api/debug/reader")
async def debug_reader_info():
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