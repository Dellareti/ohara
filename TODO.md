# TODO - Melhorias do Projeto Ohara

## Problemas RESOLVIDOS

- [x] **Import duplicado do MangaScanner** em main.py
- [x] **Endpoint duplicado** `/api/manga/{manga_id}
- [x] **Variável global** CURRENT_LIBRARY_PATH sem sincronização thread-safe
- [x] **Import circular** potencial em reader.py com `from app.main import CURRENT_LIBRARY_PATH`
- [x] **Código duplicado** entre endpoints POST e GET de scan-library 
- [x] **Métodos obsoletos no MangaScanner** 

## Problemas de Alta Urgência

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

## Problemas de Média Urgência

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

## Problemas de Baixa Urgência

### Desenvolvimento

  - **Prioridade**: Testes para MangaScanner, endpoints críticos

- [ ] **Cache híbrido complexo demais** para o caso de uso atual
  - **Avaliação**: Verificar se simplicidade não seria melhor
- [ ] **Resolver problema de conectividade** do npm run preview com backend
  - **Avaliação**: O problema é que a configuração de proxy do Vite apenas funciona no modo de desenvolvimento (npm run dev). No modo preview (npm run preview), o proxy não é aplicado, então o frontend tenta acessar diretamente http://localhost:8000 sem o proxy.

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

- [ ] **Configurações gerais** 
  - **Status**: Parcialmente implementado, precisa melhorar

- [ ] **Botão Navegar** 
  - **Status**: Parcialmente implementado, precisa melhorar