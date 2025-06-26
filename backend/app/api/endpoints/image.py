import logging
import urllib.parse
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.core.library_state import library_state

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/api/image", tags=["assets"], summary="Servir imagem")
async def serve_image(path: str):
    """
    Serve arquivos de imagem da biblioteca de mangás com validação de segurança.
    
    Args:
        path: Caminho codificado da imagem a ser servida
    
    Returns:
        FileResponse: Arquivo de imagem requisitado
        
    Raises:
        HTTPException: Se a biblioteca não estiver configurada, arquivo não encontrado
                      ou fora dos limites de segurança
    """
    
    try:
        logger.info(f"[IMAGE] Path recebido: {path}")
        
        if not library_state.current_path:
            raise HTTPException(status_code=400, detail="Biblioteca não configurada")
        
        decoded_path = urllib.parse.unquote(path)
        logger.info(f"[IMAGE] Path decodificado: {decoded_path}")
        
        # Detectar e corrigir duplo encoding
        if "/api/image?path=" in decoded_path:
            logger.info("[IMAGE] Corrigindo duplo encoding...")
            import urllib.parse as urlparse
            parsed = urlparse.urlparse(decoded_path)
            if parsed.query:
                query_params = urlparse.parse_qs(parsed.query)
                if 'path' in query_params:
                    decoded_path = query_params['path'][0]
                    logger.info(f"[IMAGE] Caminho real extraído: {decoded_path}")
                else:
                    raise HTTPException(status_code=400, detail="Parâmetro 'path' não encontrado")
        
        # Resolver caminhos absolutos
        file_path = Path(decoded_path).resolve()
        library_root = Path(library_state.current_path).resolve()
        
        logger.info(f"[IMAGE] Arquivo: {file_path}")
        logger.info(f"[IMAGE] Biblioteca: {library_root}")
        
        # Validar que está dentro da biblioteca
        if not str(file_path).startswith(str(library_root)):
            logger.info(f"Path fora da biblioteca: {file_path}")
            raise HTTPException(status_code=404, detail="Arquivo não encontrado")
        
        # Validar que existe e é arquivo
        if not file_path.exists() or not file_path.is_file():
            logger.info(f"Arquivo não encontrado: {file_path}")
            raise HTTPException(status_code=404, detail="Arquivo não encontrado")
        
        # Validar extensão de imagem por segurança
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
        if file_path.suffix.lower() not in image_extensions:
            logger.warning(f"Tentativa de acesso a arquivo não-imagem: {file_path}")
            raise HTTPException(status_code=400, detail="Tipo de arquivo não permitido")
        
        logger.info(f"Servindo imagem: {file_path.name}")
        return FileResponse(path=str(file_path))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Erro inesperado: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")