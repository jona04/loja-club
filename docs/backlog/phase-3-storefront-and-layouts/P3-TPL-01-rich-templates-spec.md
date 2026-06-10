---
id: P3-TPL-01
title: Sistema de templates ricos da vitrine (spec → implementação)
phase: 3
etapa: "Etapa 8 — Templates no storefront"
area: TPL
status: doing            # fase de SPEC (definição). Implementação começa quando o spec fechar.
depends_on: [P3-SF-02, P3-FE-02]
blocks: []
tests: tbd
---

# P3-TPL-01 — Sistema de templates ricos da vitrine (spec)

> **Spec vivo.** Esta task é **definida conversando** (ver §"Em definição") e só vai pra implementação quando o spec fechar. Provavelmente **divide** em sub-tasks (models, templates no storefront, dashboard, admin-registry) ao fechar.

## Contexto
O V1 (`P3-SF-02`) entrega **2 templates simples** (`classic`/`modern`) por renderização condicional — não chega ao nível de uma loja de ecommerce de verdade. Esta task define e implementa um **sistema de templates profissionais**: **2–3 templates** visualmente bem distintos (carrossel no topo, hero, seções ricas), adaptados de **referências de design fornecidas pelo usuário** (feitas no "Claude design"). Mexe em **3 frentes**: models de conteúdo (mais ricos), render do storefront (uma árvore de componentes por template) e o painel (escolher template por **imagem de preview**).

## Docs de referência
- [10 — Storefront & Layouts](../../10_storefront_and_layouts.md) (§"Sistema de templates")
- [09 — Merchant Dashboard](../../09_merchant_dashboard.md) (§"Layout da loja")
- [21 — Design System](../../21_design_system_todo.md)
- [07 — Database Strategy](../../07_database_strategy.md) (tabelas `content_*`)

## Escopo (o que ENTRA)
- **Arquitetura de templates:** cada template é uma **árvore de componentes própria** no `frontend-storefront` (não só estilo condicional). Ex.: `templates/<nome>/{Home,Category,Product,blocos...}`. Um **resolver/registry** escolhe o template ativo da loja em runtime.
- **2–3 templates profissionais** adaptados das referências do usuário — bem distintos entre si (carrossel/hero/seções variadas).
- **Registro de templates:** `content_theme_templates` (global) lista os disponíveis, **cada um com `preview_image_url`** (imagem de como fica). Por ora os templates entram via **seed/código** (a tela de admin pra cadastrar é futura — ver Follow-ups).
- **Evolução dos models de conteúdo:** suportar o que os templates ricos pedem — **carrossel** (vários banners ordenados), **seções configuráveis**, destaques etc. Reaproveitar o que já existe (`content_banners`, `content_menus`, `content_pages` da `P3-CONTENT-01`) e adicionar campos/tabelas conforme as referências chegarem. **+ migration.**
- **Painel (`P3-FE-02` evolui):** a tela "Layout da Loja" mostra a **lista de templates com a imagem de preview** + os campos que cada template usa (banner/carrossel/seções). O lojista escolhe pela imagem (não há preview ao vivo ainda).

## Contrato (INVARIANTE — não negociável)
- **Trocar de template NÃO pode quebrar nada pro cliente.** Todos os templates consomem o **mesmo contrato de dados** (loja/tema/produtos/categorias) e levam ao **mesmo fluxo de compra** (produto → carrinho/checkout, Fase 4). Template muda **só a apresentação**.
- **Contrato = DADOS + FLUXO, não a composição da home.** Os **mesmos dados** ficam disponíveis (loja, banners, categorias, produtos — destaques **e** por categoria); a **composição da home** (quais blocos e quantos: destaques, **seções de categoria** com N produtos, banners…) é **por template e configurável pelo lojista**. Ex.: Aurora = só destaques; Bazar = seções de categoria. Não é o contrato que muda — é o que cada template/lojista **renderiza** dos mesmos dados.
- **Todos os templates** devem reservar um **ponto de extensão pro editor 3D** na página de produto (compatibilidade com a personalização da **Fase 5** — só **reservar** o slot agora, integrar lá).

## Fora de escopo (o que NÃO entra — anotado como futuro)
- **Tela de admin (loja.club) pra cadastrar/gerenciar templates** (o usuário-plataforma registra nome/descrição/imagem/ativar): pertence ao **admin** → **fase futura** (Fase 7 ou dedicada). Por ora, templates via seed/código. → Follow-up.
- **Preview ao vivo** no painel (render real da loja do lojista com o template): futuro — hoje só a **imagem cadastrada**. → Follow-up.
- **Editor 3D / personalização**: integração é **Fase 5**; aqui só se **reserva** o slot. → `Fase 5`.
- **Carrinho/checkout completos**: **Fase 4** (os templates já preveem o ponto de "comprar").

## Arquivos a criar/alterar (provável — fechar no spec)
- `frontend-storefront/templates/<nome>/…` (criar) — componentes por template + blocos (carrossel, seções).
- `frontend-storefront/…` (criar) — resolver/registry que mapeia `active_template_id` → árvore de componentes.
- `backend/app/modules/content/{models,schemas,repositories,services}.py` (alterar) — campos/tabelas pros templates ricos (carrossel/seções) + **migration**.
- `frontend-dashboard/src/routes/_layout/store-layout.tsx` (alterar) — lista com imagem de preview + config por template.
- `docs/10_storefront_and_layouts.md`, `docs/09_merchant_dashboard.md`, `docs/07_database_strategy.md` (alterar) — documentar o sistema + os models.
- Local pra guardar as **referências** entregues pelo usuário (a decidir — ver §"Em definição").

## Decidido (até agora) ✅
> **Guia canônico** (contrato/regras + overall context) em [`docs/design/templates/README.md`](../../design/templates/README.md); prompts por template em [`docs/design/templates/prompts/`](../../design/templates/prompts/).
- **Geração:** designs no **uxpilot.ai** (HTML + Tailwind). **1 tela = 1 prompt**; **5 telas por template** (`home`/`category`/`product`/`checkout`/`confirmation`.html) → **15 prompts** pra 3 templates. Salvos em **`docs/design/templates/<nome>/`** + `print.png` (= `preview_image_url` por **seed/hardcoded**). Prompts por template em [`prompts/`](../../design/templates/prompts/).
- **Code-based:** cada template = árvore de componentes em `frontend-storefront/templates/<nome>/`, atrás de um **resolver** por `active_template_id`.
- **3 templates iniciais:** **"Aurora"** (premium minimalista, home = destaques), **"Bazar"** (vibrante/marketplace, home = seções de categoria) e **"Studio"** (catálogo com **sidebar**, home = sidebar + grid). O **Studio é deliberadamente bem diferente em blocos/estrutura** — é o **teste** de que o storefront resolve composições distintas com o **mesmo contrato** (dados + fluxo).
- **Carrossel:** banners ordenados (`content_banners`) → **1 imagem = banner, 2+ = carrossel**, configurado no painel do lojista.
- **3D:** página de produto reserva o **placeholder "Personalizar em 3D"** (integra na Fase 5).
- **Fluxo de compra (Fase 4, sem pagamento)** em **cada template** (único, não compartilhado): **checkout single-page** (itens + contato c/ **seletor de país** E.164 + endereço + **4 opções de entrega** incl. entrega combinada + resumo) + tela de **Confirmação**. O **carrinho é um drawer** (mini-carrinho no header), **não** página separada. Pagamento (gateway/split) = **Fase 6**.

## Ainda em definição 🔧
- Blocos **configuráveis** por template (quais o lojista liga/desliga); variações/disponibilidade/relacionados no V1 ou follow-up.
- **Models:** seções via config (JSON?) ou tabela; campos novos no `content_store_theme_settings`.
- Reformulação da **ordem/prioridade das fases** (o usuário vai reorganizar).

## Passos (alto nível — detalhar no spec)
1. **Fechar o spec** (arquitetura + models + contrato + lista de templates + blocos) conversando.
2. Evoluir os **models** de conteúdo + migration; reconciliar docs 10/09/07.
3. Adaptar **2–3 referências** em templates (árvores de componentes) no storefront, atrás do resolver.
4. Atualizar o **painel** (lista + imagem de preview + config por template).
5. Garantir o **contrato** (troca não quebra a compra; slot 3D reservado).

## Testes
> Regra em [`_foundations-and-bottlenecks.md`](../_foundations-and-bottlenecks.md) §10.

- **Níveis:** a decidir no spec — provável **e2e** (cada template renderiza home/produto/categoria; **trocar template não quebra** a navegação até "comprar") + **unit** (resolver/registry; config de seções).
- **Cobrir:** template ativo resolve a árvore certa; troca de template mantém o fluxo do cliente; template/preview ausente degrada bem.

## Definition of Done
- [ ] **Spec fechado** (arquitetura + models + contrato + lista de templates + blocos) revisado com o usuário.
- [ ] 2–3 templates ricos renderizam home/produto/categoria; **trocar template não quebra** o fluxo do cliente (mesmo contrato de compra).
- [ ] `content_theme_templates` lista os templates com `preview_image_url`; o painel mostra **lista + imagem**.
- [ ] Models de conteúdo evoluídos (carrossel/seções) + **migration**; docs 10/09/07 reconciliados.
- [ ] **Slot de extensão pro 3D** (Fase 5) reservado em todos os templates.
- [ ] **Modos de falha mapeados** (template sem dados; template inválido/removido; `preview_image_url` ausente; troca de template com config incompatível) → tratados ou Follow-up.
- [ ] Itens adiados varridos → Follow-ups + README.

## Notas / Reconciliações
- `content_banners`, `content_menus`, `content_pages` (`P3-CONTENT-01`) **já existem** e viram a base de **carrossel/navegação/páginas** dos templates ricos.
- Esta task **reabre a Fase 3**: o storefront base + os 2 templates simples (`classic`/`modern`) estão `done`; aqui eleva pra **templates profissionais**.
- **Teste do contrato:** os 3 templates iniciais (Aurora/Bazar/Studio) validam a hipótese "**composição ≠ contrato**". O **Studio** (sidebar/catálogo) é deliberadamente distinto em blocos/estrutura — se o storefront renderizar os 3 com o **mesmo contrato de dados + fluxo**, a hipótese se confirma. É o caso de stress da arquitetura de templates.
- **Living spec** → ao fechar, deve **dividir** em sub-tasks (ex.: `P3-TPL-02` models, `P3-TPL-03` templates no storefront, `P3-TPL-04` painel).

## Follow-ups
- [ ] **Tela de admin (loja.club) pra cadastrar templates** — *Quando:* quando o admin da plataforma existir (**Fase 7**/admin). Por ora templates via seed/código. → README.
- [ ] **Preview ao vivo no painel** — *Quando:* pós-V1 (hoje só a imagem cadastrada). → README.
- [ ] **Compatibilidade 3D dos templates** — *Quando:* **Fase 5** (slot reservado agora; integração lá). → README.
- [ ] **Definir entrega das referências + onde salvar** — *Quando:* na conversa do spec. → README.
- [ ] **Dados "produtos por categoria" na home** (`P3-SF-01`/`P3-TPL-01`): pra templates com **seções de categoria** (ex.: Bazar), a home precisa dos primeiros N produtos por categoria (+ "ver todos"). Pequena adição na API pública.
- [ ] **Home configurável (blocos)** (`P3-TPL-01`): lojista escolhe blocos/ordem/quais categorias na home. V1 = **defaults por template** + ordem das categorias; builder completo é follow-up.
- [ ] **Overflow de categorias no nav** (`P3-TPL-01`): muitas categorias → **top N + "Todas as categorias"** (menu/página), não uma barra com 20.
