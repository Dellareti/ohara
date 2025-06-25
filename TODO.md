# TODO - Melhorias do Projeto Ohara

## Resolvidas

- [x] **Botão Navegar** 
  - **Status**: Ao implementar utilizando o system file do SO trouxe muitos problemas de navegação e o browser, por medidads de segurança, impede o acesso as pastas. Portanto, preferimos manter a seleção do path como método tradicional para biblioteca.

- [x] **URLs hardcoded** no frontend
  - **Arquivos**: `App.vue:44`, `api.js:3`
  - **Solução**: Implementado usando variáveis de ambiente (`.env`)
  - **Status**: Criados arquivos `.env` e `.env.example` com `VITE_API_BASE_URL`

- [x] **Refatorar console.log para sistema de logging adequado**
  - **Solução**: Removidos todos os console.log desnecessários
  - **Status**: 35 console.log convertidos em comentários 

- [x] **Função create_image_url muito longa** (análise realizada)
  - **Decisão**: **Não modificar** 


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



## Problemas de Baixa Urgência

### Desenvolvimento

  - **Prioridade**: Testes para MangaScanner, endpoints críticos

- [ ] **Cache híbrido complexo demais** para o caso de uso atual
  - **Avaliação**: Verificar se simplicidade não seria melhor

### Frontend

- [ ] **Tratamento de erro inconsistente** em componentes Vue
  - **Solução**: Componente global de erro + store para estados de erro

## Documentação

- [ ] **Documentação da API** usando OpenAPI/Swagger
  - **Status**: Parcialmente implementado, precisa melhorar

- [ ] **README.md** com instruções de setup e desenvolvimento
  - **Impacto**: Facilita onboarding de novos desenvolvedores

- [ ] **Comentários de código** em funções complexas
  - **Foco**: MangaScanner, funções de parsing

- [ ] **Mover a pasta testes** para a pasta raiz e tira-lá da pasta app, pois o padrão python é testes na pasta raiz

## Novas Funcinonalidades 

- [ ] **Continuar Leitura** 
  - **Status**: Parcialmente implementado, precisa melhorar

- [ ] **Configurações gerais** 
  - **Status**: Parcialmente implementado, precisa melhorar

