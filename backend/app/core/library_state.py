"""
Gerenciador de estado da biblioteca thread-safe
"""
import threading
from pathlib import Path
from typing import Optional
from datetime import datetime


class LibraryState:
    """
    Classe thread-safe para gerenciar o estado global da biblioteca
    """
    
    def __init__(self):
        self._current_path: Optional[str] = None
        self._lock = threading.RLock()
        self._library_path_file = "last_library_path.txt"
    
    @property
    def current_path(self) -> Optional[str]:
        """Retorna o caminho atual da biblioteca"""
        with self._lock:
            return self._current_path
    
    @current_path.setter
    def current_path(self, path: Optional[str]) -> None:
        """Define o caminho atual da biblioteca"""
        with self._lock:
            self._current_path = path
            if path:
                self._save_to_file(path)
            else:
                self._clear_file()
    
    def load_from_file(self) -> Optional[str]:
        """Carrega o caminho da biblioteca do arquivo"""
        try:
            if Path(self._library_path_file).exists():
                with open(self._library_path_file, 'r', encoding='utf-8') as f:
                    path = f.read().strip()
                    if path and Path(path).exists():
                        with self._lock:
                            self._current_path = path
                        print(f"📂 Caminho carregado: {path}")
                        return path
                    else:
                        print(f"⚠️ Caminho salvo não existe mais: {path}")
        except Exception as e:
            print(f"❌ Erro ao carregar caminho: {e}")
        return None
    
    def _save_to_file(self, path: str) -> None:
        """Salva o caminho no arquivo"""
        try:
            with open(self._library_path_file, 'w', encoding='utf-8') as f:
                f.write(path)
            print(f"💾 Caminho salvo: {path}")
        except Exception as e:
            print(f"❌ Erro ao salvar caminho: {e}")
    
    def _clear_file(self) -> None:
        """Remove o arquivo de caminho"""
        try:
            if Path(self._library_path_file).exists():
                Path(self._library_path_file).unlink()
                print(f"🗑️ Arquivo de caminho removido")
        except Exception as e:
            print(f"❌ Erro ao remover arquivo: {e}")
    
    def clear(self) -> None:
        """Limpa o estado atual"""
        with self._lock:
            self._current_path = None
            self._clear_file()
    
    def is_configured(self) -> bool:
        """Verifica se há uma biblioteca configurada"""
        with self._lock:
            return self._current_path is not None
    
    def validate_current_path(self) -> bool:
        """Valida se o caminho atual ainda existe"""
        with self._lock:
            if not self._current_path:
                return False
            return Path(self._current_path).exists()


# Instância global thread-safe
library_state = LibraryState()