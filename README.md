# 📚 Ohara - Um leitor de mangá local

## Membros do Grupo
- Ítalo Dell Areti
- Raquel Gonçalves Rosa

## Descrição do Sistema
Aplicação web para leitura de mangás organizados localmente. O sistema escaneia uma estrutura de pastas, organiza os mangás por capítulos e oferece uma interface de leitura intuitiva.

## Como Executar o Projeto
**Pré-requisitos**

Python 3.13+ instalado

Node.js 18+ e npm instalados

Git para clonar o repositório

## Clonar o Repositório
~~~sh

git clone git@github.com:Dellareti/ohara.git

cd ohara
~~~

## Configurar o Backend

### Criar Ambiente Virtual
~~~sh
cd backend

python -m venv venv

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

Instalar Dependências

npm install
~~~

### Executar o Frontend
~~~sh
npm run dev
~~~
**Frontend disponível em: http://localhost:5173**
