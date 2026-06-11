---
id: P3-TPL-01
title: Arquitetura de templates + Aurora (POC)
phase: 3
etapa: "Etapa 3 — Módulo de conteúdo/layout"
area: TPL
status: done
depends_on: [P3-SF-02, P3-FE-02, P3-LOC-01]
blocks: [P3-TPL-02, P3-TPL-03]
tests: [unit, e2e]
---

# P3-TPL-01 — Arquitetura de templates + Aurora (POC)

## Contexto
O spec dos templates fechou: o **contrato e as regras** vivem no guia [`docs/design/templates/README.md`](../../design/templates/README.md) e os **designs** (HTML) em `docs/design/templates/<nome>/`. Esta task implementa a **arquitetura de templates** no storefront (resolver + blocos compartilhados) e porta o **Aurora** (telas de navegação) como **POC**, provando que a vitrine resolve um template rico por loja com o mesmo contrato de dados. Bazar/Studio validam o contrato em `P3-TPL-02`.

## Docs de referência
- [Guia dos templates](../../design/templates/README.md) (contrato/regras/blocos) + designs em `docs/design/templates/aurora/`
- [10 — Storefront & Layouts](../../concepts/10_storefront_and_layouts.md) (§"Sistema de templates")
- [`P3-SF-01`](./P3-SF-01-storefront-public-api.md) / [`P3-SF-02`](./P3-SF-02-storefront-rendering.md) (API pública + render base)

## Escopo (o que ENTRA)
- **Resolver/registry de template:** mapeia `active_template_id` da loja → **árvore de componentes** do template, em runtime. **Fallback** seguro se ausente/inválido (cai pro template base, não quebra).
- **Seed `content_theme_templates`:** registra `aurora`/`bazar`/`studio` com `preview_image_url` (por ora **seed/hardcoded**; o admin de cadastro é Fase 4).
- **Blocos compartilhados** (base pros 3 templates): **CartDrawer** (mini-carrinho, estado client, sem lógica de carrinho ainda), **Carousel** de banners (1 = banner, 2+ = carrossel), **ProductCard** (evoluir o atual), shell (header/footer/WhatsApp).
- **Aurora (navegação):** portar do HTML em `docs/design/templates/aurora/` pra componentes React + **Tailwind v4** do storefront: `home` (hero/carrossel + faixa de categorias + **destaques** + banner editorial), `category` (listagem), `product` (galeria + "Adicionar ao carrinho" + **slot "Personalizar em 3D"** reservado).
- **Preço pelo locale da loja** (`P3-LOC-01`) em todos os cards/preços.

## Fora de escopo (o que NÃO entra)
- **Bazar e Studio** (navegação) + dados de bloco específicos (produtos-por-categoria, sidebar/filtros): `P3-TPL-02`.
- **Painel — seletor de template com preview:** `P3-TPL-03`.
- **Checkout + confirmação** (funcionais, com carrinho/pedido): **Fase 6** (designs já existem em `docs/design/templates/aurora/`).
- **Editor 3D:** Fase 7 (aqui só **reservar** o slot no produto).
- **Admin pra cadastrar templates / preview ao vivo:** Fase 4 / futuro.

## Arquivos a criar/alterar
- `frontend-storefront/templates/aurora/{Home,Category,Product}.tsx` (criar) — árvore do Aurora.
- `frontend-storefront/lib/templates.ts` (criar) — resolver `active_template_id` → árvore + fallback.
- `frontend-storefront/components/{CartDrawer,Carousel,ProductCard}.tsx` (criar/alterar) — blocos compartilhados.
- `frontend-storefront/app/**` (alterar) — páginas renderizam a árvore do template ativo via resolver.
- `backend/app/modules/content/{models,services}.py` + seed (alterar) — `content_theme_templates` (3 + `preview_image_url`); garantir `active_template_id` na loja (+ **migration** se faltar campo).
- `docs/concepts/10_storefront_and_layouts.md` (alterar) — reconciliar o sistema implementado.

## Passos
1. Resolver/registry + seed dos 3 templates (`preview_image_url`).
2. Blocos compartilhados: CartDrawer, Carousel, ProductCard.
3. Portar Aurora `home`/`category`/`product` (do HTML → componentes).
4. Ligar as páginas ao resolver; preço por locale da loja.
5. e2e: Aurora renderiza home/categoria/produto + navegação card→produto + drawer abre.

## Testes
> Regra em [`_foundations-and-bottlenecks.md`](../_foundations-and-bottlenecks.md) §10.

- **Níveis:** unit (resolver) + e2e (render Aurora). **Quando:** durante.
- **Cobrir:**
  - unit — resolver: `active_template_id` válido → árvore certa; ausente/inválido → fallback base.
  - e2e — home/categoria/produto do Aurora renderizam; card→produto navega; drawer abre/fecha.

## Definition of Done
- [x] Resolver + seed: loja com `active_template_id=aurora` renderiza a **árvore do Aurora** (smoke real: `data-template="aurora"` + Destaques/Ver produtos/Todas as categorias/carrinho); ausente/inválido → **fallback base**.
- [x] Aurora `home`/`category`/`product` portados (hero, faixa de categorias, destaques, galeria, **slot "Personalizar em 3D"**), **preço pelo locale da loja**.
- [x] **CartDrawer** (botão no header + drawer) abre/fecha — estado client; **sem** lógica de carrinho (Fase 6).
- [x] Gates verdes: storefront (`next build` + biome) + backend (lint/cobertura) + **smoke real** da home Aurora. *(e2e Playwright do storefront ainda não existe — follow-up de `P3-SF-02`.)* docs 10 reconciliado.
- [x] **Modos de falha mapeados:** template ausente/inválido → **fallback base**; banner ausente → fundo `--primary`; sem categorias → strip some; sem destaques → estado vazio. (Carrossel multi-banner = follow-up.)
- [x] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- O **spec/contrato** vive no guia [`README.md`](../../design/templates/README.md); esta task é a **implementação**. `content_banners`/`content_menus` (`P3-CONTENT-01`) já existem e são a base de carrossel/navegação.
- Os designs vêm do uxpilot via **Tailwind CDN**; no porting convertem-se pra **Tailwind v4** do projeto + tema (`--primary`, fontes) da loja.
- **Implementação:** resolver em `frontend-storefront/lib/templates.ts` (fallback `base`); `templates/{base,aurora}/{Home,Category,Product}` (árvores); `components/CartDrawer.tsx` (client). As páginas (`app/**`) ficaram **finas** (fetch → `resolveTemplate` → render). `base` = render legado (classic/modern); **bazar/studio caem no base** até `P3-TPL-02`. Seed `aurora/bazar/studio` em `content_theme_templates`; tbrindes setada em `aurora` no dev.

## Follow-ups
- [ ] **Checkout + confirmação do Aurora** (funcionais) — *Quando:* **Fase 6** (carrinho/pedido). Designs prontos em `docs/design/templates/aurora/`. → README.
- [ ] **Bazar + Studio** (navegação) + dados de bloco — rastreado em `P3-TPL-02`. → README.
- [ ] **Painel: seletor de template com preview** — rastreado em `P3-TPL-03`. → README.
- [ ] **Carrossel multi-banner na home** — *Quando:* quando a API pública expor a lista de banners (hoje o hero usa `theme.banner_image_url` único). → README.
- [ ] **Imagens de categoria** — *Quando:* quando `Category` tiver imagem (hoje a faixa de categorias usa a inicial do nome). → README.
- [ ] **`preview_image_url` dos templates** — *Quando:* quando houver os `print.png` (hoje seedam sem imagem de preview). → README/`P3-TPL-03`.
