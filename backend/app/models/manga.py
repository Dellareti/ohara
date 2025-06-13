from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict

class Page(BaseModel):
    filename: str
    path: str
    size: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None

class Chapter(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "one-piece-ch-1001",
                "name": "Capítulo 1001",
                "number": 1001,
                "volume": 100,
                "path": "/path/to/manga/One Piece/Capítulo 1001",
                "page_count": 19,
                "pages": []
            }
        }
    )
    
    id: str = Field(..., description="ID único do capítulo")
    name: str = Field(..., description="Nome do capítulo")
    number: Optional[float] = Field(None, description="Número do capítulo")
    volume: Optional[int] = Field(None, description="Número do volume")
    path: str = Field(..., description="Caminho da pasta do capítulo")
    pages: List[Page] = Field(default_factory=list, description="Lista de páginas")
    page_count: int = Field(0, description="Número total de páginas")
    date_added: datetime = Field(default_factory=datetime.now)

class Manga(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "one-piece",
                "title": "One Piece",
                "path": "/path/to/manga/One Piece",
                "thumbnail": "/static/thumbnails/one-piece.jpg",
                "chapter_count": 1050,
                "total_pages": 20000,
                "author": "Eiichiro Oda",
                "status": "Ongoing",
                "genres": ["Action", "Adventure", "Shounen"]
            }
        }
    )
    
    id: str = Field(..., description="ID único do mangá")
    title: str = Field(..., description="Título do mangá")
    path: str = Field(..., description="Caminho da pasta do mangá")
    thumbnail: Optional[str] = Field(None, description="Caminho da thumbnail")
    chapters: List[Chapter] = Field(default_factory=list, description="Lista de capítulos")
    chapter_count: int = Field(0, description="Número total de capítulos")
    total_pages: int = Field(0, description="Número total de páginas")
    
    # Metadados opcionais
    author: Optional[str] = None
    artist: Optional[str] = None
    status: Optional[str] = None
    genres: List[str] = Field(default_factory=list)
    description: Optional[str] = None
    
    # Timestamps
    date_added: datetime = Field(default_factory=datetime.now)
    date_modified: datetime = Field(default_factory=datetime.now)

class Library(BaseModel):
    mangas: List[Manga] = Field(default_factory=list)
    total_mangas: int = Field(0, description="Total de mangás na biblioteca")
    total_chapters: int = Field(0, description="Total de capítulos")
    total_pages: int = Field(0, description="Total de páginas")
    last_updated: datetime = Field(default_factory=datetime.now)
    
    def add_manga(self, manga: Manga) -> None:
        existing = next((m for m in self.mangas if m.id == manga.id), None)
        if existing:
            self.mangas.remove(existing)
        
        self.mangas.append(manga)
        self._update_stats()
    
    def remove_manga(self, manga_id: str) -> bool:
        manga = next((m for m in self.mangas if m.id == manga_id), None)
        if manga:
            self.mangas.remove(manga)
            self._update_stats()
            return True
        return False
    
    def get_manga(self, manga_id: str) -> Optional[Manga]:
        return next((m for m in self.mangas if m.id == manga_id), None)
    
    def search(self, query: str) -> List[Manga]:
        query = query.lower()
        return [m for m in self.mangas if query in m.title.lower()]
    
    def _update_stats(self) -> None:
        self.total_mangas = len(self.mangas)
        self.total_chapters = sum(m.chapter_count for m in self.mangas)
        self.total_pages = sum(m.total_pages for m in self.mangas)
        self.last_updated = datetime.now()

# Modelos de Request/Response para API
class LibraryResponse(BaseModel):
    library: Library
    message: str = "Success"

class MangaResponse(BaseModel):
    manga: Manga
    message: str = "Success"

class ChapterResponse(BaseModel):
    chapter: Chapter
    message: str = "Success"