import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from app.models.manga import Manga

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Gerenciador de cache híbrido para sistema de mangás.
    
    Responsável por:
    - Carregamento e salvamento de cache
    - Validação de integridade do cache
    - Classificação de mangás (cache hit/miss)
    - Controle de versão do cache
    """
    
    def __init__(self, cache_version: str = '1.0'):
        self.cache_version = cache_version
        self.cache_file_name = '.ohara_cache.json'
        
    def load_cache(self, cache_file: Path) -> Dict:
        """Carregar cache com tratamento seguro de erros"""
        if not cache_file.exists():
            return {}
        
        try:
            cache_text = cache_file.read_text(encoding='utf-8')
            cache_data = json.loads(cache_text)
            
            if not isinstance(cache_data, dict):
                logger.info("Cache com formato inválido, ignorando")
                return {}
            
            if cache_data.get('_cache_version') != self.cache_version:
                logger.info(f"Cache de versão antiga ({cache_data.get('_cache_version')} != {self.cache_version}), ignorando")
                return {}

            logger.info(f"Cache carregado: {len(cache_data) - 1} entradas")
            return cache_data
            
        except Exception as e:
            logger.warning(f"Erro ao carregar cache: {e}")
            self._backup_corrupted_cache(cache_file)
            return {}
    
    def save_cache(self, cache_file: Path, mangas: List[Manga]) -> None:
        """Salvar cache otimizado"""
        try:
            cache_data = {'_cache_version': self.cache_version}
            current_time = time.time()
            
            for manga in mangas:
                try:
                    manga_path = Path(manga.path)
                    dir_mtime = manga_path.stat().st_mtime
                    lightweight_manga_data = self._create_lightweight_manga(manga)
                    
                    cache_data[manga.id] = {
                        'manga_data': lightweight_manga_data,
                        'cache_timestamp': current_time,
                        'dir_mtime': dir_mtime,
                        'cache_version': self.cache_version
                    }
                except Exception as e:
                    logger.info(f"Erro ao cachear {manga.title}: {e}")
            
            self._save_atomically(cache_file, cache_data)
            
        except Exception as e:
            logger.warning(f"Erro ao salvar cache: {e}")
    
    def can_use_cache(self, manga_dir: Path, cache_entry: Optional[Dict]) -> bool:
        """Verificar se pode usar cache baseado em timestamp"""
        if not cache_entry:
            return False
        
        if cache_entry.get('cache_version') != self.cache_version:
            return False
        
        try:
            dir_mtime = manga_dir.stat().st_mtime
            cache_timestamp = cache_entry.get('dir_mtime', 0)
            return abs(dir_mtime - cache_timestamp) < 1.0
            
        except OSError as e:
            logger.warning(f"Erro ao verificar timestamp de {manga_dir.name}: {e}")
            return False
    
    def restore_manga_from_cache(self, manga_data: Dict) -> Optional[Manga]:
        """Restaurar mangá do cache"""
        try:
            manga = Manga(**manga_data)
            return manga
        except Exception as e:
            logger.warning(f"Erro ao restaurar mangá do cache: {e}")
            return None
    
    def clear_cache(self, library_path: str) -> bool:
        """Limpar cache de uma biblioteca específica"""
        try:
            cache_file = Path(library_path) / self.cache_file_name
            if cache_file.exists():
                cache_file.unlink()
                logger.info(f"Cache limpo: {cache_file}")
                return True
            return False
        except Exception as e:
            logger.warning(f"Erro ao limpar cache: {e}")
            return False
    
    def get_cache_info(self, library_path: str) -> Dict:
        """Obter informações sobre o cache"""
        cache_file = Path(library_path) / self.cache_file_name
        
        if not cache_file.exists():
            return {"exists": False}
        
        try:
            stat = cache_file.stat()
            cache_data = self.load_cache(cache_file)
            
            return {
                "exists": True,
                "size_bytes": stat.st_size,
                "size_mb": round(stat.st_size / 1024 / 1024, 2),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "entries": len(cache_data) - 1,
                "version": cache_data.get('_cache_version', 'unknown')
            }
        except Exception as e:
            return {"exists": True, "error": str(e)}
    
    def _backup_corrupted_cache(self, cache_file: Path) -> None:
        """Fazer backup de cache corrompido"""
        try:
            backup_name = f"{cache_file.name}.corrupted.{int(time.time())}"
            cache_file.rename(cache_file.parent / backup_name)
            logger.info(f"Cache corrompido salvo como: {backup_name}")
        except OSError as ex:
            logger.error(f"Falha ao renomear arquivo corrompido: {ex}")
    
    def _save_atomically(self, cache_file: Path, cache_data: Dict) -> None:
        """Salvar cache atomicamente"""
        temp_file = cache_file.with_suffix('.tmp')
        cache_json = json.dumps(cache_data, separators=(',', ':'), default=str, ensure_ascii=False)
        temp_file.write_text(cache_json, encoding='utf-8')
        temp_file.replace(cache_file)
        
        cache_size_mb = len(cache_json) / 1024 / 1024
        logger.info(f"Cache salvo: {len(cache_data) - 1} mangás ({cache_size_mb:.2f}MB)")
    
    @staticmethod
    def _create_lightweight_manga(manga: Manga) -> Dict:
        """Criar versão leve do mangá para cache"""
        lightweight_chapters = []
        
        for chapter in manga.chapters:
            lightweight_chapter = {
                "id": chapter.id,
                "name": chapter.name,
                "number": chapter.number,
                "volume": chapter.volume,
                "path": chapter.path,
                "page_count": chapter.page_count,
                "date_added": chapter.date_added.isoformat() if chapter.date_added else None,
                "pages": []
            }
            lightweight_chapters.append(lightweight_chapter)
        
        return {
            "id": manga.id,
            "title": manga.title,
            "path": manga.path,
            "thumbnail": manga.thumbnail,
            "chapters": lightweight_chapters,
            "chapter_count": manga.chapter_count,
            "total_pages": manga.total_pages,
            "author": getattr(manga, 'author', None),
            "artist": getattr(manga, 'artist', None),
            "status": getattr(manga, 'status', None),
            "genres": getattr(manga, 'genres', []),
            "description": getattr(manga, 'description', None),
            "date_added": manga.date_added.isoformat() if manga.date_added else None,
            "date_modified": manga.date_modified.isoformat() if manga.date_modified else None
        }