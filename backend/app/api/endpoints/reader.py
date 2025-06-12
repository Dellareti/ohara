# ARQUIVO COMPLETO CORRIGIDO: backend/app/api/endpoints/reader.py

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional, List
import json
import re
from pathlib import Path
from datetime import datetime

from app.core.services.manga_scanner import MangaScanner
from app.models.manga import Chapter, Page

def chapter_to_dict(chapter) -> dict:
    """
    Converte um objeto Chapter para dict com serialização adequada de datetime
    """
    return {
        "id": chapter.id,
        "name": chapter.name,
        "number": chapter.number,
        "volume": chapter.volume,
        "path": chapter.path,
        "page_count": chapter.page_count,
        "date_added": chapter.date_added.isoformat() if chapter.date_added else None,
        "pages": [
            {
                "filename": page.filename,
                "path": page.path,
                "size": page.size,
                "width": page.width,
                "height": page.height
            }
            for page in chapter.pages
        ]
    }

router = APIRouter()
scanner = MangaScanner()

# Cache global para dados de capítulos
_chapter_cache = {}

def _find_chapter_flexible(manga, chapter_id: str):
    """
    ✅ NOVA FUNÇÃO: Busca capítulo por múltiplos critérios
    
    Aceita:
    - ID exato: "kagurabachi-ch-78.0"
    - Slug customizado: "sirius-scanlator-chapter-78-substituicao"  
    - Por número: "78", "78.0"
    - Por nome parcial: "Chapter 78"
    """
    
    print(f"🔍 Buscando capítulo: '{chapter_id}'")
    
    # 1. Busca por ID exato (mais rápida)
    for chapter in manga.chapters:
        if chapter.id == chapter_id:
            print(f"✅ Encontrado por ID exato: {chapter.id}")
            return chapter
    
    # 2. Busca por número do capítulo
    try:
        # Tentar extrair número do chapter_id
        numbers = re.findall(r'(\d+(?:\.\d+)?)', chapter_id)
        if numbers:
            search_number = float(numbers[0])
            for chapter in manga.chapters:
                if chapter.number == search_number:
                    print(f"✅ Encontrado por número: {chapter.number} -> {chapter.id}")
                    return chapter
    except Exception as e:
        print(f"⚠️ Erro na busca por número: {e}")
    
    # 3. Busca por nome parcial (fallback)
    chapter_id_lower = chapter_id.lower()
    for chapter in manga.chapters:
        chapter_name_lower = chapter.name.lower()
        
        # Remover caracteres especiais para comparação
        clean_id = re.sub(r'[^\w\s]', '', chapter_id_lower)
        clean_name = re.sub(r'[^\w\s]', '', chapter_name_lower)
        
        if clean_id in clean_name or clean_name in clean_id:
            print(f"✅ Encontrado por nome parcial: '{chapter_id}' -> {chapter.id}")
            return chapter
    
    # 4. Busca por palavras-chave
    words_in_id = chapter_id_lower.split('-')
    for chapter in manga.chapters:
        chapter_words = re.split(r'[\s\-_]+', chapter.name.lower())
        
        # Se pelo menos 2 palavras coincidirem
        matches = sum(1 for word in words_in_id if word in chapter_words)
        if matches >= 2:
            print(f"✅ Encontrado por palavras-chave ({matches} matches): {chapter.id}")
            return chapter
    
    # 5. Não encontrado
    print(f"❌ Capítulo não encontrado: '{chapter_id}'")
    print(f"📚 Capítulos disponíveis:")
    for i, ch in enumerate(manga.chapters[:5]):  # Mostrar primeiros 5
        print(f"  {i+1}. ID: '{ch.id}' | Nome: '{ch.name}' | Número: {ch.number}")
    
    return None

@router.get("/manga/{manga_id}/chapter/{chapter_id}")
async def get_chapter(manga_id: str, chapter_id: str):
    """
    Retorna dados completos de um capítulo específico
    ✅ CORRIGIDO: Aceita múltiplos formatos de chapter_id
    """
    from app.core.library_state import library_state
    
    if not library_state.current_path:
        raise HTTPException(
            status_code=400,
            detail="Nenhuma biblioteca configurada"
        )
    
    try:
        print(f"📖 Requisição de capítulo: {manga_id}/{chapter_id}")
        
        # Verificar cache primeiro
        cache_key = f"{manga_id}_{chapter_id}"
        if cache_key in _chapter_cache:
            print(f"📋 Cache hit para capítulo: {chapter_id}")
            return _chapter_cache[cache_key]
        
        # Escanear biblioteca para encontrar o capítulo
        library = scanner.scan_library(library_state.current_path)
        manga = library.get_manga(manga_id)
        
        if not manga:
            raise HTTPException(
                status_code=404,
                detail=f"Mangá '{manga_id}' não encontrado"
            )
        
        # ✅ CORREÇÃO: Buscar capítulo por múltiplos critérios
        chapter = _find_chapter_flexible(manga, chapter_id)
        
        if not chapter:
            # ✅ DEBUG: Mostrar capítulos disponíveis
            available_chapters = [{"id": ch.id, "name": ch.name, "number": ch.number} for ch in manga.chapters[:10]]
            
            raise HTTPException(
                status_code=404,
                detail={
                    "error": f"Capítulo '{chapter_id}' não encontrado",
                    "manga_id": manga_id,
                    "requested_chapter_id": chapter_id,
                    "available_chapters": available_chapters,
                    "total_chapters": len(manga.chapters)
                }
            )
        
        # Converter caminhos das páginas para URLs da API
        chapter_data = chapter_to_dict(chapter)
        for page in chapter_data['pages']:
            # Corrigir URLs das páginas
            if not page['path'].startswith('/api/image'):
                page['url'] = f"/api/image?path={page['path']}"
            else:
                page['url'] = page['path']  # Já é uma URL da API
        
        # Adicionar informações extras
        response_data = {
            "chapter": chapter_data,
            "manga": {
                "id": manga.id,
                "title": manga.title,
                "total_chapters": manga.chapter_count
            },
            "navigation": {
                "previous_chapter": _find_previous_chapter(manga, chapter),
                "next_chapter": _find_next_chapter(manga, chapter),
                "chapter_index": _get_chapter_index(manga, chapter)
            },
            "message": f"Capítulo '{chapter.name}' carregado com sucesso"
        }
        
        # Salvar no cache
        _chapter_cache[cache_key] = response_data
        
        print(f"📖 Capítulo carregado: {chapter.name} ({len(chapter.pages)} páginas)")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erro ao carregar capítulo: {str(e)}")
        import traceback
        print(f"📄 Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao carregar capítulo: {str(e)}"
        )

@router.get("/manga/{manga_id}/chapters")
async def get_manga_chapters(manga_id: str, limit: int = Query(50, ge=1, le=200)):
    """
    Retorna lista de capítulos de um mangá (para navegação)
    """
    from app.core.library_state import library_state
    
    if not library_state.current_path:
        raise HTTPException(
            status_code=400,
            detail="Nenhuma biblioteca configurada"
        )
    
    try:
        library = scanner.scan_library(library_state.current_path)
        manga = library.get_manga(manga_id)
        
        if not manga:
            raise HTTPException(
                status_code=404,
                detail=f"Mangá '{manga_id}' não encontrado"
            )
        
        # Preparar lista de capítulos (sem páginas completas para performance)
        chapters_summary = []
        for chapter in manga.chapters[:limit]:
            chapter_summary = {
                "id": chapter.id,
                "name": chapter.name,
                "number": chapter.number,
                "volume": chapter.volume,
                "page_count": chapter.page_count,
                "date_added": chapter.date_added.isoformat() if chapter.date_added else None,
                "thumbnail": chapter.pages[0].path if chapter.pages else None
            }
            
            # Converter thumbnail para URL
            if chapter_summary["thumbnail"]:
                chapter_summary["thumbnail_url"] = f"/api/image?path={chapter_summary['thumbnail']}"
            
            chapters_summary.append(chapter_summary)
        
        response_data = {
            "manga_id": manga_id,
            "manga_title": manga.title,
            "chapters": chapters_summary,
            "total_chapters": len(manga.chapters),
            "returned_count": len(chapters_summary)
        }
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erro ao listar capítulos: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao listar capítulos: {str(e)}"
        )

@router.post("/progress/{manga_id}/{chapter_id}")
async def save_reading_progress(
    manga_id: str, 
    chapter_id: str,
    current_page: int,
    total_pages: int,
    reading_time_seconds: Optional[int] = 0
):
    """
    Salva progresso de leitura de um capítulo
    """
    try:
        # Carregar progresso existente
        progress_file = Path("reading_progress.json")
        progress_data = {}
        
        if progress_file.exists():
            with open(progress_file, 'r', encoding='utf-8') as f:
                progress_data = json.load(f)
        
        # Atualizar progresso
        if manga_id not in progress_data:
            progress_data[manga_id] = {}
        
        progress_data[manga_id][chapter_id] = {
            "current_page": current_page,
            "total_pages": total_pages,
            "progress_percentage": round((current_page / max(total_pages - 1, 1)) * 100, 2),
            "is_completed": current_page >= total_pages - 1,
            "last_read": datetime.now().isoformat(),
            "reading_time_seconds": reading_time_seconds
        }
        
        # Atualizar progresso geral do mangá
        progress_data[manga_id]["_manga_info"] = {
            "last_chapter_read": chapter_id,
            "last_read": datetime.now().isoformat(),
            "total_reading_time": sum(
                ch.get("reading_time_seconds", 0) 
                for ch in progress_data[manga_id].values() 
                if isinstance(ch, dict) and "reading_time_seconds" in ch
            )
        }
        
        # Salvar arquivo
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Progresso salvo: {manga_id}/{chapter_id} - Página {current_page}/{total_pages}")
        
        return {
            "message": "Progresso salvo com sucesso",
            "progress": progress_data[manga_id][chapter_id]
        }
        
    except Exception as e:
        print(f"❌ Erro ao salvar progresso: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao salvar progresso: {str(e)}"
        )

@router.get("/progress/{manga_id}")
async def get_manga_progress(manga_id: str):
    """
    Retorna progresso de leitura de um mangá
    """
    try:
        progress_file = Path("reading_progress.json")
        
        if not progress_file.exists():
            return {
                "manga_id": manga_id,
                "chapters": {},
                "manga_info": {},
                "message": "Nenhum progresso encontrado"
            }
        
        with open(progress_file, 'r', encoding='utf-8') as f:
            progress_data = json.load(f)
        
        manga_progress = progress_data.get(manga_id, {})
        manga_info = manga_progress.pop("_manga_info", {})
        
        return {
            "manga_id": manga_id,
            "chapters": manga_progress,
            "manga_info": manga_info,
            "message": "Progresso carregado com sucesso"
        }
        
    except Exception as e:
        print(f"❌ Erro ao carregar progresso: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao carregar progresso: {str(e)}"
        )

@router.get("/progress/{manga_id}/{chapter_id}")
async def get_chapter_progress(manga_id: str, chapter_id: str):
    """
    Retorna progresso específico de um capítulo
    """
    try:
        progress_file = Path("reading_progress.json")
        
        if not progress_file.exists():
            return {
                "manga_id": manga_id,
                "chapter_id": chapter_id,
                "progress": None,
                "message": "Nenhum progresso encontrado"
            }
        
        with open(progress_file, 'r', encoding='utf-8') as f:
            progress_data = json.load(f)
        
        chapter_progress = progress_data.get(manga_id, {}).get(chapter_id)
        
        return {
            "manga_id": manga_id,
            "chapter_id": chapter_id,
            "progress": chapter_progress,
            "message": "Progresso do capítulo carregado" if chapter_progress else "Nenhum progresso encontrado"
        }
        
    except Exception as e:
        print(f"❌ Erro ao carregar progresso do capítulo: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao carregar progresso: {str(e)}"
        )

# Funções auxiliares
def _find_previous_chapter(manga, current_chapter):
    """Encontra o capítulo anterior"""
    chapters = manga.chapters
    for i, chapter in enumerate(chapters):
        if chapter.id == current_chapter.id and i < len(chapters) - 1:
            prev_ch = chapters[i + 1]  # Lista está em ordem decrescente
            return {
                "id": prev_ch.id,
                "name": prev_ch.name,
                "number": prev_ch.number
            }
    return None

def _find_next_chapter(manga, current_chapter):
    """Encontra o próximo capítulo"""
    chapters = manga.chapters
    for i, chapter in enumerate(chapters):
        if chapter.id == current_chapter.id and i > 0:
            next_ch = chapters[i - 1]  # Lista está em ordem decrescente
            return {
                "id": next_ch.id,
                "name": next_ch.name,
                "number": next_ch.number
            }
    return None

def _get_chapter_index(manga, current_chapter):
    """Retorna índice do capítulo na lista"""
    for i, chapter in enumerate(manga.chapters):
        if chapter.id == current_chapter.id:
            return {
                "current": i + 1,
                "total": len(manga.chapters)
            }
    return {"current": 0, "total": len(manga.chapters)}