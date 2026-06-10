---
id: P3-TPL-02
title: Templates Bazar + Studio (navegação) — teste do contrato
phase: 3
etapa: "Etapa 8 — Templates no storefront"
area: TPL
status: todo
depends_on: [P3-TPL-01]
blocks: []
tests: [unit, e2e]
---

# P3-TPL-02 — Bazar + Studio (navegação) — teste do contrato

## Contexto
Com a arquitetura pronta (`P3-TPL-01`/Aurora), portar **Bazar** (home por **seções de categoria**) e **Studio** (home com **sidebar + grid**) prova a hipótese central do sistema de templates: **composição ≠ contrato** — 3 homes estruturalmente bem distintas consumindo os **mesmos dados e fluxo**. É o **teste** do contrato.

## Docs de referência
- [Guia dos templates](../../design/templates/README.md) + designs em `docs/design/templates/{bazar,studio}/`
- [`P3-TPL-01`](./P3-TPL-01-rich-templates-spec.md) (arquitetura/resolver/blocos)
- [`P3-SF-01`](./P3-SF-01-storefront-public-api.md) (API pública da home)

## Escopo (o que ENTRA)
- **Bazar (navegação):** `home` (hero/carrossel + **seções de categoria** com N produtos + "ver todos" + "Todas as categorias"), `category`, `product` — reusando resolver/blocos do `P3-TPL-01`.
- **Studio (navegação):** `home` (**sidebar** de categorias + filtros simples + grid denso), `category` (sidebar), `product` — reusando resolver/blocos.
- **Dado novo na API pública:** **produtos por categoria (N por categoria)** pra home do Bazar (as seções de categoria) — adição em `P3-SF-01`.
- **Nav overflow:** "Todas as categorias" (top N + menu/página) nos templates, pra não estourar com muitas categorias.

## Fora de escopo (o que NÃO entra)
- **Checkout + confirmação** dos 2 (funcionais): **Fase 4** (designs já existem).
- **Busca real** (a barra de busca da topbar do Studio é **placeholder** agora) → futuro.
- **Filtros avançados** (a sidebar do Studio tem filtros simples/visuais; faceted search real) → futuro.
- **Home 100% configurável** (lojista liga/desliga blocos) → futuro (V1 = defaults por template + ordem das categorias).

## Arquivos a criar/alterar
- `frontend-storefront/templates/bazar/{Home,Category,Product}.tsx` (criar).
- `frontend-storefront/templates/studio/{Home,Category,Product}.tsx` (criar) — incl. o layout com **sidebar** (drawer no mobile).
- `frontend-storefront/components/**` (alterar/criar) — bloco "seção de categoria", sidebar de catálogo.
- `backend/app/modules/storefront/{services,schemas,routes}.py` (alterar) — home expõe **produtos por categoria (N)** pras seções; + testes.
- `docs/10_storefront_and_layouts.md` (alterar) — reconciliar.

## Passos
1. Backend: home pública passa a expor `produtos por categoria (N)` (Bazar).
2. Portar Bazar `home`/`category`/`product`.
3. Portar Studio `home` (sidebar)/`category`/`product`.
4. Nav overflow ("Todas as categorias") nos 3 templates.
5. e2e: trocar template (aurora↔bazar↔studio) não quebra a navegação até "comprar".

## Testes
> Regra em [`_foundations-and-bottlenecks.md`](../_foundations-and-bottlenecks.md) §10.

- **Níveis:** unit (seção por categoria/seleção de N) + e2e (render + troca de template). **Quando:** durante.
- **Cobrir:**
  - unit — "produtos por categoria (N)" (categoria sem produtos → seção some/placeholder; respeita N).
  - e2e — Bazar e Studio renderizam home/categoria/produto; **trocar template mantém** a navegação card→produto→"comprar".

## Definition of Done
- [ ] Bazar + Studio renderizam `home`/`category`/`product`; **trocar template não quebra** o fluxo do cliente.
- [ ] Home do **Bazar** = seções de categoria (dado produtos-por-categoria); home do **Studio** = **sidebar + grid** (drawer no mobile).
- [ ] **Contrato validado:** os 3 templates consomem os **mesmos dados/fluxo** (a composição é o único diferente).
- [ ] **Nav overflow** ("Todas as categorias") nos 3.
- [ ] Gates verdes (storefront + backend + **e2e local**) + docs 10 reconciliado.
- [ ] **Modos de falha mapeados** (categoria sem produtos; muitas categorias no nav/home; sidebar no mobile; loja sem banners) → tratados **ou** Follow-up.
- [ ] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- Os 3 templates reusam o **resolver + blocos** do `P3-TPL-01`; aqui só entram as **árvores** do Bazar/Studio + o **dado** que faltava (produtos-por-categoria).
- "Produtos por categoria (N)" era follow-up de `P3-TPL-01`/`P3-SF-01` — **promovido pra escopo** aqui.

## Follow-ups
- [ ] **Checkout + confirmação (Bazar/Studio)** — *Quando:* **Fase 4**. → README.
- [ ] **Busca real** (topbar do Studio é placeholder) — *Quando:* pós-V1. → README.
- [ ] **Filtros avançados / faceted** (sidebar do Studio é simples) — *Quando:* pós-V1. → README.
- [ ] **Home 100% configurável (blocos)** — *Quando:* pós-V1 (hoje defaults por template + ordem das categorias). → README.
