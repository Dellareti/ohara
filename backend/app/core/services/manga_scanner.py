import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from app.core.config import get_settings, SUPPORTED_IMAGE_EXTENSIONS
from app.core.services.simple_cache import SimpleCache
from app.core.services.chapter_parser import ChapterParser
from app.models.manga import Manga, Chapter, Page, Library

logger = logging.getLogger(__name__)


class MangaScanner:
    """
    Scanner simplificado e eficiente de mangás.
    
    Funcionalidades essenciais:
    - Escaneamento de bibliotecas de mangás
    - Cache simples baseado em timestamp
    - Descoberta de estruturas de mangá
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.supported_extensions = SUPPORTED_IMAGE_EXTENSIONS
        self.cache_enabled = True
        
        # Componentes essenciais
        self.cache = SimpleCache()
        self.chapter_parser = ChapterParser()
        
        logger.info("MangaScanner inicializado (modo simplificado)")

    def scan_library(self, library_path: str) -> Library:
        """Escaneia uma biblioteca de mangás com cache simples"""
        library_path_obj = Path(library_path)
        
        if not library_path_obj.exists():
            raise ValueError(f"Biblioteca não encontrada: {library_path}")
        
        # Carregar cache se habilitado
        cache_data = {}
        if self.cache_enabled:
            cache_file = library_path_obj / self.cache.cache_file_name
            cache_data = self.cache.load_cache(cache_file)
        
        # Descobrir diretórios de mangá
        manga_dirs = self._discover_manga_directories(library_path_obj)
        logger.info(f"Encontrados {len(manga_dirs)} diretórios de mangá")
        
        # Processar mangás
        mangas = []
        cache_hits = 0
        
        for manga_dir in manga_dirs:
            manga_id = self._generate_manga_id(manga_dir.name)
            cache_entry = cache_data.get(manga_id)
            
            # Tentar usar cache
            if self.cache_enabled and self.cache.is_valid(manga_dir, cache_entry):
                manga = self.cache.restore_manga(cache_entry['manga_data'])
                if manga:
                    # Recriar páginas se necessário
                    self._ensure_pages_loaded(manga)
                    mangas.append(manga)
                    cache_hits += 1
                    continue
            
            # Escanear mangá
            manga = self.scan_manga(str(manga_dir))
            if manga:
                mangas.append(manga)
        
        # Salvar cache atualizado
        if self.cache_enabled and mangas:
            self.cache.save_cache(library_path_obj / self.cache.cache_file_name, mangas)
        
        logger.info(f"Biblioteca escaneada: {len(mangas)} mangás ({cache_hits} do cache)")
        
        library = Library(mangas=mangas)
        library._update_stats()
        return library
    
    def scan_manga(self, manga_path: str) -> Optional[Manga]:
        """Escaneia um mangá específico"""
        manga_path_obj = Path(manga_path)
        
        if not manga_path_obj.exists():
            return None
        
        try:
            # Descobrir capítulos
            chapter_dirs = self._discover_chapter_directories(manga_path_obj)
            
            if not chapter_dirs:
                logger.warning(f"Nenhum capítulo encontrado em: {manga_path_obj.name}")
                return None
            
            # Processar capítulos
            chapters = []
            total_pages = 0
            
            for chapter_dir in chapter_dirs:
                chapter = self._scan_chapter(chapter_dir)
                if chapter:
                    chapters.append(chapter)
                    total_pages += chapter.page_count
            
            if not chapters:
                return None
            
            # Ordenar capítulos
            chapters = self.chapter_parser.sort_chapters(chapters)
            
            # Encontrar thumbnail
            thumbnail = self._find_thumbnail(manga_path_obj)
            
            # Criar mangá
            manga = Manga(
                id=self._generate_manga_id(manga_path_obj.name),
                title=manga_path_obj.name,
                path=str(manga_path_obj),
                thumbnail=thumbnail,
                chapters=chapters,
                chapter_count=len(chapters),
                total_pages=total_pages,
                date_added=datetime.now(),
                date_modified=datetime.fromtimestamp(manga_path_obj.stat().st_mtime)
            )
            
            return manga
            
        except Exception as e:
            logger.error(f"Erro ao escanear mangá {manga_path_obj.name}: {e}")
            return None
    
    def enable_cache(self):
        """Habilitar cache"""
        self.cache_enabled = True
        logger.info("Cache habilitado")
    
    def disable_cache(self):
        """Desabilitar cache"""
        self.cache_enabled = False
        logger.info("Cache desabilitado")
    
    def clear_cache(self, library_path: str) -> bool:
        """Limpar cache da biblioteca"""
        return self.cache.clear_cache(library_path)
    
    def get_cache_info(self, library_path: str) -> dict:
        """Obter informações do cache"""
        return self.cache.get_cache_info(library_path)
    
    def _discover_manga_directories(self, library_path: Path) -> List[Path]:
        """Descobrir diretórios de mangá"""
        manga_dirs = []
        
        try:
            for item in library_path.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    manga_dirs.append(item)
        except OSError as e:
            logger.error(f"Erro ao ler biblioteca: {e}")
        
        return sorted(manga_dirs)
    
    def _discover_chapter_directories(self, manga_path: Path) -> List[Path]:
        """Descobrir diretórios de capítulos"""
        chapter_dirs = []
        
        try:
            for item in manga_path.iterdir():
                if item.is_dir():
                    # Verificar se tem imagens
                    if self._has_images(item):
                        chapter_dirs.append(item)
        except OSError as e:
            logger.error(f"Erro ao ler mangá: {e}")
        
        return chapter_dirs
    
    def _scan_chapter(self, chapter_path: Path) -> Optional[Chapter]:
        """Escanear um capítulo"""
        try:
            # Encontrar imagens
            image_files = self._find_image_files(chapter_path)
            
            if not image_files:
                return None
            
            # Criar páginas
            pages = []
            for i, image_file in enumerate(image_files, 1):
                page = Page(
                    id=f"{chapter_path.name}_page_{i}",
                    number=i,
                    filename=image_file.name,
                    path=str(image_file)
                )
                pages.append(page)
            
            # Analisar capítulo
            chapter_info = self.chapter_parser.parse_chapter_name(chapter_path.name)
            
            # Gerar ID limpo para capítulo
            manga_id = self._generate_manga_id(chapter_path.parent.name)
            chapter_number = chapter_info.get('number', 0)
            chapter_id = f"{manga_id}-ch-{int(chapter_number) if chapter_number else 1}"
            
            chapter = Chapter(
                id=chapter_id,
                name=chapter_path.name,
                number=chapter_info.get('number', 0),
                volume=chapter_info.get('volume'),
                path=str(chapter_path),
                pages=pages,
                page_count=len(pages),
                date_added=datetime.now()
            )
            
            return chapter
            
        except Exception as e:
            logger.error(f"Erro ao escanear capítulo {chapter_path.name}: {e}")
            return None
    
    def _find_thumbnail(self, manga_path: Path) -> Optional[str]:
        """Encontrar thumbnail do mangá"""
        # Procurar na pasta raiz
        for ext in self.supported_extensions:
            for pattern in ['cover', 'capa', 'thumb', 'thumbnail']:
                thumb_file = manga_path / f"{pattern}.{ext}"
                if thumb_file.exists():
                    return str(thumb_file)
        
        # Usar primeira imagem da pasta raiz
        for file in manga_path.iterdir():
            if file.is_file() and file.suffix.lower() in self.supported_extensions:
                return str(file)
        
        # Usar primeira página do primeiro capítulo
        chapter_dirs = self._discover_chapter_directories(manga_path)
        if chapter_dirs:
            first_chapter = sorted(chapter_dirs)[0]
            image_files = self._find_image_files(first_chapter)
            if image_files:
                return str(image_files[0])
        
        return None
    
    def _find_image_files(self, directory: Path) -> List[Path]:
        """Encontrar arquivos de imagem em um diretório"""
        image_files = []
        
        try:
            for file in directory.iterdir():
                if file.is_file() and file.suffix.lower() in self.supported_extensions:
                    image_files.append(file)
        except OSError:
            pass
        
        return sorted(image_files)
    
    def _has_images(self, directory: Path) -> bool:
        """Verificar se diretório tem imagens"""
        try:
            for file in directory.iterdir():
                if file.is_file() and file.suffix.lower() in self.supported_extensions:
                    return True
        except OSError:
            pass
        
        return False
    
    def _ensure_pages_loaded(self, manga: Manga) -> None:
        """Garantir que páginas estão carregadas para mangá do cache"""
        for chapter in manga.chapters:
            if not chapter.pages:
                chapter_path = Path(chapter.path)
                if chapter_path.exists():
                    image_files = self._find_image_files(chapter_path)
                    pages = []
                    
                    for i, image_file in enumerate(image_files, 1):
                        page = Page(
                            id=f"{chapter.id}_page_{i}",
                            number=i,
                            filename=image_file.name,
                            path=str(image_file)
                        )
                        pages.append(page)
                    
                    chapter.pages = pages
                    chapter.page_count = len(pages)
    
    def _generate_manga_id(self, manga_name: str) -> str:
        """Gerar ID legível para mangá (compatível com sistema anterior)"""
        import re
        clean_title = manga_name.lower()
        clean_title = re.sub(r'\W+', '-', clean_title)
        clean_title = re.sub(r'-+', '-', clean_title).strip('-')
        return clean_title
    
    @staticmethod
    def validate_library_path(path: str) -> tuple[bool, str]:
        """Validar caminho de biblioteca"""
        from pathlib import Path
        
        path_obj = Path(path)
        
        if not path_obj.exists():
            return False, "Caminho não existe"
        
        if not path_obj.is_dir():
            return False, "Caminho não é um diretório"
        
        manga_dirs = [d for d in path_obj.iterdir() if d.is_dir() and not d.name.startswith('.')]
        
        if not manga_dirs:
            return False, "Nenhuma pasta de mangá encontrada"
        
        return True, "Caminho válido"