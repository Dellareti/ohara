import logging
import urllib.parse
from pathlib import Path

from app.core.library_state import library_state

logger = logging.getLogger(__name__)


def create_image_url(file_path):
    """
    Cria uma URL da API para servir uma imagem baseada no caminho do arquivo.
    
    Args:
        file_path: Caminho absoluto para o arquivo de imagem
    
    Returns:
        str: URL da API para acessar a imagem ou None se inválido
    """
    
    if not file_path:
        return None
    
    try:
        # Verificar se é arquivo de imagem
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
        file_path_obj = Path(file_path)
        
        if file_path_obj.suffix.lower() not in image_extensions:
            logger.warning(f"Arquivo não é imagem: {file_path}")
            return None
        
        # Verificar se arquivo existe
        if not file_path_obj.exists():
            logger.warning(f"Arquivo de imagem não encontrado: {file_path}")
            return None
        
        # Verificar se está dentro da biblioteca (segurança)
        if library_state.current_path:
            try:
                library_path = Path(library_state.current_path).resolve()
                file_absolute = file_path_obj.resolve()
                
                # Verificar se o arquivo está dentro da biblioteca
                try:
                    file_absolute.relative_to(library_path)
                except ValueError:
                    logger.warning(f"Arquivo fora da biblioteca: {file_path}")
                    return None
                    
            except Exception as e:
                logger.warning(f"Erro ao verificar segurança do caminho: {e}")
                return None
        
        # Encode do caminho para URL
        encoded_path = urllib.parse.quote(str(file_path_obj), safe='')
        
        return f"/api/image?path={encoded_path}"
        
    except Exception as e:
        logger.warning(f"Erro ao criar URL da imagem {file_path}: {str(e)}")
        return None