from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.encoders import jsonable_encoder
from pathlib import Path
import os
from typing import Optional
from datetime import datetime
import mimetypes
import urllib.parse
from app.core.services.manga_scanner import MangaScanner

# Imports locais
from .core.services.manga_scanner import MangaScanner
from .models.manga import LibraryResponse, MangaResponse

def create_image_url(file_path: str) -> str:
    """
    Cria URL limpa para servir imagens, evitando duplicação
    
    Args:
        file_path: Caminho absoluto do arquivo
        
    Returns:
        str: URL da API para servir a imagem ou None
    """
    if not file_path:
        return None
    
    if file_path.startswith('/api/image') or file_path.startswith('http'):
        print(f"⚠️ URL já processada detectada: {file_path[:50]}...")
        return None
    
    try:
        file_obj = Path(file_path)
        if not file_obj.exists() or not file_obj.is_file():
            print(f"⚠️ Arquivo não existe: {file_path}")
            return None
            
        # Verificar se é imagem
        import mimetypes
        mime_type, _ = mimetypes.guess_type(str(file_obj))
        if not mime_type or not mime_type.startswith('image/'):
            print(f"⚠️ Não é imagem: {file_path} (MIME: {mime_type})")
            return None
            
    except Exception as e:
        print(f"⚠️ Erro ao validar arquivo {file_path}: {e}")
        return None
    
    # Converter caminho absoluto para URL da API
    try:
        import urllib.parse
        # Encoding completo para evitar problemas
        encoded_path = urllib.parse.quote(file_path, safe='')
        clean_url = f"/api/image?path={encoded_path}"
        print(f"✅ URL criada: {file_obj.name} -> URL válida")
        return clean_url
    except Exception as e:
        print(f"❌ Erro ao criar URL para {file_path}: {e}")
        return None

# Criar aplicação FastAPI
app = FastAPI(
    title="Ohara - Manga Reader API",
    description="API para leitor de mangás local (Projeto ES2)",
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

# Instância global do scanner
scanner = MangaScanner()

# Variável para armazenar o caminho da biblioteca atual
CURRENT_LIBRARY_PATH: Optional[str] = None

# Arquivo para persistir o caminho da biblioteca
LIBRARY_PATH_FILE = "last_library_path.txt"

def load_library_path() -> Optional[str]:
    """Carrega o último caminho de biblioteca usado"""
    try:
        if Path(LIBRARY_PATH_FILE).exists():
            with open(LIBRARY_PATH_FILE, 'r', encoding='utf-8') as f:
                path = f.read().strip()
                if path and Path(path).exists():
                    print(f"📂 Carregado caminho salvo: {path}")
                    return path
                else:
                    print(f"⚠️ Caminho salvo não existe mais: {path}")
    except Exception as e:
        print(f"❌ Erro ao carregar caminho salvo: {e}")
    return None

def save_library_path(path: str):
    """Salva o caminho da biblioteca para próximas execuções"""
    try:
        with open(LIBRARY_PATH_FILE, 'w', encoding='utf-8') as f:
            f.write(path)
        print(f"💾 Caminho salvo: {path}")
    except Exception as e:
        print(f"❌ Erro ao salvar caminho: {e}")

def clear_library_path():
    """Remove o arquivo de caminho salvo"""
    try:
        if Path(LIBRARY_PATH_FILE).exists():
            Path(LIBRARY_PATH_FILE).unlink()
            print(f"🗑️ Arquivo de caminho removido: {LIBRARY_PATH_FILE}")
    except Exception as e:
        print(f"❌ Erro ao remover arquivo de caminho: {e}")

# Carregar caminho salvo na inicialização
CURRENT_LIBRARY_PATH = load_library_path()

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
        "message": "API funcionando perfeitamente! 🚀"
    }

@app.get("/api/test")
async def test_endpoint():
    return {
        "message": "🎉 API Ohara funcionando!",
        "backend": "FastAPI ✅",
        "scanner": "MangaScanner ✅",
        "status": "OK",
        "tip": "Use /api/scan-library para escanear uma pasta real"
    }

@app.post("/api/clear-library")
async def clear_library():
    """
    Limpa a biblioteca atual no backend
    """
    global CURRENT_LIBRARY_PATH
    
    try:
        print("🧹 Limpando biblioteca no backend...")
        
        # Limpar variável global
        CURRENT_LIBRARY_PATH = None
        
        # Remover arquivo de cache
        clear_library_path()
        
        print("✅ Biblioteca limpa no backend")
        
        return {
            "message": "Biblioteca limpa com sucesso",
            "current_path": None,
            "status": "cleared"
        }
        
    except Exception as e:
        print(f"❌ Erro ao limpar biblioteca: {str(e)}")
        return {
            "message": f"Erro ao limpar biblioteca: {str(e)}",
            "status": "error"
        }

@app.post("/api/scan-library")
async def scan_library_path(library_path: str = Form(...)):
    """
    Escaneia uma pasta de biblioteca de mangás
    
    Args:
        library_path: Caminho absoluto para a pasta da biblioteca
    
    Returns:
        LibraryResponse: Biblioteca escaneada com mangás encontrados
    """
    global CURRENT_LIBRARY_PATH
    
    try:
        # Limpar e normalizar o caminho
        library_path = library_path.strip()
        
        # Log para debug
        print(f"📥 Caminho recebido: '{library_path}'")
        print(f"📏 Comprimento: {len(library_path)} caracteres")
        print(f"🔤 Encoding: {library_path.encode('utf-8')}")
        
        # IMPORTANTE: Limpar biblioteca anterior primeiro
        if CURRENT_LIBRARY_PATH != library_path:
            print(f"🔄 Mudando biblioteca de '{CURRENT_LIBRARY_PATH}' para '{library_path}'")
            CURRENT_LIBRARY_PATH = None
            clear_library_path()
        
        # Validar se o caminho existe - com tratamento melhor de Unicode
        try:
            path_obj = Path(library_path)
            print(f"📁 Path object criado: {path_obj}")
            print(f"🔍 Absolute path: {path_obj.absolute()}")
            
        except Exception as path_error:
            print(f"❌ Erro ao criar Path object: {path_error}")
            raise HTTPException(
                status_code=400,
                detail=f"Caminho inválido (erro de encoding): {library_path}"
            )
        
        if not path_obj.exists():
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
                        print(f"✅ Caminho encontrado com encoding alternativo: {library_path}")
                        break
                except:
                    continue
            
            if not path_found:
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
        
        print(f"🔍 Escaneando biblioteca: {library_path}")
        print(f"📂 Subpastas encontradas: {len(subdirs)}")
        
        # Escanear biblioteca usando o scanner real
        library = scanner.scan_library(str(path_obj))
        
        # Converter thumbnails para URLs da API
        for manga in library.mangas:
            if manga.thumbnail:
                print(f"✅ Mantendo thumbnails como caminhos absolutos")
        
        # Atualizar caminho atual SOMENTE após sucesso
        CURRENT_LIBRARY_PATH = str(path_obj)
        
        # Salvar caminho para próximas execuções
        save_library_path(str(path_obj))
        
        print(f"✅ Biblioteca escaneada: {library.total_mangas} mangás encontrados")
        
        # Converter para resposta da API com encoding seguro
        response_data = {
            "library": {
                "mangas": [jsonable_encoder(manga.model_dump()) for manga in library.mangas],
                "total_mangas": library.total_mangas,
                "total_chapters": library.total_chapters,
                "total_pages": library.total_pages,
                "last_updated": library.last_updated.isoformat()
            },
            "message": f"Biblioteca escaneada com sucesso! {library.total_mangas} mangás encontrados.",
            "scanned_path": str(path_obj),
            "timestamp": library.last_updated.isoformat()
        }
        
        return JSONResponse(content=jsonable_encoder(response_data))
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erro ao escanear biblioteca: {str(e)}")
        print(f"📋 Tipo do erro: {type(e).__name__}")
        import traceback
        print(f"📄 Traceback completo:\n{traceback.format_exc()}")
        
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
        # Chama a função principal usando FormData internamente
        from fastapi import Form
        
        # Simular FormData para reutilizar a lógica existente
        library_path = path
        
        # Reutilizar toda a lógica do POST
        global CURRENT_LIBRARY_PATH
        
        # Limpar e normalizar o caminho
        library_path = library_path.strip()
        
        # Log para debug
        print(f"📥 [GET] Caminho recebido: '{library_path}'")
        
        # IMPORTANTE: Limpar biblioteca anterior primeiro
        if CURRENT_LIBRARY_PATH != library_path:
            print(f"🔄 [GET] Mudando biblioteca de '{CURRENT_LIBRARY_PATH}' para '{library_path}'")
            CURRENT_LIBRARY_PATH = None
            clear_library_path()
        
        # Validar se o caminho existe
        path_obj = Path(library_path)
        print(f"📁 [GET] Path object criado: {path_obj}")
        
        if not path_obj.exists():
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
        
        print(f"🔍 [GET] Escaneando biblioteca: {library_path}")
        print(f"📂 [GET] Subpastas encontradas: {len(subdirs)}")
        
        # Escanear biblioteca usando o scanner real
        library = scanner.scan_library(str(path_obj))
        
        # Converter thumbnails para URLs da API
        for manga in library.mangas:
            if manga.thumbnail:
                print(f"✅ Mantendo thumbnails como caminhos absolutos")

        
        # Atualizar caminho atual SOMENTE após sucesso
        CURRENT_LIBRARY_PATH = str(path_obj)
        
        # Salvar caminho para próximas execuções
        save_library_path(str(path_obj))
        
        print(f"✅ [GET] Biblioteca escaneada: {library.total_mangas} mangás encontrados")
        
        # Converter para resposta da API
        response_data = {
            "library": {
                "mangas": [jsonable_encoder(manga.model_dump()) for manga in library.mangas],
                "total_mangas": library.total_mangas,
                "total_chapters": library.total_chapters,
                "total_pages": library.total_pages,
                "last_updated": library.last_updated.isoformat()
            },
            "message": f"Biblioteca escaneada com sucesso! {library.total_mangas} mangás encontrados.",
            "scanned_path": str(path_obj),
            "timestamp": library.last_updated.isoformat(),
            "method": "GET"
        }
        
        return JSONResponse(content=jsonable_encoder(response_data))
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ [GET] Erro ao escanear biblioteca: {str(e)}")
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
    Retorna a biblioteca atual (escaneada ou dados mock)
    """
    global CURRENT_LIBRARY_PATH
    
    # Se há uma biblioteca configurada, reescanear
    if CURRENT_LIBRARY_PATH and Path(CURRENT_LIBRARY_PATH).exists():
        try:
            library = scanner.scan_library(CURRENT_LIBRARY_PATH)
            
            # Criar resposta otimizada COM thumbnails funcionais
            optimized_mangas = []
            for manga in library.mangas:
                # ✅ CORREÇÃO: Verificar se thumbnail existe antes de criar URL
                thumbnail_url = None
                if manga.thumbnail:
                    thumbnail_url = create_image_url(manga.thumbnail)
                    if thumbnail_url:
                        print(f"📸 Thumbnail URL criada: {manga.title}")
                    else:
                        print(f"⚠️ Thumbnail inválida para {manga.title}: {manga.thumbnail}")
                else:
                    print(f"❌ Thumbnail não encontrada para {manga.title}: {manga.thumbnail}")
                
                optimized_manga = {
                    "id": manga.id,
                    "title": manga.title,
                    "chapter_count": manga.chapter_count,
                    "total_pages": manga.total_pages,
                    "thumbnail": thumbnail_url,  # ✅ CORRIGIDO: URL ou None
                    "path": manga.path
                }
                optimized_mangas.append(optimized_manga)

            response_data = {
                "mangas": optimized_mangas,
                "total_mangas": library.total_mangas,
                "total_chapters": library.total_chapters,
                "total_pages": library.total_pages,
                "message": f"Biblioteca com {library.total_mangas} mangás",
                "scanned_path": CURRENT_LIBRARY_PATH,
                "last_updated": library.last_updated.isoformat(),
                "is_mock": False
            }
            
            return JSONResponse(content=jsonable_encoder(response_data))
            
        except Exception as e:
            print(f"❌ Erro ao recarregar biblioteca: {str(e)}")
            # Se falhar, limpar caminho e usar mock
            CURRENT_LIBRARY_PATH = None
            clear_library_path()
    
    # Mock data (inalterado)
    mock_library = {
        "mangas": [
            {
                "id": "one-piece",
                "title": "One Piece",
                "chapter_count": 1095,
                "thumbnail": None,
                "last_chapter": "Capítulo 1095",
                "path": "/mock/One Piece"
            },
            {
                "id": "naruto",
                "title": "Naruto", 
                "chapter_count": 700,
                "thumbnail": None,
                "last_chapter": "Capítulo 700",
                "path": "/mock/Naruto"
            },
            {
                "id": "attack-on-titan",
                "title": "Attack on Titan",
                "chapter_count": 139,
                "thumbnail": None,
                "last_chapter": "Capítulo 139",
                "path": "/mock/Attack on Titan"
            }
        ],
        "total_mangas": 3,
        "message": "📚 Configure uma biblioteca real para começar",
        "is_mock": True
    }
    return JSONResponse(content=mock_library)

@app.get("/api/manga/{manga_id}")
async def get_manga(manga_id: str):
    """
    Retorna detalhes de um mangá específico
    """
    global CURRENT_LIBRARY_PATH
    
    # Se não há biblioteca escaneada, retornar dados mock
    if CURRENT_LIBRARY_PATH is None:
        mock_manga = {
            "id": manga_id,
            "title": manga_id.replace("-", " ").title(),
            "chapters": [
                {"id": f"{manga_id}-ch-5", "name": "Capítulo 5", "number": 5, "pages": 20},
                {"id": f"{manga_id}-ch-4", "name": "Capítulo 4", "number": 4, "pages": 18},
                {"id": f"{manga_id}-ch-3", "name": "Capítulo 3", "number": 3, "pages": 22},
                {"id": f"{manga_id}-ch-2", "name": "Capítulo 2", "number": 2, "pages": 19},
                {"id": f"{manga_id}-ch-1", "name": "Capítulo 1", "number": 1, "pages": 25}
            ],
            "thumbnail": None,
            "chapter_count": 5,
            "message": f"Dados mock para {manga_id} - Escaneie uma biblioteca real",
            "is_mock": True
        }
        return JSONResponse(content=mock_manga)
    
    # Buscar mangá real na biblioteca escaneada
    try:
        library = scanner.scan_library(CURRENT_LIBRARY_PATH)
        manga = library.get_manga(manga_id)
        
        if not manga:
            raise HTTPException(
                status_code=404,
                detail=f"Mangá '{manga_id}' não encontrado na biblioteca"
            )
        
        # Converter thumbnails e páginas para URLs da API
        if manga.thumbnail:
            manga.thumbnail = f"/api/image?path={manga.thumbnail}"
        
        for chapter in manga.chapters:
            for page in chapter.pages:
                page.path = f"/api/image?path={page.path}"
        
        response_data = {
            "manga": jsonable_encoder(manga.model_dump()),
            "message": f"Detalhes do mangá '{manga.title}' carregados",
            "is_mock": False
        }
        
        return JSONResponse(content=jsonable_encoder(response_data))
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erro ao buscar mangá {manga_id}: {str(e)}")
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
    """Serve imagens - versão simplificada"""
    try:
        print(f"🖼️ [IMAGE] Path recebido: {path}")
        
        # Decodificar URL
        import urllib.parse
        decoded_path = urllib.parse.unquote(path)
        print(f"🖼️ [IMAGE] Path decodificado: {decoded_path}")
        
        # Servir arquivo diretamente
        file_path = Path(decoded_path)
        
        if not file_path.exists():
            print(f"❌ Arquivo não encontrado: {decoded_path}")
            raise HTTPException(status_code=404, detail="Arquivo não encontrado")
        
        print(f"✅ Servindo: {file_path.name}")
        return FileResponse(path=str(file_path))
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/debug")
async def debug_info():
    """
    Endpoint de debug para verificar estado do backend
    """
    global CURRENT_LIBRARY_PATH
    
    return {
        "current_library_path": CURRENT_LIBRARY_PATH,
        "path_file_exists": Path(LIBRARY_PATH_FILE).exists(),
        "path_file_content": Path(LIBRARY_PATH_FILE).read_text() if Path(LIBRARY_PATH_FILE).exists() else None,
        "path_is_valid": Path(CURRENT_LIBRARY_PATH).exists() if CURRENT_LIBRARY_PATH else False,
        "message": "Debug info"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
# === ENDPOINTS DE CACHE - ADICIONAR AO FINAL DO main.py ===

@app.get("/api/cache/info")
async def get_cache_info():
    """
    Obter informações sobre o cache da biblioteca atual
    """
    global CURRENT_LIBRARY_PATH
    
    if not CURRENT_LIBRARY_PATH:
        return {
            "cache_enabled": True,
            "current_library": None,
            "cache_info": {"exists": False}
        }
    
    try:
        cache_info = scanner.get_cache_info(CURRENT_LIBRARY_PATH)
        
        return {
            "cache_enabled": scanner.cache_enabled,
            "current_library": CURRENT_LIBRARY_PATH,
            "cache_info": cache_info,
            "scanner_version": "Cache Híbrido v1.0"
        }
        
    except Exception as e:
        return {
            "cache_enabled": scanner.cache_enabled,
            "current_library": CURRENT_LIBRARY_PATH,
            "cache_info": {"exists": False, "error": str(e)},
            "scanner_version": "Cache Híbrido v1.0"
        }

@app.post("/api/cache/clear")
async def clear_cache():
    """
    Limpar cache da biblioteca atual
    """
    global CURRENT_LIBRARY_PATH
    
    if not CURRENT_LIBRARY_PATH:
        raise HTTPException(
            status_code=400,
            detail="Nenhuma biblioteca configurada"
        )
    
    try:
        success = scanner.clear_cache(CURRENT_LIBRARY_PATH)
        
        if success:
            return {
                "message": "Cache limpo com sucesso",
                "library_path": CURRENT_LIBRARY_PATH,
                "status": "cleared"
            }
        else:
            return {
                "message": "Nenhum cache encontrado para limpar",
                "library_path": CURRENT_LIBRARY_PATH,
                "status": "no_cache"
            }
            
    except Exception as e:
        print(f"❌ Erro ao limpar cache: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao limpar cache: {str(e)}"
        )

@app.post("/api/cache/disable")
async def disable_cache():
    """
    Desabilitar cache híbrido (para debug/troubleshooting)
    """
    try:
        scanner.disable_cache()
        
        return {
            "message": "Cache híbrido desabilitado",
            "cache_enabled": False,
            "status": "disabled"
        }
        
    except Exception as e:
        print(f"❌ Erro ao desabilitar cache: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao desabilitar cache: {str(e)}"
        )

@app.post("/api/cache/enable")
async def enable_cache():
    """
    Reabilitar cache híbrido
    """
    try:
        scanner.enable_cache()
        
        return {
            "message": "Cache híbrido habilitado",
            "cache_enabled": True,
            "status": "enabled"
        }
        
    except Exception as e:
        print(f"❌ Erro ao habilitar cache: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao habilitar cache: {str(e)}"
        )

@app.get("/api/debug/performance")
async def debug_performance():
    """
    Endpoint de debug para analisar performance do scanner
    """
    global CURRENT_LIBRARY_PATH
    
    if not CURRENT_LIBRARY_PATH:
        return {
            "error": "Nenhuma biblioteca configurada",
            "current_library": None
        }
    
    try:
        import time
        from pathlib import Path
        
        library_path = Path(CURRENT_LIBRARY_PATH)
        
        # Contar estrutura rapidamente
        manga_count = len([d for d in library_path.iterdir() if d.is_dir() and not d.name.startswith('.')])
        
        # Verificar cache
        cache_info = scanner.get_cache_info(CURRENT_LIBRARY_PATH)
        
        # Estimativas de performance
        estimated_time_with_cache = 0.1 if cache_info["exists"] else None
        estimated_time_without_cache = manga_count * 0.3  # ~300ms por mangá
        
        return {
            "library_path": CURRENT_LIBRARY_PATH,
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
        print(f"❌ Erro no debug de performance: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro no debug: {str(e)}"
        )
    
@app.get("/api/preview-library")
async def preview_library(path: str):
    """Preview dos mangás que seriam encontrados no caminho"""
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
    """Define o caminho da biblioteca"""
    try:
        path = data.get("path")
        if not path:
            return {"success": False, "message": "Caminho não fornecido"}
        
        # Validar caminho
        is_valid, message = scanner.validate_library_path(path)
        if not is_valid:
            return {"success": False, "message": message}
        
        # Aqui você salvaria a configuração (arquivo, banco, etc.)
        # Por enquanto, vamos apenas validar
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
    """Debug das thumbnails da biblioteca atual"""
    global CURRENT_LIBRARY_PATH
    
    if not CURRENT_LIBRARY_PATH:
        return {"error": "Nenhuma biblioteca configurada"}
    
    try:
        library = scanner.scan_library(CURRENT_LIBRARY_PATH)
        
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
            "library_path": CURRENT_LIBRARY_PATH,
            "total_mangas": len(debug_info),
            "thumbnails": debug_info
        }
        
    except Exception as e:
        return {"error": str(e)}