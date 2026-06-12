# frontend-storefront

Vitrine pública (Next.js, App Router) das lojas Kriar, resolvida por **Host**
(`{loja}.${DOMAIN}`). O painel do lojista é o [`frontend-dashboard`](../frontend-dashboard/README.md).

Faz parte do **workspace bun** (lockfile único na raiz). bun não está instalado no
host → use os binários da raiz (`../node_modules/.bin/next`, `.../tsc`, `.../biome`).

## Rodar (dev)

```bash
# da raiz do repo, após `bun install`:
bun run --filter frontend-storefront dev   # http://localhost:3000
```

Aponte para a API pública com `NEXT_PUBLIC_API_URL` (ex.: `http://localhost:8800`).

## Escopo atual

`P3-FE-01` entrega só o **scaffold + placeholder**. A resolução por Host e os
templates (home/categoria/produto) entram em `P3-SF-02`; a API pública em `P3-SF-01`.
