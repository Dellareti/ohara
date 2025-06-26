import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from app.core.services.manga_scanner import MangaScanner


class TestMangaScannerSimple:
    """Testes para MangaScanner simplificado"""
    
    def setup_method(self):
        self.scanner = MangaScanner()
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init(self):
        """Deve inicializar corretamente o scanner"""
        assert self.scanner.cache_enabled is True
        assert hasattr(self.scanner, 'cache')
        assert hasattr(self.scanner, 'chapter_parser')
    
    def test_enable_disable_cache(self):
        """Deve habilitar/desabilitar cache"""
        self.scanner.disable_cache()
        assert self.scanner.cache_enabled is False
        
        self.scanner.enable_cache()
        assert self.scanner.cache_enabled is True
    
    def test_scan_library_nonexistent_path(self):
        """Deve lançar exceção para caminho inexistente"""
        with pytest.raises(ValueError, match="Biblioteca não encontrada"):
            self.scanner.scan_library("/caminho/inexistente")
    
    def test_discover_manga_directories(self):
        """Deve descobrir diretórios de mangá"""
        # Criar estrutura de teste
        (self.temp_dir / "Manga1").mkdir()
        (self.temp_dir / "Manga2").mkdir()
        (self.temp_dir / ".hidden").mkdir()  # Deve ser ignorado
        (self.temp_dir / "arquivo.txt").write_text("texto")  # Deve ser ignorado
        
        manga_dirs = self.scanner._discover_manga_directories(self.temp_dir)
        
        assert len(manga_dirs) == 2
        assert all(d.is_dir() for d in manga_dirs)
        assert not any(d.name.startswith('.') for d in manga_dirs)
    
    def test_discover_chapter_directories(self):
        """Deve descobrir diretórios de capítulos com imagens"""
        manga_dir = self.temp_dir / "Manga1"
        manga_dir.mkdir()
        
        # Capítulo com imagens
        ch1_dir = manga_dir / "Chapter 1"
        ch1_dir.mkdir()
        (ch1_dir / "page1.jpg").write_text("fake image")
        
        # Capítulo sem imagens (deve ser ignorado)
        ch2_dir = manga_dir / "Chapter 2"
        ch2_dir.mkdir()
        
        chapter_dirs = self.scanner._discover_chapter_directories(manga_dir)
        
        assert len(chapter_dirs) == 1
        assert chapter_dirs[0].name == "Chapter 1"
    
    def test_has_images(self):
        """Deve detectar presença de imagens"""
        test_dir = self.temp_dir / "test"
        test_dir.mkdir()
        
        # Sem imagens
        assert self.scanner._has_images(test_dir) is False
        
        # Com imagem
        (test_dir / "image.jpg").write_text("fake image")
        assert self.scanner._has_images(test_dir) is True
    
    def test_find_image_files(self):
        """Deve encontrar arquivos de imagem"""
        test_dir = self.temp_dir / "test"
        test_dir.mkdir()
        
        # Criar arquivos
        (test_dir / "page1.jpg").write_text("fake")
        (test_dir / "page2.png").write_text("fake")
        (test_dir / "text.txt").write_text("fake")  # Não é imagem
        
        image_files = self.scanner._find_image_files(test_dir)
        
        assert len(image_files) == 2
        assert all(f.suffix.lower() in ['.jpg', '.png'] for f in image_files)
    
    def test_generate_manga_id(self):
        """Deve gerar IDs legíveis e consistentes"""
        id1 = self.scanner._generate_manga_id("Manga Name")
        id2 = self.scanner._generate_manga_id("Manga Name")
        id3 = self.scanner._generate_manga_id("Different Name")
        
        # Mesmo nome deve gerar mesmo ID
        assert id1 == id2
        
        # Nomes diferentes devem gerar IDs diferentes
        assert id1 != id3
        
        # ID deve ser legível
        assert id1 == "manga-name"
        assert id3 == "different-name"
    
    @patch('app.core.services.manga_scanner.MangaScanner._discover_manga_directories')
    @patch('app.core.services.manga_scanner.MangaScanner.scan_manga')
    def test_scan_library_with_cache_disabled(self, mock_scan_manga, mock_discover):
        """Deve escanear biblioteca sem usar cache"""
        from app.models.manga import Manga
        from datetime import datetime
        
        # Configurar mocks
        manga_dir = self.temp_dir / "Manga1"
        manga_dir.mkdir()
        mock_discover.return_value = [manga_dir]
        
        # Criar manga válido
        mock_manga = Manga(
            id="manga1",
            title="Test Manga",
            path=str(manga_dir),
            thumbnail=None,
            chapters=[],
            chapter_count=0,
            total_pages=0,
            date_added=datetime.now(),
            date_modified=datetime.now()
        )
        mock_scan_manga.return_value = mock_manga
        
        # Desabilitar cache
        self.scanner.disable_cache()
        
        # Escanear biblioteca
        library = self.scanner.scan_library(str(self.temp_dir))
        
        # Verificar resultados
        assert library.total_mangas == 1
        assert len(library.mangas) == 1
        mock_scan_manga.assert_called_once()
    
    def test_clear_cache(self):
        """Deve limpar cache"""
        # Criar arquivo de cache fake
        cache_file = self.temp_dir / self.scanner.cache.cache_file_name
        cache_file.write_text('{"test": "data"}')
        
        # Limpar cache
        result = self.scanner.clear_cache(str(self.temp_dir))
        
        assert result is True
        assert not cache_file.exists()
    
    def test_get_cache_info(self):
        """Deve retornar informações do cache"""
        # Sem cache
        info = self.scanner.get_cache_info(str(self.temp_dir))
        assert info["exists"] is False
        
        # Com cache
        cache_file = self.temp_dir / self.scanner.cache.cache_file_name
        cache_file.write_text('{"manga1": {"test": "data"}}')
        
        info = self.scanner.get_cache_info(str(self.temp_dir))
        assert info["exists"] is True
        assert info["entries"] == 1
    
    def test_validate_library_path_valid(self):
        """Deve validar caminho válido"""
        # Criar manga de teste
        manga_dir = self.temp_dir / "Test Manga"
        manga_dir.mkdir()
        
        is_valid, message = self.scanner.validate_library_path(str(self.temp_dir))
        assert is_valid is True
        assert message == "Caminho válido"
    
    def test_validate_library_path_nonexistent(self):
        """Deve rejeitar caminho inexistente"""
        is_valid, message = self.scanner.validate_library_path("/caminho/inexistente")
        assert is_valid is False
        assert message == "Caminho não existe"
    
    def test_validate_library_path_not_directory(self):
        """Deve rejeitar arquivo em vez de diretório"""
        test_file = self.temp_dir / "test.txt"
        test_file.write_text("test")
        
        is_valid, message = self.scanner.validate_library_path(str(test_file))
        assert is_valid is False
        assert message == "Caminho não é um diretório"
    
    def test_validate_library_path_empty(self):
        """Deve rejeitar diretório vazio"""
        is_valid, message = self.scanner.validate_library_path(str(self.temp_dir))
        assert is_valid is False
        assert message == "Nenhuma pasta de mangá encontrada"