# Kriar — Frontend (platform admin)

The internal admin used by the Kriar team to operate the platform, built with
[Vite](https://vitejs.dev/), [React](https://react.dev/),
[TypeScript](https://www.typescriptlang.org/),
[TanStack Query + Router](https://tanstack.com/), Tailwind CSS and shadcn/Radix.
It talks to the backend through a generated OpenAPI client and is authenticated by
**global platform roles** (`platform.*`).

> Separate project from the merchant **dashboard** (`frontend-dashboard`) and the
> public **storefront** (`frontend-storefront`). Served at `admin.${DOMAIN}` (dev:
> `admin.localhost`); the shell shows a clear **internal-environment** banner.

## Workspace & tooling note

Part of the **Bun workspace** at the repo root: a **single `bun.lock` and a single
`node_modules` at the root** (deps are hoisted — there is no `frontend-admin/node_modules`).
Bun need not be installed globally; call the hoisted binaries `../node_modules/.bin/<tool>`.

Install from the **repo root** (regenerates `bun.lock` when a member's `package.json` changes):

```bash
npx bun@1.3.14 install
```

## Commands

From `./frontend-admin` (via the hoisted binaries when Bun isn't installed locally):

| Task | Command |
|---|---|
| Dev server | `../node_modules/.bin/vite` (port **5181**) |
| Type-check | `../node_modules/.bin/tsc -p tsconfig.build.json` |
| Production build | `../node_modules/.bin/vite build` |
| Lint / format | `../node_modules/.bin/biome check ./` (add `--write` to fix) |
| E2E (Playwright) | `../node_modules/.bin/playwright test` |
| Regenerate API client | `../node_modules/.bin/openapi-ts` |

## Routing & auth

- Served at **`admin.${DOMAIN}`** via Traefik (dev: `admin.localhost`, Traefik on
  `:8088`); the direct dev server runs on **`localhost:5181`**.
- Login uses the backend token flow; the shell guards access with
  **`GET /platform/me`** — a user with no `platform_roles` gets "Acesso negado".
- Operation screens (stores / users / plans / templates) land in `P4-ADMIN-02`/`03`.
