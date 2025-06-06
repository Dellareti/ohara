from pydantic_settings import BaseSettings
from pydantic import Field
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
    allowed_origins: List[str] = Field(default=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000"
    ])
    
    # Configurações de arquivos
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    supported_image_formats: List[str] = Field(default=[".jpg", ".jpeg", ".png", ".gif", ".webp"])
    supported_archive_formats: List[str] = Field(default=[".zip", ".rar", ".cbz", ".cbr"])
    
    # Configurações de thumbnail
    thumbnail_size: tuple = (300, 400)
    thumbnail_quality: int = 85
    
    # Configurações de cache
    cache_thumbnails: bool = True
    cache_dir: str = "cache"
    
    # Configurações de banco de dados 
    database_url: str = "sqlite:///./ohara.db"
    
    # Configurações de logging
    log_level: str = "INFO"
    log_file: str = "ohara.log"
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False
    }

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
    r'Vol\.\s*\d+,\s*Ch\.\s*(\d+\.?\d*)',  # "Vol. 1, Ch. 1.5"
    r'Volume\s*\d+\s*Chapter\s*(\d+\.?\d*)', # "Volume 1 Chapter 1"
    r'[Vv]ol\.?\s*(\d+)\s*[Cc]h\.?\s*(\d+\.?\d*)', # "Vol 1 Ch 2"
    r'[Cc]hapter\s*(\d+\.?\d*)', # "Chapter 1"
    r'[Cc]ap[ií]tulo\s*(\d+\.?\d*)', # "Capítulo 1"
    r'[Cc]h\.?\s*(\d+\.?\d*)', # "Ch. 1" ou "Ch 1"
    r'^(\d+\.?\d*)(?:\s*[-_].*)?', # "1 - Título" ou "1_titulo"
    r'(\d+\.?\d*)(?:\s|$)', # Números decimais como "1.5"
]