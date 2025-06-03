from pydantic_settings import BaseSettings
from pathlib import Path
from typing import List
import os

class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # Configurações gerais
    app_name: str = "Ohara"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Configurações de API
    api_prefix: str = "/api"
    host: str = "localhost"
    port: int = 8000
    
    # Configurações de CORS
    allowed_origins: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000"
    ]
    
    # Configurações de arquivos
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    supported_image_formats: List[str] = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
    supported_archive_formats: List[str] = [".zip", ".rar", ".cbz", ".cbr"]
    
    # Configurações de thumbnail
    thumbnail_size: tuple = (300, 400)
    thumbnail_quality: int = 85
    
    # Configurações de cache
    cache_thumbnails: bool = True
    cache_dir: str = "cache"
    
    # Configurações de banco de dados (SQLite para simplicidade)
    database_url: str = "sqlite:///./ohara.db"
    
    # Configurações de logging
    log_level: str = "INFO"
    log_file: str = "ohara.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Instância global de configurações
_settings = None

def get_settings() -> Settings:
    """Retorna instância singleton das configurações"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

# Constantes úteis
SUPPORTED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
CHAPTER_PATTERNS = [
    r'[Cc]ap[ií]tulo\s*(\d+)',
    r'[Cc]hapter\s*(\d+)',
    r'[Cc]h\s*(\d+)',
    r'[Vv]ol\.?\s*(\d+)\s*[Cc]h\.?\s*(\d+)',
    r'(\d+)(?:\s*-.*)?$'
]