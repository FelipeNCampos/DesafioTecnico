# Estoque X API

API Flask para controle de estoque por enderecos, com JWT por perfil, SQL Server e Swagger.

## Como Rodar

1. Copie `.env.example` para `.env` e ajuste os segredos.
2. Suba SQL Server e API:

```bash
docker compose up --build -d
```

3. Acesse:

- API: `http://localhost:8000`
- Swagger (documentação): `http://localhost:8000/docs`

Para rodar sem Docker, instale as dependencias e defina `DATABASE_URL`. Sem essa variavel, a aplicacao usa SQLite local apenas para desenvolvimento rapido.

```bash
python -m venv venv 
.\venv\Scripts\activate
pip install -r requirements.txt
python seed.py
python run.py # (dados para teste)
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
