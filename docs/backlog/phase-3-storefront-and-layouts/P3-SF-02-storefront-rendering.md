---
id: P3-SF-02
title: Storefront Next.js — host, "não encontrada", templates
phase: 3
etapa: "Etapa 8 — Templates no storefront"
area: SF
status: todo
depends_on: [P3-FE-01, P3-SF-01]
blocks: []
tests: [e2e]
---

# P3-SF-02 — Render do storefront (Next.js)

## Contexto
A vitrine pública: o Next.js lê o `Host`, chama a API pública (`P3-SF-01`) e renderiza com o template ativo da loja. Só **imagem** (o editor 3D é Fase 5).

## Docs de referência
- [10 — Storefront & Layouts](../../10_storefront_and_layouts.md)
- [05 — Frontend Architecture](../../05_frontend_architecture.md)
- [13 — Performance, Cache & CDN](../../13_performance_cache_and_cdn.md)
- [21 — Design System](../../21_design_system_todo.md)

## Escopo (o que ENTRA)
- **Resolução por Host** (middleware/SSR) → `store_id` + dados públicos; **"loja não encontrada"** amigável (host inexistente/loja não publicada).
- **Templates** `classic` e `modern`: HomePage, CategoryPage, ProductPage (imagem) — o ativo vem do tema.
- **Cache público** (SSR/ISR sobre o cache do backend).
- **Botão flutuante de WhatsApp** quando a loja tiver número.

## Fora de escopo (o que NÃO entra)
- **ProductCustomizer / editor 3D** → Fase 5.
- **CartPage/CheckoutPage** completos → Fase 4 (placeholders aqui).
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
- [ ] Vitrine abre em `nomedaloja.${DOMAIN}` com o template ativo; home/categoria/produto (imagem) renderizam.
- [ ] Host inexistente/loja não publicada → "loja não encontrada".
- [ ] **Modos de falha mapeados** (API fora, produto sem imagem, cache stale após troca de template) → tratados ou Follow-up.
- [ ] Itens adiados varridos → Follow-ups + README, ou "nenhum".

## Notas / Reconciliações
- Carrinho/checkout ficam como **placeholder** até a Fase 4; o `ProductCustomizer` entra na Fase 5.

## Follow-ups
- (preencher ao executar)
