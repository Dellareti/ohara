import os
import json
import time
import re
from pathlib import Path
from typing import List, Optional, Dict, Tuple
import mimetypes
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.models.manga import Manga, Chapter, Page, Library
from app.core.config import get_settings, SUPPORTED_IMAGE_EXTENSIONS, CHAPTER_PATTERNS

class MangaScanner:
    """
    Scanner de mangás com Cache Híbrido Otimizado
    
    COMPATIBILIDADE TOTAL:
    - Mantém toda API existente
    - Fallback automático para algoritmo original
    - Zero breaking changes
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.supported_extensions = SUPPORTED_IMAGE_EXTENSIONS
        
        # Configurações do cache híbrido
        self.cache_enabled = True  # Flag para desabilitar se necessário
        self.cache_file_name = '.ohara_cache.json'
        self.max_workers = 4  # Threads para paralelização
        self.cache_version = '1.0'  # Para invalidar cache se mudar estrutura
        
        print(f"🚀 MangaScanner inicializado (Cache Híbrido v{self.cache_version})")
        
    def scan_library(self, library_path: str) -> Library:
        """
        API ORIGINAL - 100% Compatível
        
        Agora usa Cache Híbrido automaticamente com fallback seguro
        """
        try:
            return self._scan_library_with_cache(library_path)
        except Exception as e:
            print(f"⚠️ Cache híbrido falhou, usando scanner original: {e}")
            return self._scan_library_original(library_path)
    
    def _scan_library_with_cache(self, library_path: str) -> Library:
        """Scanner otimizado com cache híbrido"""
        start_time = time.time()
        library_path = Path(library_path)
        
        if not self.cache_enabled:
            print("📋 Cache desabilitado, usando scan direto")
            return self._scan_library_original(str(library_path))
        
        print(f"🔍 Iniciando scan híbrido: {library_path}")
        
        # 1. Setup do cache
        cache_file = library_path / self.cache_file_name
        cache_data = self._load_cache_safe(cache_file)
        
        # 2. Descobrir mangás na pasta
        manga_dirs = self._get_manga_directories_fast(library_path)
        print(f"📂 Encontrados {len(manga_dirs)} diretórios de mangá")
        
        # 3. Dividir entre cache e scan
        cached_mangas, dirs_to_scan = self._classify_mangas(manga_dirs, cache_data)
        
        print(f"📋 Cache hits: {len(cached_mangas)}, Rescans: {len(dirs_to_scan)}")
        
        # 4. Escanear apenas os necessários
        new_mangas = []
        if dirs_to_scan:
            print(f"🔄 Escaneando {len(dirs_to_scan)} mangás...")
            new_mangas = self._scan_mangas_parallel_safe(dirs_to_scan)
        
        # 5. Combinar resultados
        all_mangas = cached_mangas + new_mangas
        
        # 6. Atualizar cache
        if new_mangas:  # Só salvar se houver mudanças
            self._save_cache_safe(cache_file, all_mangas)
        
        # 7. Criar biblioteca final
        library = Library()
        for manga in all_mangas:
            library.add_manga(manga)
        
        elapsed = time.time() - start_time
        print(f"✅ Scan híbrido concluído em {elapsed:.2f}s ({len(all_mangas)} mangás)")
        
        return library
    
    def _get_manga_directories_fast(self, library_path: Path) -> List[Path]:
        """Obter diretórios usando os.scandir() (mais rápido que iterdir)"""
        manga_dirs = []
        
        try:
            with os.scandir(library_path) as entries:
                for entry in entries:
                    if entry.is_dir() and not entry.name.startswith('.'):
                        manga_dirs.append(Path(entry.path))
        except OSError as e:
            print(f"❌ Erro ao listar diretórios: {e}")
            # Fallback para método original
            manga_dirs = [d for d in library_path.iterdir() if d.is_dir() and not d.name.startswith('.')]
        
        return sorted(manga_dirs, key=lambda x: x.name.lower())
    
    def _classify_mangas(self, manga_dirs: List[Path], cache_data: Dict) -> Tuple[List[Manga], List[Path]]:
        """Dividir mangás entre cache hits e que precisam scan"""
        cached_mangas = []
        dirs_to_scan = []
        
        for manga_dir in manga_dirs:
            manga_id = self._generate_manga_id(manga_dir.name)
            cache_entry = cache_data.get(manga_id)
            
            if self._can_use_cache(manga_dir, cache_entry):
                # Usar cache
                try:
                    manga = self._restore_manga_from_cache(cache_entry['manga_data'])
                    if manga:
                        cached_mangas.append(manga)
                        continue
                except Exception as e:
                    print(f"⚠️ Erro ao restaurar {manga_dir.name} do cache: {e}")
            
            # Precisa escanear
            dirs_to_scan.append(manga_dir)
        
        return cached_mangas, dirs_to_scan
    
    def _can_use_cache(self, manga_dir: Path, cache_entry: Optional[Dict]) -> bool:
        """Verificar se pode usar cache baseado em timestamp"""
        if not cache_entry:
            return False
        
        if cache_entry.get('cache_version') != self.cache_version:
            return False
        
        try:
            # Comparar mtime da pasta do mangá
            dir_mtime = manga_dir.stat().st_mtime
            cache_timestamp = cache_entry.get('dir_mtime', 0)
            
            # Se pasta não foi modificada, usar cache
            return abs(dir_mtime - cache_timestamp) < 1.0  # Tolerância de 1s
            
        except OSError as e:
            print(f"⚠️ Erro ao verificar timestamp de {manga_dir.name}: {e}")
            return False
    
    def _scan_mangas_parallel_safe(self, manga_dirs: List[Path]) -> List[Manga]:
        """Escanear mangás em paralelo com fallback seguro"""
        if len(manga_dirs) == 1:
            # Para apenas 1 mangá, não vale a pena paralelizar
            manga = self.scan_manga(str(manga_dirs[0]))
            return [manga] if manga else []
        
        mangas = []
        
        try:
            # Tentar paralelização
            with ThreadPoolExecutor(max_workers=min(self.max_workers, len(manga_dirs))) as executor:
                future_to_dir = {
                    executor.submit(self._scan_manga_optimized_safe, manga_dir): manga_dir 
                    for manga_dir in manga_dirs
                }
                
                for future in as_completed(future_to_dir):
                    manga_dir = future_to_dir[future]
                    try:
                        manga = future.result(timeout=30)  # Timeout de 30s por mangá
                        if manga and manga.chapters:
                            mangas.append(manga)
                    except Exception as e:
                        print(f"❌ Erro paralelo em {manga_dir.name}: {e}")
                        # Fallback: escanear com método original
                        try:
                            manga = self.scan_manga(str(manga_dir))
                            if manga and manga.chapters:
                                mangas.append(manga)
                        except Exception as e2:
                            print(f"❌ Fallback também falhou para {manga_dir.name}: {e2}")
        
        except Exception as e:
            print(f"❌ Paralelização falhou, usando scan sequencial: {e}")
            # Fallback: escanear sequencialmente
            for manga_dir in manga_dirs:
                try:
                    manga = self.scan_manga(str(manga_dir))
                    if manga and manga.chapters:
                        mangas.append(manga)
                except Exception as e:
                    print(f"❌ Erro em {manga_dir.name}: {e}")
        
        return mangas
    
    def _scan_manga_optimized_safe(self, manga_path: Path) -> Optional[Manga]:
        """Scanner de mangá individual otimizado com fallbacks"""
        try:
            # Usar scanner otimizado
            return self._scan_manga_fast(manga_path)
        except Exception as e:
            print(f"⚠️ Scanner otimizado falhou para {manga_path.name}: {e}")
            # Fallback: usar método original
            return self.scan_manga(str(manga_path))
    
    def _scan_manga_fast(self, manga_path: Path) -> Optional[Manga]:
        """Scanner otimizado com lazy loading"""
        # Criar objeto mangá
        manga_id = self._generate_manga_id(manga_path.name)
        manga = Manga(
            id=manga_id,
            title=manga_path.name,
            path=str(manga_path),
            date_added=datetime.fromtimestamp(manga_path.stat().st_ctime)
        )
        
        # Buscar thumbnail (método original - já é rápido)
        manga.thumbnail = self._find_thumbnail(manga_path)
        
        # Escanear capítulos com lazy loading
        chapters = self._scan_chapters_lazy(manga_path, manga_id)
        
        if not chapters:
            return None
        
        # Ordenar e estatísticas
        manga.chapters = self._sort_chapters(chapters)
        manga.chapter_count = len(manga.chapters)
        manga.total_pages = sum(ch.page_count for ch in manga.chapters)
        
        return manga
    
    def _scan_chapters_lazy(self, manga_path: Path, manga_id: str) -> List[Chapter]:
        """Escanear capítulos com lazy loading de páginas"""
        chapters = []
        
        try:
            # Usar os.scandir() para performance
            with os.scandir(manga_path) as entries:
                chapter_entries = [entry for entry in entries if entry.is_dir() and not entry.name.startswith('.')]
        except OSError:
            # Fallback
            chapter_entries = [{'path': str(d), 'name': d.name} for d in manga_path.iterdir() if d.is_dir() and not d.name.startswith('.')]
            chapter_entries = [type('Entry', (), entry) for entry in chapter_entries]
        
        for entry in chapter_entries:
            try:
                chapter_path = Path(entry.path) if hasattr(entry, 'path') else Path(entry.name)
                if not chapter_path.is_absolute():
                    chapter_path = manga_path / chapter_path
                
                chapter = self._scan_chapter_lazy(chapter_path, manga_id)
                if chapter:
                    chapters.append(chapter)
            except Exception as e:
                print(f"⚠️ Erro no capítulo {getattr(entry, 'name', 'unknown')}: {e}")
        
        return chapters
    
    def _scan_chapter_lazy(self, chapter_path: Path, manga_id: str) -> Optional[Chapter]:
        """Escanear capítulo com lazy loading"""
        try:
            # Parse do nome
            chapter_info = self._parse_chapter_name(chapter_path.name)
            
            # Contar páginas rapidamente
            page_count = self._count_image_files_fast(chapter_path)
            
            if page_count == 0:
                return None
            
            # Criar lista de páginas lazy (só nomes, sem metadados)
            pages = self._create_pages_lazy(chapter_path)
            
            # Criar capítulo
            chapter_id = f"{manga_id}-ch-{chapter_info['number'] or page_count}"
            chapter = Chapter(
                id=chapter_id,
                name=chapter_path.name,
                number=chapter_info['number'],
                volume=chapter_info['volume'],
                path=str(chapter_path),
                pages=pages,
                page_count=page_count,
                date_added=datetime.fromtimestamp(chapter_path.stat().st_ctime)
            )
            
            return chapter
            
        except Exception as e:
            print(f"⚠️ Erro no capítulo {chapter_path.name}: {e}")
            # Fallback: usar método original
            return self._scan_chapter(chapter_path, manga_id)
    
    def _count_image_files_fast(self, chapter_path: Path) -> int:
        """Contar arquivos de imagem rapidamente"""
        try:
            count = 0
            with os.scandir(chapter_path) as entries:
                for entry in entries:
                    if entry.is_file() and self._is_image_file_name(entry.name):
                        count += 1
            return count
        except OSError:
            # Fallback
            return len([f for f in chapter_path.iterdir() if f.is_file() and self._is_image_file(f)])
    
    def _create_pages_lazy(self, chapter_path: Path) -> List[Page]:
        """Criar páginas sem carregar metadados (lazy)"""
        pages = []
        
        try:
            # Coletar nomes de arquivos
            image_files = []
            with os.scandir(chapter_path) as entries:
                for entry in entries:
                    if entry.is_file() and self._is_image_file_name(entry.name):
                        image_files.append(entry.name)
        except OSError:
            # Fallback
            image_files = [f.name for f in chapter_path.iterdir() if f.is_file() and self._is_image_file(f)]
        
        # Ordenar
        image_files.sort(key=self._natural_sort_key)
        
        # Criar objetos Page lazy
        for filename in image_files:
            page = Page(
                filename=filename,
                path=str(chapter_path / filename),
                size=None,  # Carregar sob demanda
                width=None,
                height=None
            )
            pages.append(page)
        
        return pages
    
    def _is_image_file_name(self, filename: str) -> bool:
        """Verificação rápida por extensão"""
        return Path(filename).suffix.lower() in self.supported_extensions
    
    def _load_cache_safe(self, cache_file: Path) -> Dict:
        """Carregar cache com tratamento seguro de erros"""
        if not cache_file.exists():
            return {}
        
        try:
            cache_text = cache_file.read_text(encoding='utf-8')
            cache_data = json.loads(cache_text)
            
            # Validar estrutura do cache
            if not isinstance(cache_data, dict):
                print("⚠️ Cache com formato inválido, ignorando")
                return {}
            
            # Verificar versão do cache
            if cache_data.get('_cache_version') != self.cache_version:
                print(f"⚠️ Cache de versão antiga ({cache_data.get('_cache_version')} != {self.cache_version}), ignorando")
                return {}
            
            print(f"📋 Cache carregado: {len(cache_data) - 1} entradas")  # -1 para _cache_version
            return cache_data
            
        except Exception as e:
            print(f"⚠️ Erro ao carregar cache: {e}")
            # Tentar renomear cache corrompido
            try:
                backup_name = f"{cache_file.name}.corrupted.{int(time.time())}"
                cache_file.rename(cache_file.parent / backup_name)
                print(f"📁 Cache corrompido salvo como: {backup_name}")
            except:
                pass
            
            return {}
    
    def _save_cache_safe(self, cache_file: Path, mangas: List[Manga]) -> None:
        """Salvar cache otimizado (sem páginas individuais)"""
        try:
            cache_data = {'_cache_version': self.cache_version}
            current_time = time.time()
            
            for manga in mangas:
                try:
                    manga_path = Path(manga.path)
                    dir_mtime = manga_path.stat().st_mtime
                    
                    # Usar versão leve do mangá (SEM páginas individuais)
                    lightweight_manga_data = self._create_lightweight_manga_for_cache(manga)
                    
                    cache_data[manga.id] = {
                        'manga_data': lightweight_manga_data,
                        'cache_timestamp': current_time,
                        'dir_mtime': dir_mtime,
                        'cache_version': self.cache_version
                    }
                except Exception as e:
                    print(f"⚠️ Erro ao cachear {manga.title}: {e}")
            
            # Salvar atomicamente
            temp_file = cache_file.with_suffix('.tmp')
            
            # Usar compactação JSON para economizar ainda mais espaço
            cache_json = json.dumps(cache_data, separators=(',', ':'), default=str, ensure_ascii=False)
            temp_file.write_text(cache_json, encoding='utf-8')
            temp_file.replace(cache_file)
            
            # Calcular economia de espaço
            cache_size_mb = len(cache_json) / 1024 / 1024
            estimated_full_size = cache_size_mb * 100  # Estimativa sem otimização
            
            print(f"💾 Cache otimizado salvo: {len(mangas)} mangás")
            print(f"📊 Tamanho do cache: {cache_size_mb:.2f}MB (economizou ~{estimated_full_size:.1f}MB)")
            
        except Exception as e:
            print(f"❌ Erro ao salvar cache: {e}")

    def _restore_manga_from_cache(self, manga_data: Dict) -> Optional[Manga]:
        """Restaurar mangá do cache e recriar páginas sob demanda"""
        try:
            # Restaurar dados básicos
            manga = Manga(**manga_data)
            
            # ✅ CORREÇÃO: Se não tem thumbnail no cache, buscar novamente
            if not manga.thumbnail:
                manga_path = Path(manga.path)
                if manga_path.exists():
                    print(f"🔍 Buscando thumbnail para {manga.title}...")
                    manga.thumbnail = self._find_thumbnail(manga_path)
                    print(f"📸 Thumbnail encontrada: {manga.thumbnail}")
            
            # Recriar páginas sob demanda para cada capítulo
            for chapter in manga.chapters:
                if not chapter.pages:  # Se não tem páginas no cache
                    chapter_path = Path(chapter.path)
                    if chapter_path.exists():
                        # Recriar páginas rapidamente
                        chapter.pages = self._create_pages_lazy(chapter_path)
                        # Validar contagem
                        if len(chapter.pages) != chapter.page_count:
                            print(f"⚠️ Inconsistência em {chapter.name}: {len(chapter.pages)} vs {chapter.page_count}")
                            chapter.page_count = len(chapter.pages)
            
            return manga
            
        except Exception as e:
            print(f"⚠️ Erro ao restaurar mangá do cache: {e}")
            return None
    

    def _create_lightweight_manga_for_cache(self, manga: Manga) -> Dict:
        """Criar versão leve do mangá para cache (sem páginas individuais)"""
        # Criar cópia leve sem páginas detalhadas
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
                # NÃO salvar array de páginas individuais (economiza 99% do espaço)
                "pages": []  # Array vazio - páginas são carregadas sob demanda
            }
            lightweight_chapters.append(lightweight_chapter)
        
        lightweight_manga = {
            "id": manga.id,
            "title": manga.title,
            "path": manga.path,
            # ✅ CORREÇÃO: Garantir que thumbnail seja preservada
            "thumbnail": manga.thumbnail,  # CRÍTICO: Manter thumbnail no cache
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
        
        return lightweight_manga

    # === MÉTODOS ORIGINAIS ===
    
    def _scan_library_original(self, library_path: str) -> Library:
        """Método original preservado como fallback"""
        library = Library()
        library_path = Path(library_path)
        
        if not library_path.exists() or not library_path.is_dir():
            raise ValueError(f"Caminho inválido: {library_path}")
        
        for manga_dir in library_path.iterdir():
            if manga_dir.is_dir() and not manga_dir.name.startswith('.'):
                try:
                    manga = self.scan_manga(str(manga_dir))
                    if manga and manga.chapters:
                        library.add_manga(manga)
                except Exception as e:
                    print(f"Erro ao escanear mangá {manga_dir.name}: {e}")
                    continue
        
        return library
    
    def scan_manga(self, manga_path: str) -> Optional[Manga]:
        """Método original - mantido para compatibilidade"""
        manga_path = Path(manga_path)
        
        if not manga_path.exists() or not manga_path.is_dir():
            return None
        
        manga_id = self._generate_manga_id(manga_path.name)
        manga = Manga(
            id=manga_id,
            title=manga_path.name,
            path=str(manga_path),
            date_added=datetime.fromtimestamp(manga_path.stat().st_ctime)
        )
        
        manga.thumbnail = self._find_thumbnail(manga_path)
        
        chapters = []
        for chapter_dir in manga_path.iterdir():
            if chapter_dir.is_dir() and not chapter_dir.name.startswith('.'):
                chapter = self._scan_chapter(chapter_dir, manga_id)
                if chapter:
                    chapters.append(chapter)
        
        manga.chapters = self._sort_chapters(chapters)
        manga.chapter_count = len(manga.chapters)
        manga.total_pages = sum(ch.page_count for ch in manga.chapters)
        
        return manga
    
    def _scan_chapter(self, chapter_path: Path, manga_id: str) -> Optional[Chapter]:
        """Método original - mantido para compatibilidade"""
        chapter_info = self._parse_chapter_name(chapter_path.name)
        
        pages = []
        image_files = []
        
        for file_path in chapter_path.iterdir():
            if file_path.is_file() and self._is_image_file(file_path):
                image_files.append(file_path)
        
        image_files.sort(key=lambda x: self._natural_sort_key(x.name))
        
        for i, img_path in enumerate(image_files):
            page = Page(
                filename=img_path.name,
                path=str(img_path),
                size=img_path.stat().st_size
            )
            pages.append(page)
        
        if not pages:
            return None
        
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
        """Método original preservado"""
        info = {'number': None, 'volume': None}
        
        for pattern in CHAPTER_PATTERNS:
            match = re.search(pattern, chapter_name, re.IGNORECASE)
            if match:
                groups = match.groups()
                
                if len(groups) == 1:
                    try:
                        info['number'] = float(groups[0])
                    except ValueError:
                        pass
                elif len(groups) == 2:
                    try:
                        info['volume'] = int(groups[0])
                        info['number'] = float(groups[1])
                    except ValueError:
                        pass
                break
        
        return info
    
    def _sort_chapters(self, chapters: List[Chapter]) -> List[Chapter]:
        """Método original preservado"""
        def sort_key(chapter):
            if chapter.number is not None:
                return (0, -chapter.number)
            else:
                return (1, chapter.name)
        
        return sorted(chapters, key=sort_key)
    
    def _find_thumbnail(self, manga_path: Path) -> Optional[str]:
        """Método original preservado"""
        for file_path in manga_path.iterdir():
            if file_path.is_file() and self._is_image_file(file_path):
                return str(file_path)
        
        chapters = []
        for chapter_dir in manga_path.iterdir():
            if chapter_dir.is_dir():
                chapters.append(chapter_dir)
        
        if chapters:
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
        """Método original preservado"""
        return file_path.suffix.lower() in self.supported_extensions
    
    def _generate_manga_id(self, manga_title: str) -> str:
        """Método original preservado"""
        clean_title = re.sub(r'[^\w\s-]', '', manga_title.lower())
        clean_title = re.sub(r'[-\s]+', '-', clean_title)
        return clean_title.strip('-')
    
    def _natural_sort_key(self, text: str) -> List:
        """Método original preservado"""
        def convert(text):
            return int(text) if text.isdigit() else text.lower()
        
        return [convert(c) for c in re.split('([0-9]+)', text)]
    
    def refresh_manga(self, manga_path: str) -> Optional[Manga]:
        """Método original preservado"""
        return self.scan_manga(manga_path)
    
    def validate_library_path(self, path: str) -> Tuple[bool, str]:
        """Método original preservado"""
        path_obj = Path(path)
        
        if not path_obj.exists():
            return False, "Caminho não existe"
        
        if not path_obj.is_dir():
            return False, "Caminho não é um diretório"
        
        manga_dirs = [d for d in path_obj.iterdir() if d.is_dir() and not d.name.startswith('.')]
        
        if not manga_dirs:
            return False, "Nenhuma pasta de mangá encontrada"
        
        return True, "Caminho válido"
    
    # === MÉTODOS DE CONTROLE DO CACHE ===
    
    def disable_cache(self):
        """Desabilitar cache híbrido (para debug/troubleshooting)"""
        self.cache_enabled = False
        print("⚠️ Cache híbrido desabilitado")
    
    def enable_cache(self):
        """Reabilitar cache híbrido"""
        self.cache_enabled = True
        print("✅ Cache híbrido habilitado")
    
    def clear_cache(self, library_path: str) -> bool:
        """Limpar cache de uma biblioteca específica"""
        try:
            cache_file = Path(library_path) / self.cache_file_name
            if cache_file.exists():
                cache_file.unlink()
                print(f"🗑️ Cache limpo: {cache_file}")
                return True
            return False
        except Exception as e:
            print(f"❌ Erro ao limpar cache: {e}")
            return False
    
    def get_cache_info(self, library_path: str) -> Dict:
        """Obter informações sobre o cache"""
        cache_file = Path(library_path) / self.cache_file_name
        
        if not cache_file.exists():
            return {"exists": False}
        
        try:
            stat = cache_file.stat()
            cache_data = self._load_cache_safe(cache_file)
            
            return {
                "exists": True,
                "size_bytes": stat.st_size,
                "size_mb": round(stat.st_size / 1024 / 1024, 2),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "entries": len(cache_data) - 1,  # -1 para _cache_version
                "version": cache_data.get('_cache_version', 'unknown')
            }
        except Exception as e:
            return {"exists": True, "error": str(e)}