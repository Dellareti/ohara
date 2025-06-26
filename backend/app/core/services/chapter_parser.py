import re
from typing import Dict, List

from app.core.config import CHAPTER_PATTERNS
from app.models.manga import Chapter


class ChapterParser:
    """
    Parser especializado para análise e processamento de capítulos de mangá.
    
    Responsável por:
    - Análise de nomes de capítulos usando regex
    - Extração de números de capítulo e volume
    - Ordenação natural de capítulos
    - Determinação de numeração sequencial
    """
    
    @staticmethod
    def parse_chapter_name_enhanced(chapter_name: str) -> Dict:
        """
        Parser avançado de nomes de capítulos com suporte a múltiplos padrões.
        
        Detecta automaticamente números de capítulo e volume usando regex
        otimizadas. Suporta padrões em português, inglês e variações comuns
        encontradas em bibliotecas de mangá.
        
        Args:
            chapter_name (str): Nome do diretório do capítulo
            
        Returns:
            Dict: {
                'number': float ou None - Número do capítulo detectado
                'volume': int ou None - Número do volume (se presente)
            }
            
        Supported Patterns:
            - "Vol. 1, Ch. 15" / "Volume 1 Chapter 15"
            - "Capítulo 1" / "Chapter 1" / "Ch. 1"
            - "001" / "1 - Título" / "1.5"
            - Case-insensitive matching
            - Suporte a capítulos decimais (1.5, 2.1)
        """
        info = {'number': None, 'volume': None}
        
        enhanced_patterns = [
            r'[Vv]ol\.?\s*(\d+)[,]?\s*[Cc]h\.?\s*(\d+\.?\d*)',  # "Vol. 1, Ch. 15"
            r'Volume\s*(\d+)\s*Chapter\s*(\d+\.?\d*)',  # "Volume 1 Chapter 1"
            r'[Cc]hapter\s*(\d+\.?\d*)',  # "Chapter 1"
            r'[Cc]ap[ií]tulo\s*(\d+\.?\d*)',  # "Capítulo 1"
            r'[Cc]h\.?\s*(\d+\.?\d*)',  # "Ch. 1"
            r'^(\d+\.?\d*)(?:\s*[-_].*)?',  # "1 - Título"
            r'(\d+\.?\d*)(?:\s|$)',  # Números soltos
        ]

        for pattern in enhanced_patterns:
            match = re.search(pattern, chapter_name, re.IGNORECASE)
            if match:
                groups = match.groups()
                
                if len(groups) == 1:
                    try:
                        info['number'] = float(groups[0])
                        break
                    except ValueError:
                        continue
                elif len(groups) == 2:
                    try:
                        info['volume'] = int(groups[0])
                        info['number'] = float(groups[1])
                        break
                    except ValueError:
                        continue
        
        return info
    
    @staticmethod
    def parse_chapter_name(chapter_name: str) -> Dict:
        """
        Parser básico de nomes de capítulos usando padrões de configuração.
        
        Args:
            chapter_name (str): Nome do capítulo
            
        Returns:
            Dict: Informações extraídas do nome
        """
        info = {'number': None, 'volume': None}
        
        for pattern in CHAPTER_PATTERNS:
            match = re.search(pattern, chapter_name, re.IGNORECASE)
            if match:
                groups = match.groups()
                
                if len(groups) == 1:
                    try:
                        info['number'] = float(groups[0])
                    except ValueError:
                        pass
                elif len(groups) == 2:
                    try:
                        info['volume'] = int(groups[0])
                        info['number'] = float(groups[1])
                    except ValueError:
                        pass
                break
        
        return info
    
    @staticmethod
    def sort_chapters(chapters: List[Chapter]) -> List[Chapter]:
        """
        Ordena capítulos por número (decrescente) e depois por nome.
        
        Args:
            chapters (List[Chapter]): Lista de capítulos para ordenar
            
        Returns:
            List[Chapter]: Lista ordenada de capítulos
        """
        def sort_key(chapter):
            if chapter.number is not None:
                return (0, -chapter.number)
            else:
                return (1, chapter.name)
        
        return sorted(chapters, key=sort_key)
    
    @staticmethod
    def determine_chapter_number(chapter_info: dict, sequential_index: int, 
                               page_count: int, chapter_name: str) -> str:
        """
        Determinar número do capítulo usando múltiplas estratégias.
        
        Args:
            chapter_info (dict): Informações extraídas do parsing
            sequential_index (int): Índice sequencial do capítulo
            page_count (int): Número de páginas do capítulo
            chapter_name (str): Nome original do capítulo
            
        Returns:
            str: Número do capítulo determinado
        """
        if chapter_info['number'] is not None:
            return str(chapter_info['number'])
        
        return str(sequential_index)
    
    @staticmethod
    def natural_sort_key(text: str) -> List:
        """
        Gera chave de ordenação natural para strings com números.
        
        Implementa algoritmo de ordenação natural que trata números como
        inteiros em vez de strings, garantindo ordem lógica:
        
        Ordenação alfabética: ["1", "10", "2", "20"]
        Ordenação natural: ["1", "2", "10", "20"]
        
        Args:
            text (str): String a ser convertida para chave de ordenação
            
        Returns:
            List: Lista mista de inteiros e strings para ordenação
        """
        def convert(text):
            return int(text) if text.isdigit() else text.lower()
        
        return [convert(c) for c in re.split('([0-9]+)', text)]