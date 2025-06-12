# TODO - Melhorias do Projeto Ohara

## Problemas RESOLVIDOS

- [x] **Import duplicado do MangaScanner** em main.py
- [x] **Endpoint duplicado** `/api/manga/{manga_id}
- [x] **Variável global** CURRENT_LIBRARY_PATH sem sincronização thread-safe
- [x] **Import circular** potencial em reader.py com `from app.main import CURRENT_LIBRARY_PATH`

## Problemas Urgentes

- [ ] **Código duplicado massivo** entre endpoints POST e GET de scan-library (248 linhas duplicadas em main.py:196-444)
  - **Impacto**: Dificuldade de manutenção, inconsistências
  - **Solução**: Extrair lógica comum para função `_scan_library_common()`

- [ ] **Arquivo main.py muito grande** com 1034 linhas e múltiplas responsabilidades
  - **Impacto**: Dificulta navegação e manutenção
  - **Solução**: Dividir em módulos:
    - `endpoints/library.py` - Endpoints de biblioteca
    - `endpoints/manga.py` - Endpoints de mangá  
    - `endpoints/cache.py` - Endpoints de cache
    - `endpoints/debug.py` - Endpoints de debug

- [ ] **Classe MangaScanner complexa demais** (789 linhas, múltiplas responsabilidades)
  - **Impacto**: Hard to test, maintain and extend
  - **Solução**: Separar em:
    - `MangaScanner` - Lógica principal
    - `CacheManager` - Gerenciamento de cache
    - `ChapterParser` - Parsing de capítulos

- [ ] **Métodos obsoletos no MangaScanner** 
  - **Impacto**: Confusão, código morto
  - **Solução**: Remover métodos marcados como "preservados" que não são mais usados

## Problemas Médios

### Code Quality

- [ ] **Função create_image_url muito longa** (48 linhas em main.py:19-67)
  - **Solução**: Quebrar em funções menores: `_validate_image_path()`, `_create_api_url()`

- [ ] **URLs hardcoded** no frontend
  - **Arquivos**: `App.vue:42-56`, `api.js:3`
  - **Solução**: Usar variáveis de ambiente (`.env`)

- [ ] **Logs excessivos** prejudicando performance
  - **Impacto**: Logs desnecessários em produção
  - **Solução**: Sistema de logging estruturado com níveis (DEBUG, INFO, ERROR)

- [ ] **Falta validação robusta** de entrada em endpoints
  - **Impacto**: Possíveis erros não tratados
  - **Solução**: Usar Pydantic models para request/response validation

## Problemas Baixos 

### Desenvolvimento

  - **Prioridade**: Testes para MangaScanner, endpoints críticos

- [ ] **Cache híbrido complexo demais** para o caso de uso atual
  - **Avaliação**: Verificar se simplicidade não seria melhor

### Frontend

- [ ] **Tratamento de erro inconsistente** em componentes Vue
  - **Solução**: Componente global de erro + store para estados de erro

- [ ] **Falta loading states** em operações longas
  - **Impacto**: UX ruim durante scans longos
  - **Solução**: Skeletons/spinners em componentes

## Melhorias de Segurança

- [ ] **Validação de caminhos** mais rigorosa
  - **Risco**: Path traversal attacks
  - **Solução**: Sanitização e validação mais rigorosa de paths

- [ ] **Rate limiting** nos endpoints de scan
  - **Risco**: Sobrecarga do servidor
  - **Solução**: Implementar rate limiting com slowapi

## Melhorias de Performance

- [ ] **Lazy loading** de thumbnails na biblioteca
  - **Impacto**: Carregamento inicial mais rápido

- [ ] **Paginação** na listagem de mangás
  - **Impacto**: Performance com bibliotecas grandes (1000+ mangás)

- [ ] **Compressão** de imagens thumbnails
  - **Impacto**: Menor uso de bandwidth

## Documentação

- [ ] **Documentação da API** usando OpenAPI/Swagger
  - **Status**: Parcialmente implementado, precisa melhorar

- [ ] **README.md** com instruções de setup e desenvolvimento
  - **Impacto**: Facilita onboarding de novos desenvolvedores

- [ ] **Comentários de código** em funções complexas
  - **Foco**: MangaScanner, funções de parsing

## Novas Funcinonalidades 

- [ ] **Continuar Leitura** 
  - **Status**: Parcialmente implementado, precisa melhorar

- [ ] **Cinfigurações gerais** 
  - **Status**: Parcialmente implementado, precisa melhorar