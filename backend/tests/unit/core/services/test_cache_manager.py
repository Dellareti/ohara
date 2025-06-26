import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import patch

import pytest

from app.core.services.cache_manager import CacheManager
from app.models.manga import Manga, Chapter

@pytest.fixture
def temp_directory():
    directory = tempfile.mkdtemp()
    yield Path(directory)
    shutil.rmtree(directory)

@pytest.fixture
def sample_manga():
    return Manga(
        id="test-manga",
        title="Test Manga",
        path="/test/path",
        chapters=[
            Chapter(
                id="test-ch-1",
                name="Chapter 1",
                number=1.0,
                volume=None,
                path="/test/path/chapter1",
                pages=[],
                page_count=10,
                date_added=datetime.now()
            )
        ],
        chapter_count=1,
        total_pages=10,
        date_added=datetime.now()
    )


class TestCacheManagerMethods:
    def setup_method(self):
        self.cache_manager = CacheManager()

    def test_load_cache__nonexistent_file(self, temp_directory):
        cache_file = temp_directory / "nonexistent.json"
        result = self.cache_manager.load_cache(cache_file)
        assert result == {}

    def test_load_cache__valid_cache(self, temp_directory):
        cache_file = temp_directory / "cache.json"
        cache_data = {
            "_cache_version": "1.0",
            "test-manga": {
                "manga_data": {"id": "test-manga", "title": "Test"},
                "cache_timestamp": 123456789,
                "dir_mtime": 123456789,
                "cache_version": "1.0"
            }
        }
        
        import json
        cache_file.write_text(json.dumps(cache_data))
        
        result = self.cache_manager.load_cache(cache_file)
        assert result == cache_data

    def test_load_cache__invalid_version(self, temp_directory):
        cache_file = temp_directory / "cache.json"
        cache_data = {
            "_cache_version": "0.9",
            "test-manga": {}
        }
        
        import json
        cache_file.write_text(json.dumps(cache_data))
        
        result = self.cache_manager.load_cache(cache_file)
        assert result == {}

    def test_save_cache(self, temp_directory, sample_manga):
        cache_file = temp_directory / "cache.json"
        
        # Mock manga.path para um diretório que existe
        sample_manga.path = str(temp_directory)
        
        self.cache_manager.save_cache(cache_file, [sample_manga])
        
        assert cache_file.exists()
        
        # Verificar conteúdo
        import json
        content = json.loads(cache_file.read_text())
        assert "_cache_version" in content
        assert "test-manga" in content

    def test_can_use_cache__no_entry(self, temp_directory):
        test_dir = temp_directory / "test"
        test_dir.mkdir()
        
        result = self.cache_manager.can_use_cache(test_dir, None)
        assert result is False

    def test_can_use_cache__wrong_version(self, temp_directory):
        test_dir = temp_directory / "test"
        test_dir.mkdir()
        
        cache_entry = {
            "cache_version": "0.9",
            "dir_mtime": test_dir.stat().st_mtime
        }
        
        result = self.cache_manager.can_use_cache(test_dir, cache_entry)
        assert result is False

    def test_can_use_cache__valid_entry(self, temp_directory):
        test_dir = temp_directory / "test"
        test_dir.mkdir()
        
        cache_entry = {
            "cache_version": "1.0",
            "dir_mtime": test_dir.stat().st_mtime
        }
        
        result = self.cache_manager.can_use_cache(test_dir, cache_entry)
        assert result is True

    def test_restore_manga_from_cache(self):
        manga_data = {
            "id": "test-manga",
            "title": "Test Manga",
            "path": "/test/path",
            "chapters": [],
            "chapter_count": 0,
            "total_pages": 0,
            "date_added": datetime.now().isoformat()
        }
        
        result = self.cache_manager.restore_manga_from_cache(manga_data)
        assert result is not None
        assert result.id == "test-manga"
        assert result.title == "Test Manga"

    def test_clear_cache(self, temp_directory):
        cache_file = temp_directory / ".ohara_cache.json"
        cache_file.write_text("{}")
        
        result = self.cache_manager.clear_cache(str(temp_directory))
        assert result is True
        assert not cache_file.exists()

    def test_clear_cache__nonexistent(self, temp_directory):
        result = self.cache_manager.clear_cache(str(temp_directory))
        assert result is False

    def test_get_cache_info__exists(self, temp_directory):
        cache_file = temp_directory / ".ohara_cache.json"
        cache_data = {"_cache_version": "1.0", "test": {}}
        
        import json
        cache_file.write_text(json.dumps(cache_data))
        
        result = self.cache_manager.get_cache_info(str(temp_directory))
        assert result["exists"] is True
        assert result["entries"] == 1
        assert result["version"] == "1.0"

    def test_get_cache_info__not_exists(self, temp_directory):
        result = self.cache_manager.get_cache_info(str(temp_directory))
        assert result["exists"] is False