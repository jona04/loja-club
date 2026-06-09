# Loja Club — Frontend (merchant dashboard)

The merchant panel, built with [Vite](https://vitejs.dev/),
[React](https://react.dev/), [TypeScript](https://www.typescriptlang.org/),
[TanStack Query + Router + Table](https://tanstack.com/), Tailwind CSS and
shadcn/Radix. It talks to the backend through a generated OpenAPI client.

> This is the **dashboard**. The public storefront and the platform admin are
> separate frontends (planned).

## Workspace & tooling note

This package is part of a **Bun workspace** defined at the repo root:

- there is a **single lockfile** (`bun.lock`) and a **single `node_modules` at the
  repo root** (dependencies are hoisted) — there is no `frontend/node_modules`.
- **Bun is not required to be installed globally.** You can either use
  `npx bun@1.3.14 …` or call the tool binaries directly from the hoisted folder:
  `../node_modules/.bin/<tool>`.

Install dependencies from the **repo root**:

```bash
npx bun@1.3.14 install      # regenerates bun.lock when package.json changes
```

## Commands

From `./frontend`. Two equivalent ways — via Bun, or via the hoisted binaries
(handy when Bun isn't installed locally):

| Task | With Bun | Without Bun (hoisted binaries) |
|---|---|---|
| Dev server (hot reload) | `bun run dev` | `../node_modules/.bin/vite` |
| Type-check (build config) | — | `../node_modules/.bin/tsc -p tsconfig.build.json` |
| Production build | `bun run build` | `../node_modules/.bin/vite build` |
| Lint / format | `bun run lint` | `../node_modules/.bin/biome check src` (add `--write` to fix) |
| Unit tests (Vitest) | `bun run test:unit` | `CI=true ../node_modules/.bin/vitest run` |
| E2E (Playwright) | `bun run test` | `../node_modules/.bin/playwright test` |
| Regenerate API client | `bun run generate-client` | `../node_modules/.bin/openapi-ts` |

The Vite dev server runs on http://localhost:5180 (set in `vite.config.ts`). Point it at a
running API with `VITE_API_URL` (e.g. `http://localhost:8800`, or
`http://api.localhost:8088`) in `frontend/.env`. When you run the full
Docker stack instead, the dashboard is served at http://localhost:5180 /
http://app.localhost:8088 (see the [root README](../README.md)).

## Generated API client

The client in `src/client/` is generated from the backend's OpenAPI schema
(`@hey-api/openapi-ts`). Regenerate it whenever the backend API changes:

```bash
# with the backend running, then from ./frontend:
../node_modules/.bin/openapi-ts        # or: bun run generate-client
```

Commit the regenerated client.

## End-to-end tests (Playwright)

E2E needs the Docker stack up:

```bash
docker compose up -d --wait backend
../node_modules/.bin/playwright test           # or: bun run test
../node_modules/.bin/playwright test --ui      # interactive
docker compose down -v                         # tear down + wipe test data
```

## Code structure

```text
src/
  client/       generated OpenAPI client (do not edit by hand)
  components/    UI components
  hooks/         custom hooks (e.g. useActiveStore)
  lib/           helpers (menu, active store, …)
  routes/        TanStack Router routes (pages)
tests/          unit (Vitest)
```
