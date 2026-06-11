---
id: P3-SF-02
title: Storefront Next.js — host, "não encontrada", templates
phase: 3
etapa: "Etapa 1 — Projeto frontend-storefront"
area: SF
status: done
depends_on: [P3-FE-01, P3-SF-01]
blocks: []
tests: [e2e]
---

# P3-SF-02 — Render do storefront (Next.js)

## Contexto
A vitrine pública: o Next.js lê o `Host`, chama a API pública (`P3-SF-01`) e renderiza com o template ativo da loja. Só **imagem** (o editor 3D é Fase 7).

## Docs de referência
- [10 — Storefront & Layouts](../../concepts/10_storefront_and_layouts.md)
- [05 — Frontend Architecture](../../concepts/05_frontend_architecture.md)
- [13 — Performance, Cache & CDN](../../concepts/13_performance_cache_and_cdn.md)
- [21 — Design System](../../concepts/21_design_system_todo.md)

## Escopo (o que ENTRA)
- **Resolução por Host** (middleware/SSR) → `store_id` + dados públicos; **"loja não encontrada"** amigável (host inexistente/loja não publicada).
- **Templates** `classic` e `modern`: HomePage, CategoryPage, ProductPage (imagem) — o ativo vem do tema.
- **Cache público** (SSR/ISR sobre o cache do backend).
- **Botão flutuante de WhatsApp** quando a loja tiver número.

## Fora de escopo (o que NÃO entra)
- **ProductCustomizer / editor 3D** → Fase 7.
- **CartPage/CheckoutPage** completos → Fase 6 (placeholders aqui).
- Aplicar template (painel) → `P3-CONTENT-02`/`P3-FE-02`.

## Arquivos a criar/alterar
- `frontend-storefront/` — middleware de host, páginas (home/categoria/produto), os 2 templates, "não encontrada", botão WhatsApp.

## Passos
1. Middleware/SSR lê `Host` → chama API pública; 404 → página "não encontrada".
2. Home/Categoria/Produto consumindo a API pública; aplicar o template ativo.
3. ISR/SSR + revalidação; botão WhatsApp condicional.

## Testes
> Regra em [`_foundations-and-bottlenecks.md`](../_foundations-and-bottlenecks.md) §10.

- **Níveis:** e2e (Playwright) — ou follow-up se depender do stack completo, como na Fase 1.
- **Cobrir:** host resolve a loja; host/loja inválida → "não encontrada"; home/produto/categoria carregam; trocar template muda a vitrine.

## Definition of Done
- [x] Home/categoria/produto (imagem) renderizam com o template ativo; **validado por smoke real** (storefront SSR + backend + loja publicada).
- [x] Host inexistente/loja não publicada → **404 "Loja não encontrada"** (`notFound`).
- [x] **Modos de falha mapeados** (produto sem imagem → "sem imagem"; cache stale → `no-store` + invalidação do backend; API fora → Follow-up) → tratados/Follow-up.
- [x] Itens adiados varridos → Follow-ups + README.

## Notas / Reconciliações
- Carrinho/checkout = **Fase 6** (a página de produto é **informativa, sem CTA de compra**; o único WhatsApp da vitrine é o **botão flutuante** de contato → WhatsApp web); o `ProductCustomizer` entra na Fase 7.
- **SSR resolvido por Host:** o Next encaminha o host original como `X-Forwarded-Host`; **`P3-SF-01` foi estendida** — o dep lê `X-Forwarded-Host` (fallback `Host`) e `/products` ganhou `?category=` (para a CategoryPage).
- **Cache:** fetch `no-store` (não cacheia no Next — a chave por URL vazaria entre lojas); o cache por-loja é do backend (Redis, doc 13). Trocar o template invalida `store:{id}:home` (`P3-CONTENT-02`) → a vitrine reflete.
- **Templates:** `classic` (headline + grid simples) vs `modern` (hero com banner + cards maiores) + cores do tema; trocar o template ativo muda a home.
- **Imagens:** `<img>` no V1 (regra `noImgElement` desligada no biome do storefront). `NEXT_PUBLIC_API_URL` do container dev = `http://backend:8000` (SSR alcança o backend interno).
- **Verificação:** `next build` + smoke (home/produto renderizam, host desconhecido → 404), com cleanup.

## Follow-ups
- [ ] **Produto: ação de compra (carrinho)** (`P3-SF-02` → Fase 6): a página de produto é **informativa** no V1 (sem botão de compra); adicionar o **carrinho** na Fase 6. O WhatsApp da vitrine é só o **botão flutuante** de contato (não há "comprar pelo WhatsApp").
- [ ] **e2e Playwright do storefront** (`P3-SF-02`): a suíte é só painel (:5180); o render foi validado por smoke manual. Automatizar host→loja / 404 / home-produto-categoria / troca de template (a task permite e2e como follow-up).
- [ ] **API fora → erro amigável** (`P3-SF-02`): `apiGet` joga em `!ok` (não-404) → 500 genérico; adicionar `app/error.tsx`.
- [ ] **next/image** (`P3-SF-02`): trocar `<img>` por `next/image` + `remotePatterns` do CDN (perf/LCP).
- [ ] **API URL server-only** (`P3-SF-02`): a SSR usa `NEXT_PUBLIC_API_URL` (exposto ao client); separar um `INTERNAL_API_URL` server-only.
- [ ] **Rebuild + smoke do Traefik** (`P3-SF-02`, infra): `docker compose up -d --build backend frontend-storefront` e abrir a vitrine em `{loja}.localhost` via Traefik.
