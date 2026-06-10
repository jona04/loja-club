---
id: P3-TPL-02
title: Templates Bazar + Studio (navegação) — teste do contrato
phase: 3
etapa: "Etapa 8 — Templates no storefront"
area: TPL
status: done
depends_on: [P3-TPL-01]
blocks: []
tests: [unit, e2e]
---

# P3-TPL-02 — Bazar + Studio (navegação) — teste do contrato

## Contexto
Com a arquitetura pronta (`P3-TPL-01`/Aurora), portar **Bazar** (home por **seções de categoria**) e **Studio** (home com **sidebar + grid**) prova a hipótese central do sistema de templates: **composição ≠ contrato** — 3 homes estruturalmente bem distintas consumindo os **mesmos dados e fluxo**. É o **teste** do contrato.

## Abordagem (port FIEL ao template, como o Aurora em `P3-TPL-01`)
- **Copiar a estrutura do HTML** (`docs/design/templates/{bazar,studio}/`) pra componentes React — **não adaptar/simplificar**. FontAwesome (já no `layout.tsx`), animações/hover idênticos; real onde há dado + **lorem onde não há**.
- **Cada template tem o seu Shell** (header/footer/cart drawer) + ProductCard + **paleta própria** (`@theme` no `globals.css` — Bazar/Studio têm cores diferentes do Aurora).
- **Reutiliza o compartilhado:** carrinho client (`lib/cart.tsx`), `lib/format.ts`, o **resolver** e as páginas `/checkout`·`/pedido`·`/conta`·`/institucional/*`.
- **"Adicionar ao carrinho" funcionando** + **cada clique leva a uma página** (lorem onde precisar).

## Docs de referência
- [Guia dos templates](../../design/templates/README.md) + designs em `docs/design/templates/{bazar,studio}/`
- [`P3-TPL-01`](./P3-TPL-01-template-architecture-aurora.md) (arquitetura/resolver/blocos)
- [`P3-SF-01`](./P3-SF-01-storefront-public-api.md) (API pública da home)

## Escopo (o que ENTRA)
- **Bazar — port fiel:** Shell + ProductCard + paleta próprios; `home` (hero + **seções de categoria** com N produtos + "ver todos" + "Todas as categorias"), `category`, `product`.
- **Studio — port fiel:** Shell com **sidebar** (categorias + filtros, drawer no mobile); `home` (sidebar + grid denso), `category`, `product`.
- **Páginas avulsas viram template-aware:** `/checkout`·`/pedido`·`/conta`·`/institucional/*` passam a resolver o **Shell do template ativo** (hoje usam o `AuroraShell` fixo) — o `Template` ganha `Shell` no contrato.
- **Dado novo na API pública:** **produtos por categoria (N)** pra home do Bazar — adição em `P3-SF-01`.
- **Nav overflow:** "Todas as categorias" (top N + menu/página) nos 3 templates.

## Fora de escopo (o que NÃO entra)
- **Checkout + confirmação** dos 2 (funcionais): **Fase 6** (designs já existem).
- **Busca real** (a barra de busca da topbar do Studio é **placeholder** agora) → futuro.
- **Filtros avançados** (a sidebar do Studio tem filtros simples/visuais; faceted search real) → futuro.
- **Home 100% configurável** (lojista liga/desliga blocos) → futuro (V1 = defaults por template + ordem das categorias).

## Arquivos a criar/alterar
- `frontend-storefront/templates/bazar/{Shell,Home,Category,Product,…Card}.tsx` (criar) — árvore + Shell + card próprios.
- `frontend-storefront/templates/studio/{Shell,Home,Category,Product,…}.tsx` (criar) — incl. a **sidebar** (drawer no mobile).
- `frontend-storefront/app/globals.css` (alterar) — paletas `@theme` do Bazar/Studio.
- `frontend-storefront/lib/{templates,template-types}.ts` (alterar) — expor `Shell` no contrato `Template`.
- `frontend-storefront/app/{checkout,pedido,conta,institucional/[slug]}/page.tsx` (alterar) — usar o **Shell do template ativo** (resolver), não o `AuroraShell` fixo.
- `backend/app/modules/storefront/{services,schemas,routes}.py` (alterar) — home expõe **produtos por categoria (N)** + testes.
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
- [x] Bazar + Studio renderizam `home`/`category`/`product`; **trocar template não quebra** o fluxo (resolver `{aurora, bazar, studio}`; **smoke real** de cada).
- [x] **Port fiel** ao template (FontAwesome, hover/animações, paleta própria); **"Adicionar ao carrinho" funciona** (carrinho compartilhado); **cada clique leva a uma página**; as páginas avulsas (`/checkout`·`/account`·`/order-confirmation`·`/pages/*`) usam o **Shell do template ativo** (`Template.Shell`).
- [x] Home do **Bazar** = seções de categoria (`StorefrontHome.category_sections`); home do **Studio** = **sidebar + grid** (sidebar desktop; drawer no mobile = follow-up).
- [x] **Contrato VALIDADO:** os 3 (Aurora destaques / Bazar seções / Studio sidebar) consomem os **mesmos dados/fluxo** — a hipótese "composição ≠ contrato" se confirma.
- [x] **Nav overflow** ("Todas as categorias") nos 3.
- [x] Gates verdes (storefront build/biome + backend lint/cobertura **94%** + **smoke real** dos 3); docs 10 reconciliado.
- [x] **Modos de falha mapeados:** categoria sem produtos → seção pulada; loja sem banners → fallback gradiente/cor; muitas categorias → "Todas as categorias". (Sidebar mobile + busca/filtros reais = follow-up.)
- [x] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- Seguir o **padrão do Aurora** (`P3-TPL-01`): port fiel do HTML, **Shell + ProductCard + paleta por template**, reusando carrinho/`format`/resolver/FontAwesome. Como **cada template tem seu Shell**, o resolver passa a expor `Shell` no contrato `Template` pras **páginas avulsas** (`/checkout`, `/pedido`, `/conta`, `/institucional/*`) renderizarem o shell certo.
- **Conteúdo estático/lorem** de cada template (anúncio/editorial/etc.) → dinâmico no painel = `P3-TPL-03`.
- "Produtos por categoria (N)" era follow-up de `P3-TPL-01`/`P3-SF-01` — **promovido pra escopo** aqui.
- **Implementação:** **Bazar** (`templates/bazar/*`) = **indigo/rose** (defaults Tailwind = a paleta do template, sem `@theme` novo) + **Plus Jakarta Sans** (`--font-jakarta` no `layout.tsx`) + shadows `soft`/`float` no `globals.css @theme`. **Studio** (`templates/studio/*`) = **black/gray** (defaults) + Inter + **sidebar `lg:block`** (catálogo). Aurora = `brand` custom. `Template` ganhou **`Shell`**; cada index exporta o seu. Rotas avulsas em **inglês**: `account`/`order-confirmation`/`pages/[slug]`/`checkout` resolvem o shell ativo. `CheckoutView` (single-page) é compartilhado (mora em `templates/aurora/`).

## Follow-ups
- [ ] **Checkout + confirmação (Bazar/Studio)** — *Quando:* **Fase 6**. → README.
- [ ] **Busca real** (topbar do Studio é placeholder) — *Quando:* pós-V1. → README.
- [ ] **Filtros avançados / faceted** (sidebar do Studio é simples) — *Quando:* pós-V1. → README.
- [ ] **Home 100% configurável (blocos)** — *Quando:* pós-V1 (hoje defaults por template + ordem das categorias). → README.
- [ ] **Sidebar do Studio no mobile (drawer)** — *Quando:* pós-V1 (hoje `lg:block`; no mobile o catálogo vem por `/products`). → README.
- [ ] **`CheckoutView` em local compartilhado** — *Quando:* refino (hoje em `templates/aurora/`, usado pelos 3 templates). → README.
- [ ] **Home do Studio mostra os destaques** (não o catálogo todo) — *Quando:* quando a home expuser uma lista paginada de produtos (hoje usa `featured_products`). → README.
