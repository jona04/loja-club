# Fase 7 — Produtos 3D (catálogo da plataforma)

> Objetivo: a loja passa a vender **produtos 3D** e **3D personalizáveis** **escolhendo do catálogo público da plataforma** — modelos GLB personalizáveis **prontos** (caneca, camiseta, ecobag…) que a **Kriar disponibiliza**. O lojista **só seleciona** o modelo do catálogo e vincula ao produto; o cliente personaliza no storefront (editor 3D), aprova, e a personalização é **congelada no pedido**. Construída sobre as Fases 2 (catálogo), 3 (storefront) e 6 (checkout).

Docs de referência: [22](../concepts/22_product_customization_3d.md), [07](../concepts/07_database_strategy.md), [13](../concepts/13_performance_cache_and_cdn.md), [14](../concepts/14_security_strategy.md), [18](../concepts/18_open_decisions.md), [10](../concepts/10_storefront_and_layouts.md), [09](../concepts/09_merchant_dashboard.md), [25](../concepts/25_platform_admin.md), [16](../concepts/16_testing_strategy.md).

> **Catálogo da plataforma, não por loja.** Os modelos 3D são **públicos** (da Kriar), **populados por seed pelo dev** (programaticamente, igual ao registro de templates da Fase 4 — mais rápido e barato que cada lojista gerar o GLB de um item comum). O **admin** apenas **habilita/desabilita** modelos do catálogo. O caminho "**o lojista gera o próprio GLB via API externa + mapeia a área personalizável**" é a **[Fase 12](./phase-12-merchant-3d-generation.md)** (avançado/DIY).

## Definition of Done da fase
- Existe um **catálogo público de modelos 3D** (plataforma), populado por **seed**; o **admin habilita/desabilita** quais estão disponíveis.
- Produto pode ser **`image`**, **`image_3d`** ou **`image_3d_customizable`** — o campo `type` no `catalog_products` **já existe desde a Fase 6** (default `image`); a Fase 7 **ativa** os tipos 3D ao vincular um modelo **do catálogo**.
- O lojista **escolhe um modelo do catálogo público** e vincula ao produto (sem gerar nada, sem custo).
- Cliente personaliza no **editor 3D do storefront** (Three.js): arte, cor, texto, posição/escala/rotação, preview, autosave e **aprovação** antes do carrinho.
- Personalização aprovada é **congelada no pedido** (cópia própria; não depende da sessão viva).
- O lojista pode **montar a personalização em nome do cliente** (pré-cadastrado por e-mail/telefone); o cliente vê/aprova e segue o fluxo normal (carrinho/checkout).
- Lojista vê as sessões/arte da própria loja e atualiza o **status de arte/produção**.
- Testes: isolamento (sessão só da loja), arte **privada** (URL assinada), congelamento no pedido.

## Etapa 1 — Catálogo público de modelos 3D (plataforma, via seed)
> Os modelos são **da plataforma** (sem `store_id`), com a **área imprimível** e os limites já definidos no próprio seed (quem desenha é o dev). É o mesmo padrão do registro de templates (Fase 4): conteúdo via seed, não CRUD complexo de UI.
- [ ] Tabelas **platform-owned** do catálogo 3D: o modelo (nome, categoria, GLB no storage da plataforma/CDN, `is_active`) + versões (GLB, parâmetros, **áreas imprimíveis**, limites de cor/texto). Doc [07](../concepts/07_database_strategy.md)/[22](../concepts/22_product_customization_3d.md).
- [ ] **Seed** dos modelos iniciais (ex.: caneca, camiseta) — GLB + área + config, populado programaticamente (análogo a `import_assets`/registro de templates). GLB servido por CDN.

## Etapa 2 — Admin: habilitar/desabilitar modelos do catálogo
> O admin **não cria** modelos (isso é seed). Só governa o catálogo.
- [ ] No `platform_admin` + `frontend-admin` (Fase 4): listar os modelos do catálogo + **habilitar/desabilitar** (visibilidade pro lojista) + preview. Doc [25](../concepts/25_platform_admin.md)/[09](../concepts/09_merchant_dashboard.md).

## Etapa 3 — Painel do lojista: escolher do catálogo + vincular ao produto
- [ ] O lojista **navega o catálogo público** (modelos habilitados), **escolhe** um e vincula ao produto, marcando-o como `image_3d`/`image_3d_customizable`. `customization_product_settings` (por loja: produto → modelo do catálogo, permite cor?, observações de produção). Doc [07](../concepts/07_database_strategy.md)/[22](../concepts/22_product_customization_3d.md).

## Etapa 4 — Sessões de personalização (backend)
- [ ] `customization_sessions` (campos do doc [07](../concepts/07_database_strategy.md)) + `customization_uploads` (arte privada). Status `draft|approved|added_to_cart|ordered|abandoned|expired`.
- [ ] Rotas: iniciar/obter sessão; **autosave** do `state_json`; upload de arte (validado, privado, URL assinada); preview; **aprovar** (congela snapshot + versão do modelo do catálogo + data). Expirar 30 dias → `expired` (worker).
- [ ] Enum de status de arte/produção (`received…production_done`).
- [ ] **Personalização assistida pelo lojista** (doc [22](../concepts/22_product_customization_3d.md)): sessão **criada pela loja em nome do cliente** (`created_by` = usuário da loja), pré-cadastrando o cliente por e-mail/telefone (`create_or_update_customer`, Fase 6). O cliente acessa e **aprova**; **acesso (login vs link público) = decisão em aberto** ([18](../concepts/18_open_decisions.md)).

## Etapa 5 — Editor 3D no storefront (Three.js)
- [ ] Carregar o GLB do **modelo do catálogo** (versão escolhida, CDN); upload de arte; texto/cor/posição/escala/rotação dentro da área imprimível; preview; **autosave**; **aprovação** obrigatória antes do carrinho; restaurar pela `guest_session_id`. Doc [10](../concepts/10_storefront_and_layouts.md)/[22](../concepts/22_product_customization_3d.md).

## Etapa 6 — Carrinho/pedido: congelar personalização
- [ ] `customization_cart_items` / `customization_order_items` — cópia congelada da personalização aprovada no pedido (INV-P5). Regra: item `image_3d_customizable` só entra com sessão `approved`. Doc [07](../concepts/07_database_strategy.md)/[11](../concepts/11_checkout_payments_and_split.md).

## Etapa 7 — Painel do lojista: operar as personalizações
- [ ] Ver sessões/arte da loja (polling), baixar arquivos (URL assinada), atualizar status de arte/produção. Doc [09](../concepts/09_merchant_dashboard.md).
- [ ] **Montar a personalização pelo cliente** (assistida): a partir do contato do cliente, abrir o editor em nome dele, salvar a sessão e gerar o **link de acesso** para o cliente ver/aprovar. Doc [22](../concepts/22_product_customization_3d.md).

## Etapa 8 — Vitrine: seleção de variação (geral, não-3D)
> **Veio da Fase 6** (era o fast-follow `P6-SF-02`): a página de produto da vitrine ganha o seletor de variação. Fica aqui porque é a fase que reabre a página de produto do storefront (junto do editor 3D). Não depende de 3D — só do catálogo (Fase 2) + carrinho (`P6-CART-01`, que já aceita `variant_id`).
- [ ] `StorefrontProduct` passa a expor **variações + disponibilidade** (hoje só imagem/nome/preço/descrição) — `backend/app/modules/storefront/{schemas,services}.py`. Doc [10 — Página de produto](../concepts/10_storefront_and_layouts.md)/[07](../concepts/07_database_strategy.md).
- [ ] Página de produto (3 templates): **escolher a variação** + ver disponibilidade; o add-to-cart envia o `variant_id` (o backend já guarda em `cart_items` desde `P6-CART-01`). Fecha o follow-up "Vitrine expõe variações + disponibilidade" (Fase 3, `P3-SF-01`/`P3-SF-02`) — marcar na origem ao concluir.
- [ ] **Modos de falha:** variação sem estoque (desabilita/avisa); produto sem variação (compra direta).

## Testes (doc [16](../concepts/16_testing_strategy.md))
- [ ] **Catálogo:** seed popula os modelos; admin habilita/desabilita; só modelos habilitados aparecem pro lojista.
- [ ] **Isolamento** (sessão de personalização só da loja); **arte privada** (URL assinada); **congelamento** da personalização no pedido (não depende da sessão viva); item `image_3d_customizable` só entra no carrinho com sessão `approved`.
- [ ] **Variação na vitrine (Etapa 8):** integração — variações/estoque no payload público; e2e (`P3-SF-03`) — escolher variação → carrinho com o `variant_id` certo.

---

## Reconciliações (registrar aqui)
- **Modelos 3D = catálogo público da plataforma**, populado **por seed** pelo dev (rápido/barato; o lojista não gera GLB de item comum). O **admin só habilita/desabilita**. Reverte a postura anterior de "modelos por loja, sem catálogo da plataforma" — ver doc [22](../concepts/22_product_customization_3d.md) (atualizado).
- **O lojista gerar o próprio GLB via API externa (Meshy/Tripo3D/Hyper3D) + mapear a área personalizável pelo painel** = **[Fase 12](./phase-12-merchant-3d-generation.md)** (avançado). A decisão do provedor de geração fica lá (doc [18](../concepts/18_open_decisions.md)).
- **Restringir a personalização a plano pago** é da **Fase 8** (planos/pagamentos); aqui é livre. O gancho de plano já existe em `require_permission` (Fase 1).
- **Personalização assistida pelo lojista** (lojista monta em nome do cliente, pré-cadastrado por contato): doc [22](../concepts/22_product_customization_3d.md); o **acesso do cliente** (login vs link público) é **decisão em aberto** ([18](../concepts/18_open_decisions.md)) — a parte de login depende da Fase 8.
