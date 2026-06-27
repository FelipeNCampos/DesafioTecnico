# Estoque X API

API Flask para controle de estoque por enderecos, com JWT por perfil, SQL Server e Swagger.

## Como Rodar

1. Copie `.env.example` para `.env` e ajuste os segredos.
2. Suba SQL Server e API:

```bash
docker compose up --build
```

3. Rode a carga inicial:

```bash
docker compose exec api python seed.py
```

4. Acesse:

- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs/swagger`

Para rodar sem Docker, instale as dependencias e defina `DATABASE_URL`. Sem essa variavel, a aplicacao usa SQLite local apenas para desenvolvimento rapido.

```bash
pip install -r requirements.txt
python seed.py
python run.py
```

## Autenticacao

Rotas publicas:

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/token`

Use o token retornado no header:

```http
Authorization: Bearer <token>
```

Perfis:

- `gerente`: administra produtos, enderecos e relatorios.
- `operador`: consulta produtos/enderecos e registra/consulta contagens.

Usuarios criados pelo seed:

- `gerente@example.com` / `gerente123`
- `operador@example.com` / `operador123`

## Endpoints Principais

- `GET /api/produtos`, `POST /api/produtos`, `GET /api/produtos/sku/<codigo>`, `PUT/DELETE /api/produtos/<id>`
- `GET /api/enderecos`, `POST /api/enderecos`, `GET /api/enderecos/codigo/<codigo>`, `PUT/DELETE /api/enderecos/<id>`
- `POST /api/contagens`
- `GET /api/contagens/saldo/<codigo_endereco>`
- `GET /api/contagens/historico/<sku>?data_inicio=...&data_fim=...`
- `GET /api/relatorios/divergencia/<codigo_endereco>`

O relatorio de divergencia usa SQL puro em `sql/divergencia.sql`, comparando as duas ultimas contagens por produto no endereco.
