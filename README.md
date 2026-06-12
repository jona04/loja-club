# Kriar

Multi-tenant ecommerce **SaaS** with an initial focus on promotional products,
print shops and visual communication. A merchant signs up, creates a store,
adds products, and sells — without standing up any infrastructure of their own.

> **Status:** early development. Phases 0–1 (foundation + multi-tenancy + merchant
> panel) are done; Phase 2 (catalog + media) is in progress. See the
> [roadmap](./docs/concepts/17_v1_roadmap.md) and the [backlog](./docs/backlog/README.md).

## Architecture at a glance

- **Backend** — a **modular monolith** in FastAPI (`backend/app/modules/<domain>/`),
  SQLModel + Alembic over **PostgreSQL**, **Redis** for cache/locks/queue.
- **Worker** — async background jobs (image thumbnails, emails, …) via **arq**
  on Redis. Email is always dispatched through the worker (never inline).
- **Dashboard** — the merchant panel: **React + Vite + TanStack** (`frontend/`).
- **Storefront / Admin** — separate frontends (planned).
- **Object storage** — **AWS S3 + CloudFront** (real, even from local dev — no MinIO).
- **Edge** — **Traefik** routes `api.`, `app.`, `admin.` and the wildcard `*.` hosts.

Multi-tenancy is a shared database scoped by `store_id` on every commercial table.

## Repository layout

```text
backend/        FastAPI app (app/modules/*, alembic, tests, scripts)
frontend/       Merchant dashboard (React/Vite); part of the bun workspace
docs/           Concept docs (01–24) + backlog (the actionable, phased to-do)
compose.yml     Docker Compose stack (+ compose.override.yml for local dev)
.env            Local config — gitignored; copy from .env.example
```

## Quickstart (Docker Compose)

Requirements: **Docker**, [**uv**](https://docs.astral.sh/uv/) (backend), and
**Node/Bun** (frontend).

```bash
cp .env.example .env          # then edit secrets (see "Configuration" below)
docker compose up -d          # build + start the whole stack
```

### Local URLs

| Service | URL |
|---|---|
| Dashboard (merchant panel) | http://localhost:5180 · http://app.localhost:8088 |
| API | http://localhost:8800 · http://api.localhost:8088 |
| API docs (Swagger UI) | http://localhost:8800/docs |
| Adminer (database UI) | http://localhost:8810 |
| Mailcatcher (captured emails) | http://localhost:1090 |
| Traefik dashboard | http://localhost:8091 |

> `*.localhost` resolves to `127.0.0.1` in browsers automatically. For CLI
> tools, add the hosts to `/etc/hosts`.

Sign in with the superuser from your `.env` (`FIRST_SUPERUSER` /
`FIRST_SUPERUSER_PASSWORD`), then create a store.

## Command cheat sheet

Details live in [`backend/README.md`](./backend/README.md) and
[`frontend/README.md`](./frontend/README.md). The essentials:

```bash
# Infra only (for running the backend/tests on the host)
docker compose up -d --wait db redis

# --- Backend (run from ./backend) ---
uv sync
uv run bash scripts/lint.sh                                   # mypy + ty + ruff + format
POSTGRES_PORT=5442 REDIS_PORT=6399 uv run coverage run -m pytest tests/
POSTGRES_PORT=5442 REDIS_PORT=6399 uv run coverage report --fail-under=90
POSTGRES_PORT=5442 REDIS_PORT=6399 uv run alembic upgrade head
POSTGRES_PORT=5442 REDIS_PORT=6399 uv run alembic check       # diff models ↔ DB

# --- Frontend (run from ./frontend; bun is not installed locally) ---
../node_modules/.bin/vite                 # dev server (hot reload)
../node_modules/.bin/vitest run           # unit tests
../node_modules/.bin/biome check src      # lint/format
../node_modules/.bin/tsc -p tsconfig.build.json   # type-check

# --- Worker / queue ---
docker compose up -d --build worker       # rebuild after adding/changing a task
docker compose exec -T redis redis-cli GET arq:queue:health-check
```

> The host ports are non-standard on purpose (db `5442`, redis `6399`, backend
> `8800`, dashboard `5180`) so the stack never clashes with other local services.
> Host-run tests therefore need `POSTGRES_PORT=5442 REDIS_PORT=6399`.

## Configuration & secrets

- Config lives in `.env` (**gitignored**). Start from `.env.example` and change at
  least `SECRET_KEY`, `POSTGRES_PASSWORD`, `FIRST_SUPERUSER_PASSWORD`.
- **Never commit `.env`** or AWS keys (this repo is public). In deploy, secrets
  come from GitHub Actions Secrets / AWS SSM, and AWS uses an IAM role.
- Object storage (S3/CloudFront) is optional locally: with empty AWS vars the
  `moto`-mocked tests still run; fill them to exercise the real smoke tests.
  See [`backend/README.md`](./backend/README.md#object-storage-aws).

## Documentation

- **Docs index (concepts 01–24):** [`docs/README.md`](./docs/README.md)
- **Backlog (phases + tasks):** [`docs/backlog/README.md`](./docs/backlog/README.md)
- **Invariants & cross-phase decisions:** [`docs/backlog/_foundations-and-bottlenecks.md`](./docs/backlog/_foundations-and-bottlenecks.md)
- **Backend dev guide:** [`backend/README.md`](./backend/README.md)
- **Frontend dev guide:** [`frontend/README.md`](./frontend/README.md)
- **Local environment / Docker Compose:** [`development.md`](./development.md)
- **Deployment:** [`deployment.md`](./deployment.md)
- **Code conventions (for devs and AI):** [`CLAUDE.md`](./CLAUDE.md)
- **Security policy:** [`SECURITY.md`](./SECURITY.md) · **Contributing:** [`CONTRIBUTING.md`](./CONTRIBUTING.md)

> Concept docs (`docs/`) are written in Portuguese; code, identifiers and these
> README/run guides are in English.

## License

MIT — see [`LICENSE`](./LICENSE).
