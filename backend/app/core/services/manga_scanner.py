import os
import re
from pathlib import Path
from typing import List, Optional, Dict, Tuple
import mimetypes
from datetime import datetime

from app.models.manga import Manga, Chapter, Page, Library
from app.core.config import get_settings, SUPPORTED_IMAGE_EXTENSIONS, CHAPTER_PATTERNS

class MangaScanner:
    """Serviço para escanear e organizar mangás"""
    
    def __init__(self):
        self.settings = get_settings()
        self.supported_extensions = SUPPORTED_IMAGE_EXTENSIONS
        
    def scan_library(self, library_path: str) -> Library:
        """
        Escaneia uma pasta de biblioteca e retorna objeto Library
        
        Args:
            library_path: Caminho para a pasta da biblioteca
            
        Returns:
            Library: Objeto biblioteca com todos os mangás encontrados
        """
        library = Library()
        library_path = Path(library_path)
        
        if not library_path.exists() or not library_path.is_dir():
            raise ValueError(f"Caminho inválido: {library_path}")
        
        # Escanear cada pasta como um mangá potencial
        for manga_dir in library_path.iterdir():
            if manga_dir.is_dir() and not manga_dir.name.startswith('.'):
                try:
                    manga = self.scan_manga(str(manga_dir))
                    if manga and manga.chapters:  # Só adiciona se tem capítulos
                        library.add_manga(manga)
                except Exception as e:
                    print(f"Erro ao escanear mangá {manga_dir.name}: {e}")
                    continue
        
        return library
    
    def scan_manga(self, manga_path: str) -> Optional[Manga]:
        """
        Escaneia uma pasta de mangá específico
        
        Args:
            manga_path: Caminho para a pasta do mangá
            
        Returns:
            Manga: Objeto mangá com capítulos organizados
        """
        manga_path = Path(manga_path)
        
        if not manga_path.exists() or not manga_path.is_dir():
            return None
        
        # Criar objeto mangá
        manga_id = self._generate_manga_id(manga_path.name)
        manga = Manga(
            id=manga_id,
            title=manga_path.name,
            path=str(manga_path),
            date_added=datetime.fromtimestamp(manga_path.stat().st_ctime)
        )
        
        # Buscar thumbnail
        manga.thumbnail = self._find_thumbnail(manga_path)
        
        # Escanear capítulos
        chapters = []
        for chapter_dir in manga_path.iterdir():
            if chapter_dir.is_dir() and not chapter_dir.name.startswith('.'):
                chapter = self._scan_chapter(chapter_dir, manga_id)
                if chapter:
                    chapters.append(chapter)
        
        # Ordenar capítulos
        manga.chapters = self._sort_chapters(chapters)
        manga.chapter_count = len(manga.chapters)
        manga.total_pages = sum(ch.page_count for ch in manga.chapters)
        
        return manga
    
    def _scan_chapter(self, chapter_path: Path, manga_id: str) -> Optional[Chapter]:
        """
        Escaneia uma pasta de capítulo
        
        Args:
            chapter_path: Caminho para a pasta do capítulo
            manga_id: ID do mangá pai
            
        Returns:
            Chapter: Objeto capítulo com páginas
        """
        # Extrair informações do capítulo
        chapter_info = self._parse_chapter_name(chapter_path.name)
        
        # Buscar páginas (imagens)
        pages = []
        image_files = []
        
        for file_path in chapter_path.iterdir():
            if file_path.is_file() and self._is_image_file(file_path):
                image_files.append(file_path)
        
        # Ordenar arquivos de imagem por nome
        image_files.sort(key=lambda x: self._natural_sort_key(x.name))
        
        # Criar objetos Page
        for i, img_path in enumerate(image_files):
            page = Page(
                filename=img_path.name,
                path=str(img_path),
                size=img_path.stat().st_size
            )
            pages.append(page)
        
        if not pages:  # Capítulo sem páginas válidas
            return None
        
        # Criar objeto Chapter
        chapter_id = f"{manga_id}-ch-{chapter_info['number'] or len(pages)}"
        chapter = Chapter(
            id=chapter_id,
            name=chapter_path.name,
            number=chapter_info['number'],
            volume=chapter_info['volume'],
            path=str(chapter_path),
            pages=pages,
            page_count=len(pages),
            date_added=datetime.fromtimestamp(chapter_path.stat().st_ctime)
        )
        
        return chapter
    
    def _parse_chapter_name(self, chapter_name: str) -> Dict:
        """
        Extrai informações do nome do capítulo usando regex
        
        Args:
            chapter_name: Nome da pasta do capítulo
            
        Returns:
            Dict: Informações extraídas (number, volume)
        """
        info = {'number': None, 'volume': None}
        
        for pattern in CHAPTER_PATTERNS:
            match = re.search(pattern, chapter_name, re.IGNORECASE)
            if match:
                groups = match.groups()
                
                if len(groups) == 1:
                    # Padrão simples: apenas número do capítulo
                    try:
                        info['number'] = float(groups[0])
                    except ValueError:
                        pass
                elif len(groups) == 2:
                    # Padrão Volume + Capítulo
                    try:
                        info['volume'] = int(groups[0])
                        info['number'] = float(groups[1])
                    except ValueError:
                        pass
                break
        
        return info
    
    def _sort_chapters(self, chapters: List[Chapter]) -> List[Chapter]:
        """
        Ordena capítulos por número (mais recentes primeiro)
        
        Args:
            chapters: Lista de capítulos
            
        Returns:
            List[Chapter]: Capítulos ordenados
        """
        def sort_key(chapter):
            # Priorizar por número de capítulo, depois por nome
            if chapter.number is not None:
                return (0, -chapter.number)  # Negativo para ordem decrescente
            else:
                return (1, chapter.name)  # Fallback alfabético
        
        return sorted(chapters, key=sort_key)
    
    def _find_thumbnail(self, manga_path: Path) -> Optional[str]:
        """
        Busca uma imagem de thumbnail na pasta do mangá
        
        Args:
            manga_path: Caminho da pasta do mangá
            
        Returns:
            str: Caminho da thumbnail ou None
        """
        # Buscar arquivos de imagem na raiz
        for file_path in manga_path.iterdir():
            if file_path.is_file() and self._is_image_file(file_path):
                return str(file_path)
        
        # Se não encontrou na raiz, buscar na primeira página do primeiro capítulo
        chapters = []
        for chapter_dir in manga_path.iterdir():
            if chapter_dir.is_dir():
                chapters.append(chapter_dir)
        
        if chapters:
            # Ordenar capítulos e pegar o primeiro
            chapters.sort(key=lambda x: self._natural_sort_key(x.name))
            first_chapter = chapters[0]
            
            images = []
            for file_path in first_chapter.iterdir():
                if file_path.is_file() and self._is_image_file(file_path):
                    images.append(file_path)
            
            if images:
                images.sort(key=lambda x: self._natural_sort_key(x.name))
                return str(images[0])
        
        return None
    
    def _is_image_file(self, file_path: Path) -> bool:
        """Verifica se um arquivo é uma imagem suportada"""
        return file_path.suffix.lower() in self.supported_extensions
    
    def _generate_manga_id(self, manga_title: str) -> str:
        """Gera um ID único para o mangá baseado no título"""
        # Remove caracteres especiais e converte para lowercase
        clean_title = re.sub(r'[^\w\s-]', '', manga_title.lower())
        clean_title = re.sub(r'[-\s]+', '-', clean_title)
        return clean_title.strip('-')
    
    def _natural_sort_key(self, text: str) -> List:
        """
        Chave para ordenação natural (1, 2, 10 em vez de 1, 10, 2)
        """
        def convert(text):
            return int(text) if text.isdigit() else text.lower()
        
        return [convert(c) for c in re.split('([0-9]+)', text)]
    
    def refresh_manga(self, manga_path: str) -> Optional[Manga]:
        """
        Reescaneia um mangá específico (útil para atualizações)
        
        Args:
            manga_path: Caminho do mangá para reescanear
            
        Returns:
            Manga: Mangá atualizado
        """
        return self.scan_manga(manga_path)
    
    def validate_library_path(self, path: str) -> Tuple[bool, str]:
        """
        Valida se um caminho é válido para biblioteca
        
        Args:
            path: Caminho a ser validado
            
        Returns:
            Tuple[bool, str]: (é_válido, mensagem)
        """
        path_obj = Path(path)
        
        if not path_obj.exists():
            return False, "Caminho não existe"
        
        if not path_obj.is_dir():
            return False, "Caminho não é um diretório"
        
        # Verificar se tem pelo menos uma pasta que pode ser um mangá
        manga_dirs = [d for d in path_obj.iterdir() if d.is_dir() and not d.name.startswith('.')]
        
        if not manga_dirs:
            return False, "Nenhuma pasta de mangá encontrada"
        
        return True, "Caminho válido"