from datetime import datetime

import pytest

from app.core.services.chapter_parser import ChapterParser
from app.models.manga import Chapter

class TestChapterParserMethods:
    def setup_method(self):
        self.parser = ChapterParser()

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
            result = self.parser.parse_chapter_name_enhanced(chapter_name)
            assert result["number"] == expected["number"], f"Falhou para: '{chapter_name}'"
            if expected["volume"] is not None:
                assert result["volume"] == expected["volume"], f"Volume falhou para: '{chapter_name}'"

    def test_parse_chapter_name__basic_patterns(self):
        # Teste o parser básico para compatibilidade
        result = self.parser.parse_chapter_name("Chapter 1")
        assert result["number"] == 1.0
        assert result["volume"] is None

    def test_sort_chapters__mixed_numbering(self):
        chapters = [
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

        sorted_chapters = self.parser.sort_chapters(chapters)

        assert sorted_chapters[0].number == 10.0  # Chapter 10
        assert sorted_chapters[1].number == 2.0   # Chapter 2
        assert sorted_chapters[2].number == 1.5   # Chapter 1.5
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
            sorted_items = sorted(items, key=self.parser.natural_sort_key)
            assert sorted_items == expected_order

    def test_determine_chapter_number__with_parsed_number(self):
        chapter_info = {"number": 5.0, "volume": None}
        result = self.parser.determine_chapter_number(
            chapter_info, sequential_index=10, page_count=15, chapter_name="Chapter 5"
        )
        assert result == "5.0"

    def test_determine_chapter_number__fallback_to_sequential(self):
        chapter_info = {"number": None, "volume": None}
        result = self.parser.determine_chapter_number(
            chapter_info, sequential_index=3, page_count=15, chapter_name="Extra Chapter"
        )
        assert result == "3"

    def test_natural_sort_key__edge_cases(self):
        # Teste casos extremos
        assert self.parser.natural_sort_key("") == [""]
        assert self.parser.natural_sort_key("123") == ["", 123, ""]
        assert self.parser.natural_sort_key("abc") == ["abc"]
        
        # Números no meio
        result = self.parser.natural_sort_key("chapter5page10")
        assert result == ["chapter", 5, "page", 10, ""]