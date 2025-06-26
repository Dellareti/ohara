import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from app.core.services.manga_scanner import MangaScanner
from app.models.manga import Chapter, Library

@pytest.fixture
def library_directory():
    directory = tempfile.mkdtemp()
    library_path = Path(directory) / "test_library"
    library_path.mkdir()

    # Mangá 1: One Piece
    one_piece = library_path / "One Piece"
    one_piece.mkdir()

    chapter_data = [
        ("Chapter 001", 5),
        ("Chapter 002", 4),
        ("Chapter 003", 6),
        ("Chapter 1.5 - Extra", 3)
    ]

    for chapter_name, page_count in chapter_data:
        chapter = one_piece / chapter_name
        chapter.mkdir()

        for j in range(1, page_count + 1):
            page_file = chapter / f"page_{j:02d}.jpg"
            page_file.write_text(f"fake image data {j}")

    thumbnail = one_piece / "cover.jpg"
    thumbnail.write_text("fake thumbnail data")

    # Mangá 2: Naruto - Sem thumbnail
    naruto = library_path / "Naruto"
    naruto.mkdir()

    naruto_chapters = [
        ("Cap 001 - Uzumaki Naruto", 3),
        ("Capítulo 2", 4),
        ("Ch. 3", 2)
    ]

    for chapter_name, page_count in naruto_chapters:
        chapter = naruto / chapter_name
        chapter.mkdir()

        for j in range(1, page_count + 1):
            page_file = chapter / f"{j:03d}.png"
            page_file.write_text(f"fake naruto page {j}")

    # Mangá 3: Attack on Titan - Formatos mistos
    aot = library_path / "Attack on Titan"
    aot.mkdir()

    aot_chapters = [
        ("Volume 1 Chapter 1", 20),
        ("Vol. 1, Ch. 2", 18),
        ("015 - Final Battle", 25)
    ]

    for chapter_name, page_count in aot_chapters:
        chapter = aot / chapter_name
        chapter.mkdir()

        for j in range(1, page_count + 1):
            page_file = chapter / f"page{j:03d}.webp"
            page_file.write_text(f"fake aot page {j}")

    # Mangá 4: Vazio
    empty = library_path / "Empty Manga"
    empty.mkdir()

    # Mangá 5: Só arquivos, sem capítulos
    invalid = library_path / "Invalid Manga"
    invalid.mkdir()
    (invalid / "readme.txt").write_text("Not a manga")
    (invalid / "info.json").write_text('{"title": "test"}')

    yield str(library_path)

    # Cleanup
    shutil.rmtree(directory)


@pytest.fixture
def empty_directory():
    directory = tempfile.mkdtemp()
    yield directory
    shutil.rmtree(directory)


@pytest.fixture
def sample_chapters():
    return [
        Chapter(
            id="test-ch-10", name="Chapter 10", number=10.0, volume=None,
            path="/test/ch10", pages=[], page_count=15,
            date_added=datetime.now()
        ),
        Chapter(
            id="test-ch-2", name="Chapter 2", number=2.0, volume=None,
            path="/test/ch2", pages=[], page_count=12,
            date_added=datetime.now()
        ),
        Chapter(
            id="test-ch-extra", name="Extra Chapter", number=None, volume=None,
            path="/test/extra", pages=[], page_count=8,
            date_added=datetime.now()
        ),
        Chapter(
            id="test-ch-1.5", name="Chapter 1.5", number=1.5, volume=None,
            path="/test/ch1.5", pages=[], page_count=10,
            date_added=datetime.now()
        )
    ]


class TestMangaScannerPublicMethods:
    def setup_method(self):
        self.scanner = MangaScanner()

    def test_scan_library(self, library_directory):
        library = self.scanner.scan_library(library_directory)

        assert isinstance(library, Library)
        assert library.total_mangas >= 3

        one_piece = library.get_manga("one-piece")
        assert one_piece is not None
        assert one_piece.title == "One Piece"
        assert one_piece.chapter_count == 4
        assert one_piece.thumbnail is not None

        naruto = library.get_manga("naruto")
        assert naruto is not None
        assert naruto.chapter_count == 3

    def test_scan_library__fallback_on_cache_error(self, library_directory):
        with patch.object(self.scanner, '_scan_library_with_cache', side_effect=Exception("Cache error")):
            library = self.scanner.scan_library(library_directory)
            assert isinstance(library, Library)
            assert library.total_mangas > 0

    def test_scan_library__invalid_path(self):
        with pytest.raises(ValueError, match="Caminho inválido"):
            self.scanner.scan_library("/non/existent/path")

    def test_scan_library__empty_directory(self, empty_directory):
        library = self.scanner.scan_library(empty_directory)
        assert isinstance(library, Library)
        assert library.total_mangas == 0
        assert len(library.mangas) == 0

    def test_scan_manga__complete_structure(self, library_directory):
        one_piece_path = Path(library_directory) / "One Piece"
        manga = self.scanner.scan_manga(str(one_piece_path))

        assert manga is not None
        assert manga.title == "One Piece"
        assert manga.id == "one-piece"
        assert manga.chapter_count == 4
        assert manga.total_pages > 0
        assert manga.thumbnail is not None

        assert manga.chapters[0].number == 3.0
        assert manga.chapters[1].number == 2.0
        assert manga.chapters[2].number == 1.5
        assert manga.chapters[3].number == 1.0

    def test_scan_manga__nonexistent_path(self):
        result = self.scanner.scan_manga("/non/existent/path")
        assert result is None

    def test_scan_manga__empty_manga(self, library_directory):
        empty_path = Path(library_directory) / "Empty Manga"
        manga = self.scanner.scan_manga(str(empty_path))

        assert manga is not None
        assert manga.title == "Empty Manga"
        assert manga.chapter_count == 0
        assert len(manga.chapters) == 0
        assert manga.total_pages == 0


class TestMangaScannerCriticalMethods:
    def setup_method(self):
        self.scanner = MangaScanner()

    def test_parse_chapter_name_enhanced__comprehensive(self):
        test_cases = [
            # Formatos básicos
            ("Chapter 001", {"number": 1.0, "volume": None}),
            ("Capítulo 2", {"number": 2.0, "volume": None}),
            ("Ch. 3", {"number": 3.0, "volume": None}),

            # Formatos com volume
            ("Vol. 1, Ch. 15", {"number": 15.0, "volume": 1}),
            ("Volume 2 Chapter 5", {"number": 5.0, "volume": 2}),
            ("Vol 3 Ch 10", {"number": 10.0, "volume": 3}),

            # Formatos numéricos
            ("001 - Título", {"number": 1.0, "volume": None}),
            ("025", {"number": 25.0, "volume": None}),

            # Capítulos especiais
            ("Chapter 1.5", {"number": 1.5, "volume": None}),
            ("Ch. 0.1", {"number": 0.1, "volume": None}),

            # Casos sem match
            ("Random Text", {"number": None, "volume": None}),
            ("Extra Chapter", {"number": None, "volume": None}),
            ("", {"number": None, "volume": None})
        ]

        for chapter_name, expected in test_cases:
            result = self.scanner.chapter_parser.parse_chapter_name_enhanced(chapter_name)
            assert result["number"] == expected["number"], f"Falhou para: '{chapter_name}'"
            if expected["volume"] is not None:
                assert result["volume"] == expected["volume"], f"Volume falhou para: '{chapter_name}'"

    def test_sort_chapters__mixed_numbering(self, sample_chapters):
        sorted_chapters = self.scanner.chapter_parser.sort_chapters(sample_chapters)

        assert sorted_chapters[0].number == 10.0  # Chapter 10
        assert sorted_chapters[1].number == 2.0  # Chapter 2
        assert sorted_chapters[2].number == 1.5  # Chapter 1.5
        assert sorted_chapters[3].number is None  # Extra Chapter

    def test_natural_sort_key__comprehensive(self):
        test_cases = [
            # Caso 1: Páginas numeradas
            (["page1.jpg", "page10.jpg", "page2.jpg", "page21.jpg"],
             ["page1.jpg", "page2.jpg", "page10.jpg", "page21.jpg"]),

            # Caso 2: Capítulos
            (["ch1", "ch10", "ch2", "ch100", "ch3"],
             ["ch1", "ch2", "ch3", "ch10", "ch100"]),

            # Caso 3: Mistura texto/número
            (["a10", "a2", "a1", "b1", "a20"],
             ["a1", "a2", "a10", "a20", "b1"])
        ]

        for items, expected_order in test_cases:
            sorted_items = sorted(items, key=self.scanner.chapter_parser.natural_sort_key)
            assert sorted_items == expected_order

    def test_generate_manga_id__edge_cases(self):
        test_cases = [
            ("One Piece", "one-piece"),
            ("Attack on Titan", "attack-on-titan"),
            ("Dr. Stone", "dr-stone"),
            ("Demon Slayer: Kimetsu no Yaiba", "demon-slayer-kimetsu-no-yaiba"),
            ("Manga!@#$%Name", "manga-name"),
            ("   Multiple   Spaces   ", "multiple-spaces"),
            ("--Special--Characters--", "special-characters"),
            ("", ""),
            ("123", "123"),
            ("A", "a")
        ]

        for title, expected_id in test_cases:
            result = self.scanner._generate_manga_id(title)
            assert result == expected_id, f"Falhou para: '{title}'"


class TestMangaScannerValidation:
    def setup_method(self):
        self.scanner = MangaScanner()

    def test_validate_library_path__valid(self, library_directory):
        is_valid, message = self.scanner.validate_library_path(library_directory)
        assert is_valid is True
        assert message == "Caminho válido"

    def test_validate_library_path__nonexistent_path(self):
        is_valid, message = self.scanner.validate_library_path("/non/existent/path")
        assert is_valid is False
        assert message == "Caminho não existe"

    def test_validate_library_path__path_is_file(self, empty_directory):
        file_path = Path(empty_directory) / "test_file.txt"
        file_path.write_text("test")

        is_valid, message = self.scanner.validate_library_path(str(file_path))
        assert is_valid is False
        assert message == "Caminho não é um diretório"

    def test_validate_library_path__empty_library_dir(self, empty_directory):
        is_valid, message = self.scanner.validate_library_path(empty_directory)
        assert is_valid is False
        assert message == "Nenhuma pasta de mangá encontrada"

    def test_image_file__validation(self):
        valid_cases = [
            ("test.jpg", True),
            ("test.jpeg", True),
            ("test.png", True),
            ("test.gif", True),
            ("test.webp", True),
            ("test.bmp", True),
            ("TEST.JPG", True),
        ]

        invalid_cases = [
            ("test.txt", False),
            ("test.pdf", False),
            ("test.zip", False),
            ("test", False),
            ("test.", False)
        ]

        for filename, expected in valid_cases + invalid_cases:
            file_path = Path(filename)
            result = self.scanner._is_image_file(file_path)
            assert result == expected, f"_is_image_file falhou para: {filename}"

        for filename, expected in valid_cases + invalid_cases:
            result = self.scanner._is_image_file_name(filename)
            assert result == expected, f"_is_image_file_name falhou para: {filename}"