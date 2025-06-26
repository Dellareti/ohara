# TODO - Melhorias do Projeto Ohara

## Resolvidas

- [x] **Botão Navegar** 
  - **Status**: Ao implementar utilizando o system file do SO trouxe muitos problemas de navegação e o browser, por medidads de segurança, impede o acesso as pastas. Portanto, preferimos manter a seleção do path como método tradicional para biblioteca.

- [x] **URLs hardcoded** no frontend
  - **Solução**: Implementado usando variáveis de ambiente (`.env`)
  - **Status**: **IMPLEMENTADO**

- [x] **Refatorar console.log para sistema de logging adequado**
  - **Solução**: Removidos todos os console.log desnecessários
  - **Status**: **IMPLEMENTADO**

- [x] **Função create_image_url muito longa** (análise realizada)
  - **Decisão**: **Não modificar** 

- [x] **Tratamento de erro inconsistente** em componentes Vue
  - **Solução**: **IMPLEMENTADO**

- [x] **Continuar Leitura** 
  - **Status**: **IMPLEMENTADO**
  
- [x] **Documentação da API** usando OpenAPI/Swagger
  - **Solução**: Adicionadas tags organizacionais, descrições detalhadas, exemplos e metadados completos
  - **Status**: **IMPLEMENTADO**

- [x] **README.md** com instruções de setup e desenvolvimento
  - **Solução**: Expandido com arquitetura, endpoints, troubleshooting, performance e guia de contribuição
  - **Status**: **IMPLEMENTADO**

- [x] **Comentários de código** em funções complexas
  - **Solução**: Docstrings detalhadas na classe MangaScanner e métodos principais de parsing
  - **Status**: **IMPLEMENTADO**

  - [x] **Configurações gerais** 
  - **Status**: **IMPLEMENTADO**

  - [x] **Mover a pasta testes** 
  - **Status**: **IMPLEMENTADO**

- [x] **Arquivo main.py muito grande** 
  - **Status**: **IMPLEMENTADO**

- [x] **Classe MangaScanner complexa demais** 
  - **Status**: **IMPLEMENTADO**

- [x] **Cache híbrido complexo demais** 
- **Solução**: Implimentação do SimpleCache
  - **Status**: **IMPLEMENTADO**

### Desenvolvimento

  - **Prioridade**: Testes para MangaScanner, endpoints críticos