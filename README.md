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

- Docker e Docker Compose (o suficiente para subir o ambiente de demonstração)
- Python 3.12 ou superior e Node.js 22.22 ou superior (para desenvolver e rodar os testes fora do Docker)

## Ambiente de demonstração

O sistema completo roda com Docker Compose em três contêineres (Arquitetura, seção 2.6):

| Serviço | Conteúdo                                                                   |
| ------- | -------------------------------------------------------------------------- |
| `web`   | Nginx com o build do React; encaminha `/api` para a API                    |
| `api`   | FastAPI com Uvicorn (Python 3.12); aplica as migrações ao iniciar          |
| `db`    | PostgreSQL 16 com volume persistente                                       |

**1. Crie o arquivo `.env` na raiz do repositório** (ele não é versionado):

```bash
cp .env.example .env              # Windows (PowerShell): Copy-Item .env.example .env
```

Abra o `.env` e preencha `SECRET_KEY` com um valor aleatório de pelo menos 32 caracteres. Para gerar um:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
# sem Python instalado:
docker run --rm python:3.12-slim python -c "import secrets; print(secrets.token_urlsafe(48))"
```

**2. Suba o ambiente:**

```bash
docker compose up --build --detach --wait
```

O comando termina quando os três serviços estão prontos. O site fica em `http://localhost:8080` (a porta pode ser trocada por `WEB_PORT` no `.env`).

**3. Rode o seed:**

```bash
docker compose exec api python -m app.seed_demo
```

O comando cria os usuários fictícios abaixo, todos com a senha `sintoniza-demo`. Pode ser executado de novo sem duplicar dados.

| E-mail                  | Situação                                                      |
| ----------------------- | ------------------------------------------------------------- |
| `demo@example.com`      | Sem check-ins                                                 |
| `historico@example.com` | Com check-ins nos 5 dias anteriores; o de hoje fica em aberto |

O catálogo de materiais oficiais será carregado pelo comando seed da issue #19, que ainda não foi integrado. Quando for, este passo passa a incluir esse comando.

**Comandos úteis:**

```bash
docker compose logs -f api        # acompanha os logs da API
docker compose down               # para os contêineres e mantém os dados
docker compose down --volumes     # para os contêineres e apaga o banco
```

Depois de atualizar a branch, rode de novo o `docker compose up --build --detach --wait` para reconstruir as imagens. A partir desta versão, o banco usa PostgreSQL 16 em um volume novo (`sintoniza_db-data`). Se um contêiner antigo do projeto ainda estiver usando a porta 5432, pare-o com `docker compose -p 20262-t03-lamport down`.

## Desenvolvimento local

### Banco de dados

```bash
docker compose up -d db
```

O PostgreSQL fica disponível em `localhost:5432` com usuário, senha e banco `sintoniza` (valores apenas para desenvolvimento; podem ser alterados por `POSTGRES_USER`, `POSTGRES_PASSWORD` e `POSTGRES_DB`). O `.env` da raiz precisa existir mesmo para subir só o banco (veja o passo 1 do ambiente de demonstração).

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
| `LOGIN_MAX_ATTEMPTS`          | Falhas de login permitidas por e-mail na janela (padrão: 5) |
| `LOGIN_LOCKOUT_MINUTES`       | Duração da janela de bloqueio, em minutos (padrão: 15)      |

Aplique as migrações e inicie a API:

```bash
alembic upgrade head
uvicorn app.main:app --reload
```

A API fica em `http://localhost:8000` e a documentação OpenAPI em `http://localhost:8000/docs`. Para criar os usuários fictícios nesse banco local, rode `python -m app.seed_demo`.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

A aplicação fica em `http://localhost:5173`. `VITE_API_URL` define o endereço da API.

## Testes e verificações

Backend (requer o PostgreSQL em execução com `docker compose up -d db`; o banco `sintoniza_test` é recriado e migrado a cada execução, e pode ser alterado por `TEST_DATABASE_URL`):

```bash
cd backend
pytest
ruff check . && ruff format --check .
```

Para conferir se as migrações sobem e descem em um banco vazio, como a CI faz, use um banco descartável:

```bash
cd backend
docker compose exec db createdb -U sintoniza sintoniza_mig
export DATABASE_URL=postgresql+psycopg://sintoniza:sintoniza@localhost:5432/sintoniza_mig
alembic upgrade head && alembic downgrade base && alembic upgrade head
unset DATABASE_URL
docker compose exec db dropdb -U sintoniza sintoniza_mig
```

Frontend:

```bash
cd frontend
npm test
npm run lint
npm run format:check
npm run build
```

## Integração contínua

O workflow [`.github/workflows/tests.yml`](.github/workflows/tests.yml) roda em todo pull request e em pushes para `main` e `developer`, com três jobs:

| Job        | O que verifica                                                                                                          |
| ---------- | ----------------------------------------------------------------------------------------------------------------------- |
| `backend`  | ruff; migrações Alembic em banco vazio (upgrade, downgrade e upgrade); pytest com PostgreSQL 16 de teste                |
| `frontend` | eslint, prettier, testes (vitest) e build                                                                               |
| `demo`     | sobe `web`, `api` e `db` com Docker Compose seguindo este README, roda o seed e acessa o site e a API pelo Nginx        |

As branches `main` e `developer` são protegidas: o merge só é liberado quando os três jobs passam. Para configurar a proteção (é preciso ser administrador do repositório), vá em **Settings → Branches → Add branch protection rule** e, para cada uma das branches:

1. em **Branch name pattern**, informe `main` (depois repita para `developer`);
2. marque **Require a pull request before merging** e, nela, **Require approvals** com 1 aprovação;
3. marque **Require status checks to pass before merging** e **Require branches to be up to date before merging**;
4. em **Status checks that are required**, adicione `backend`, `frontend` e `demo` (os nomes só aparecem depois que o workflow rodou uma vez);
5. marque **Do not allow bypassing the above settings** e salve.

## Autenticação

A API usa JWT enviado no cabeçalho `Authorization: Bearer <token>`. Senhas são armazenadas com Argon2id. No logout o identificador do token (`jti`) é revogado no servidor, invalidando-o antes da expiração. O frontend guarda o token em `sessionStorage`, que é descartado ao fechar a aba.

| Método | Rota                 | Autenticação | Descrição                                                     |
| ------ | -------------------- | ------------ | ------------------------------------------------------------- |
| GET    | `/api/health`        | Não          | Verifica a API e a conexão com o banco                        |
| POST   | `/api/auth/cadastro` | Não          | Cadastra usuário (`email`, `senha`, `aceite_termos`, `maior_de_idade`) |
| POST   | `/api/auth/login`    | Não          | Retorna `access_token` para `email` e `senha`                 |
| POST   | `/api/auth/logout`   | Sim          | Revoga o token atual                                          |
| GET    | `/api/me`            | Sim          | Retorna os dados do usuário autenticado                       |
| GET    | `/api/terms`         | Não          | Retorna a versão vigente dos termos de uso                    |

Respostas de erro seguem o formato `{"detail": ...}`: `401` para credenciais ou token inválidos, `409` para e-mail já cadastrado, `422` para dados inválidos, `429` para excesso de tentativas de login e `503` para falha de acesso ao banco.

Depois de `LOGIN_MAX_ATTEMPTS` falhas de login para o mesmo e-mail dentro de `LOGIN_LOCKOUT_MINUTES`, novas tentativas recebem `429` com o cabeçalho `Retry-After`. E-mails não cadastrados são bloqueados da mesma forma, para não revelar quais contas existem. As tentativas são registradas pelo hash do e-mail, e um login bem-sucedido zera a contagem.

Ao alterar o texto dos termos de uso, atualize `TERMS_VERSION` no backend. A página de privacidade do frontend lê a versão de `GET /api/terms`.

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
