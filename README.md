# Ohara - Leitor de Mangá Local

## Membros do Grupo
- Ítalo Dell Areti
- Raquel Gonçalves Rosa

## Descrição do Sistema
Sistema web para leitura de mangás organizados localmente. O Ohara escaneia estruturas de pastas contendo mangás, organiza automaticamente por capítulos e oferece uma interface intuitiva para leitura. O sistema permite configurar uma biblioteca local, visualizar thumbnails, navegar entre capítulos e acompanhar o progresso de leitura.

**Funcionalidades principais:**
- Escaneamento automático de bibliotecas de mangás
- Organização automática por mangás e capítulos
- Interface de leitura com navegação por páginas
- Sistema de cache para melhor performance
- API REST para integração

## Tecnologias Utilizadas

**Frontend:**
- Vue.js 3 - Framework JavaScript reativo
- Vue Router - Roteamento de páginas
- Pinia - Gerenciamento de estado
- Vite - Build tool e servidor de desenvolvimento
- Axios - Cliente HTTP para comunicação com API

**Backend:**
- FastAPI - Framework web moderno para Python
- Uvicorn - Servidor ASGI de alta performance
- Pydantic - Validação de dados e serialização
- Python 3.13+ - Linguagem de programação

**Outras tecnologias:**
- JSON - Armazenamento de dados e cache
- REST API - Arquitetura de comunicação
- CORS - Configuração de cross-origin

## Como Executar o Projeto
**Pré-requisitos**

Python 3.13+ instalado

Node.js 18+ e npm instalados

Git para clonar o repositório

## Clonar o Repositório
~~~sh
git clone git@github.com:Dellareti/ohara.git
~~~

~~~sh
cd ohara
~~~

## Configurar o Backend

### Criar Ambiente Virtual
~~~sh
cd backend
~~~

~~~sh
python -m venv venv
~~~

~~~sh
source venv/bin/activate
~~~

### Instalar Dependências
~~~sh
pip install -r requirements.txt
~~~

### Executar o Backend

~~~sh
python -m app.main
~~~

**Backend disponível em: http://localhost:8000**

**Documentação da API: http://localhost:8000/api/docs**

## Configurar o Frontend

### Abrir novo terminal e navegar para frontend
~~~sh
cd frontend
~~~

Instalar Dependências

~~~sh
npm install
~~~

### Executar o Frontend
~~~sh
npm run dev
~~~
**Frontend disponível em: http://localhost:5173**
