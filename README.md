# Sintoniza

Aplicação de apoio à saúde mental com check-ins de humor e recomendações personalizadas, desenvolvida pelo grupo Lamport na disciplina de Métodos de Desenvolvimento de Software (UnB, 2026.2).

Arquitetura em camadas (monólito modular), conforme o Documento de Arquitetura:

| Diretório   | Conteúdo                                                                   |
| ----------- | -------------------------------------------------------------------------- |
| `backend/`  | API REST em FastAPI, PostgreSQL via SQLAlchemy, migrações com Alembic       |
| `frontend/` | Cliente web em React + TypeScript (Vite)                                   |

Organização do backend (`backend/app`):

- `api/` — rotas, schemas de validação, dependências de autenticação e tratamento de erros
- `application/` — casos de uso (cadastro, login, sessão)
- `domain/` — entidades e contratos de repositório, sem dependência de framework ou banco
- `infrastructure/` — modelos ORM, repositórios e conexão com o PostgreSQL
- `core/` — configuração e utilitários de segurança (hash de senha, JWT)

## Pré-requisitos

- Python 3.12 ou superior
- Node.js 22.22 ou superior
- Docker e Docker Compose (para o PostgreSQL)

## Configuração

### Banco de dados

```bash
docker compose up -d db
```

O PostgreSQL fica disponível em `localhost:5432` com usuário, senha e banco `sintoniza` (valores apenas para desenvolvimento; podem ser alterados por `POSTGRES_USER`, `POSTGRES_PASSWORD` e `POSTGRES_DB`).

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env
```

Edite `.env` e defina `SECRET_KEY` com um valor aleatório de pelo menos 32 caracteres:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

| Variável                      | Descrição                                                   |
| ----------------------------- | ----------------------------------------------------------- |
| `DATABASE_URL`                | URL de conexão do SQLAlchemy com o PostgreSQL               |
| `SECRET_KEY`                  | Chave de assinatura dos tokens JWT                          |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Validade do token de acesso (padrão: 60)                    |
| `CORS_ORIGINS`                | Origens autorizadas a chamar a API (lista JSON)             |
| `TERMS_VERSION`               | Versão dos termos registrada no consentimento do cadastro   |

Aplique as migrações e inicie a API:

```bash
alembic upgrade head
uvicorn app.main:app --reload
```

A API fica em `http://localhost:8000` e a documentação OpenAPI em `http://localhost:8000/docs`.

Alternativamente, banco e backend podem ser iniciados juntos com `docker compose up --build` (o contêiner aplica as migrações ao iniciar; o arquivo `backend/.env` precisa existir).

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

A aplicação fica em `http://localhost:5173`. `VITE_API_URL` define o endereço da API.

## Testes e verificações

Backend (requer o PostgreSQL em execução; o banco `sintoniza_test` é recriado e migrado a cada execução, e pode ser alterado por `TEST_DATABASE_URL`):

```bash
cd backend
pytest
ruff check . && ruff format --check .
```

Frontend:

```bash
cd frontend
npm test
npm run lint
npm run format:check
npm run build
```

O workflow `.github/workflows/tests.yml` executa essas verificações em pull requests e em pushes para `main` e `developer`.

## Autenticação

A API usa JWT enviado no cabeçalho `Authorization: Bearer <token>`. Senhas são armazenadas com Argon2id. No logout o identificador do token (`jti`) é revogado no servidor, invalidando-o antes da expiração. O frontend guarda o token em `sessionStorage`, que é descartado ao fechar a aba.

| Método | Rota                 | Autenticação | Descrição                                                     |
| ------ | -------------------- | ------------ | ------------------------------------------------------------- |
| GET    | `/api/health`        | Não          | Verifica a API e a conexão com o banco                        |
| POST   | `/api/auth/register` | Não          | Cadastra usuário (`email`, `password`, `accept_terms`)        |
| POST   | `/api/auth/login`    | Não          | Retorna `access_token` para `email` e `password`              |
| POST   | `/api/auth/logout`   | Sim          | Revoga o token atual                                          |
| GET    | `/api/users/me`      | Sim          | Retorna os dados do usuário autenticado                       |

Respostas de erro seguem o formato `{"detail": ...}`: `401` para credenciais ou token inválidos, `409` para e-mail já cadastrado, `422` para dados inválidos e `503` para falha de acesso ao banco.

Ao alterar o texto dos termos de uso, atualize `TERMS_VERSION` no backend e a constante correspondente em `frontend/src/pages/PrivacyPage.tsx`.

## Sobre o repositório

Template de Repositório para a matéria de Métodos de Desenvolvimento de Software lecionado pelo professor Ricardo Ajax.

A branch `main` deve ser usada exclusivamente para a versão de produção dos softwares da equipe.

O repositório conta com mais 3 branchs:

- docs: Usada para armazenar a documentação do projeto.
- developer: usada como um intermediário antes do código chegar realmente para produção. É o ambiente ideal para realizar os últimos testes antes das apresentações.
- gh-pages: Local dos arquivos estáticos de deploy da documentação. (Para deploy da documentação, consultar seu monitor)

A documentação é gerada com [MkDocs](https://www.mkdocs.org/) e o tema [Material](https://squidfunk.github.io/mkdocs-material/). Para que o deploy da documentação funcione, configure o GitHub Pages do repositório:

- Acesse as configurações do repositório;
- Procure a aba de "Pages"
- Em "Source" escolha a opção "Deploy from a branch";
- Em "Branch" escolha "gh-pages";
- Clique em salvar e pronto;
