# Fase 7 — Produtos 3D (catálogo da plataforma)

> Objetivo: a loja passa a vender **produtos 3D** e **3D personalizáveis** **escolhendo do catálogo público da plataforma** — modelos GLB personalizáveis **prontos** que a **Kriar disponibiliza**. O lojista **só seleciona** o modelo e vincula ao produto; o cliente personaliza no storefront (editor 3D), aprova, e a personalização é **congelada no pedido**. Construída sobre as Fases 2 (catálogo), 3 (storefront) e 6 (checkout).
>
> **Contrato técnico completo no doc [30](../concepts/30_3d_customization_technical_design.md)** (preparo do GLB, área imprimível/decal, editor de 2 painéis, `state_json`, snapshot, storage, link público). A **experiência** está no doc [22](../concepts/22_product_customization_3d.md). Esta fase **executa** o doc 30 — não redecide.
>
> **Decomposta em tasks:** índice detalhado em [`phase-7-3d-products/README.md`](./phase-7-3d-products/README.md). Este `.md` é a **trilha** de alto nível.

Docs de referência: [30](../concepts/30_3d_customization_technical_design.md), [22](../concepts/22_product_customization_3d.md), [07](../concepts/07_database_strategy.md), [13](../concepts/13_performance_cache_and_cdn.md), [14](../concepts/14_security_strategy.md), [10](../concepts/10_storefront_and_layouts.md), [09](../concepts/09_merchant_dashboard.md), [25](../concepts/25_platform_admin.md), [16](../concepts/16_testing_strategy.md).

> **Decisões de entrada (doc 30):** **1 modelo inicial = caneca branca de cerâmica** (GLB já gerado no Tripo3D); editor = **imagem + transform + texto** (**sem troca de cor do produto** na V1); arte **só raster (PNG/JPG)**; assistida = **link público + confirmação de contato** (sem conta). Lib = **react-three-fiber + drei**; área imprimível = **decal projetado**, **parametrizado no banco e editável no admin** (mesma ferramenta que o lojista usa na [Fase 12](./phase-12-merchant-3d-generation.md)).

> **Catálogo da plataforma, não por loja.** Os modelos 3D são **públicos** (da Kriar), **populados por seed pelo dev**. O **admin** **habilita/desabilita** e **edita a área imprimível** (parâmetros no banco). O caminho "**o lojista gera o próprio GLB via API externa**" é a **[Fase 12](./phase-12-merchant-3d-generation.md)**.

## Definition of Done da fase
- Existe um **catálogo público de modelos 3D** (plataforma), populado por **seed**, com a **caneca** como primeiro modelo; o **admin habilita/desabilita** e **edita os parâmetros da área imprimível** (ferramenta visual).
- Produto pode ser **`image`**, **`image_3d`** ou **`image_3d_customizable`** — o campo `type` no `catalog_products` **já existe desde a Fase 6** (default `image`); a Fase 7 **ativa** os tipos 3D ao vincular um modelo **do catálogo**.
- O lojista **escolhe um modelo do catálogo público** e vincula ao produto (sem gerar nada, sem custo).
- Cliente personaliza no **editor 3D do storefront** (react-three-fiber): **painel 2D** de edição (imagem + texto, posição/escala/rotação dentro da área) + **painel 3D ao vivo** (girar/zoom/mover), **autosave** e **aprovação** antes do carrinho.
- Personalização aprovada é **congelada no pedido** (cópia própria com `state_json` + `version_id` + snapshot; não depende da sessão viva).
- O lojista pode **montar a personalização em nome do cliente** (pré-cadastrado por e-mail/telefone); o cliente vê por **link público** e **aprova confirmando o contato**, seguindo o fluxo normal (carrinho/checkout).
- Lojista vê as sessões/arte da própria loja e atualiza o **status de arte/produção**.
- Testes: isolamento (sessão só da loja), arte **privada** (URL assinada), congelamento no pedido, gate `image_3d_customizable` só com sessão `approved`.

## Etapa 1 — Catálogo público de modelos 3D (plataforma, via seed)
> Modelos **da plataforma** (sem `store_id`); o **GLB** vem por seed, a **área imprimível/limites** ficam em JSON no banco (editáveis no admin). Padrão do registro de templates (Fase 4): conteúdo por seed.
- [ ] **Pré-processamento do GLB (gate da pipeline)** — o source vem **sempre em 4K (~56 MB)**; otimizar pra web (textura 4K → ~1–2K, decimate < ~150k tri, **Draco**) derrubando pra **poucos MB**, **automatizável via `gltf-transform`** (sem Blender). O GLB **otimizado** sobe ao **CDN** (`public/3d-models/<slug>/v<N>/model.glb`). Origem dos arquivos = `glb-models/`. Doc [30 §1](../concepts/30_3d_customization_technical_design.md).
- [ ] Tabelas **platform-owned**: `platform_3d_models` (`name`, `category`, `slug`, `is_active`, soft delete) + `platform_3d_model_versions` (`model_id`, `version`, `glb_url`, `printable_areas` JSON, `text_config` JSON, `art_limits` JSON, `is_active`). Campos/índices no doc [07](../concepts/07_database_strategy.md); JSONs no doc [30 §3/§8](../concepts/30_3d_customization_technical_design.md).
- [ ] **Definir a área imprimível** da caneca (projetor da faixa frontal) + **seed** do modelo (GLB no CDN + `printable_areas` + `text_config` + `art_limits`), populado programaticamente (análogo a `seed_content_templates`/`import_assets`).

## Etapa 2 — Admin: habilitar/desabilitar + editar a área imprimível
> O admin **não cria** modelos (GLB é seed). Governa o catálogo **e ajusta os parâmetros** da área/limites — a **mesma ferramenta de mapeamento** que o lojista usará na [Fase 12](./phase-12-merchant-3d-generation.md).
- [ ] No `platform_admin` + `frontend-admin` (Fase 4): listar modelos + **habilitar/desabilitar** (visibilidade pro lojista) + preview 3D.
- [ ] **Editor visual da área imprimível** (sobre o preview 3D): ajustar o `projector`/retângulo/limites e salvar no `platform_3d_model_versions` — sem novo deploy. **Editar afeta sessões novas**; pedidos congelados não mudam (doc [30 §3](../concepts/30_3d_customization_technical_design.md)). Doc [25](../concepts/25_platform_admin.md)/[09](../concepts/09_merchant_dashboard.md).

## Etapa 3 — Painel do lojista: escolher do catálogo + vincular ao produto
- [ ] O lojista **navega o catálogo público** (modelos habilitados), **escolhe** um e vincula ao produto, marcando-o `image_3d`/`image_3d_customizable`. `customization_product_settings` (por loja: `product_id` → `platform_3d_model_id` + observações de produção). Doc [07](../concepts/07_database_strategy.md)/[30 §8](../concepts/30_3d_customization_technical_design.md).

## Etapa 4 — Sessões de personalização (backend)
- [ ] `customization_sessions` (campos do doc [07](../concepts/07_database_strategy.md)/[30 §8](../concepts/30_3d_customization_technical_design.md): `state_json`, `platform_3d_model_version_id`, `status`, `guest_session_id`, `customer_id?`, `created_by?`, `snapshot_key?`, `public_token?`, `expires_at`) + `customization_uploads` (arte **privada**: `key`, `mime`, `size_bytes`, `width`/`height`). Status `draft|approved|added_to_cart|ordered|abandoned|expired`.
- [ ] Rotas: iniciar/obter sessão; **autosave** do `state_json` (validado contra a versão); upload de arte (raster, validado, privado, **URL assinada**); **aprovar** (gera/recebe o **snapshot** client-side, congela `state_json` + `version_id` + data). Expirar 30 dias → `expired` (worker).
- [ ] Enum de status de arte/produção (`received…production_done`).
- [ ] **Personalização assistida** (doc [30 §9](../concepts/30_3d_customization_technical_design.md)): sessão **criada pela loja** (`created_by`), pré-cadastrando o cliente por contato (`create_or_update_customer`, Fase 6) + **`public_token`** (link read-only). O cliente vê pelo link e **aprova confirmando o contato** (sem conta).

## Etapa 5 — Editor 3D no storefront (react-three-fiber)
- [ ] **Layout de 2 painéis** (doc [30 §2](../concepts/30_3d_customization_technical_design.md)): **painel 2D** (retângulo da área imprimível — arrastar/escalar/rotacionar **imagem** e **texto** dentro da área) + **painel 3D ao vivo** (`OrbitControls`: **girar/zoom/mover** a câmera). Sincronização automática 2D → decal no 3D. Responsivo: mobile empilha/abas.
- [ ] Carregar o GLB da **versão escolhida** (CDN, Draco, lazy); camadas **imagem** (upload raster) + **texto** (fonte de conjunto fechado) aplicadas via **decal** na área; **autosave**; restaurar pela `guest_session_id`.
- [ ] **Aprovação** obrigatória antes do carrinho: gera o **snapshot** (canvas → PNG, doc [30 §5](../concepts/30_3d_customization_technical_design.md)) e chama o endpoint de aprovar. **Sem troca de cor do produto** (fora da V1).

## Etapa 6 — Carrinho/pedido: congelar personalização
- [ ] `customization_cart_items` / `customization_order_items` — cópia **congelada** (`state_json` + `version_id` + **snapshot copiado** pra `private/<store_id>/orders/<order_id>/...`) no pedido (INV-P5). Regra: item `image_3d_customizable` só entra com sessão `approved` — o carrinho passa `has_approved_customization=True` ao gate [`assert_addable_to_cart`](../../backend/app/modules/catalog/services.py) (Fase 6). Doc [07](../concepts/07_database_strategy.md)/[11](../concepts/11_checkout_payments_and_split.md)/[30 §7](../concepts/30_3d_customization_technical_design.md).

## Etapa 7 — Painel do lojista: operar as personalizações
- [ ] Ver sessões/arte da loja (polling), baixar arquivos (**URL assinada**), atualizar status de arte/produção. Doc [09](../concepts/09_merchant_dashboard.md).
- [ ] **Montar a personalização pelo cliente** (assistida): a partir do contato, abrir o editor em nome dele, salvar a sessão e gerar o **link público** (`public_token`) pra o cliente ver/aprovar. Doc [30 §9](../concepts/30_3d_customization_technical_design.md).

## Etapa 8 — Vitrine: seleção de variação (geral, não-3D)
> **Veio da Fase 6** (era o fast-follow `P6-SF-02`): a página de produto da vitrine ganha o seletor de variação. Fica aqui porque é a fase que reabre a página de produto do storefront (junto do editor 3D). Não depende de 3D — só do catálogo (Fase 2) + carrinho (`P6-CART-01`, que já aceita `variant_id`).
- [ ] `StorefrontProduct` passa a expor **variações + disponibilidade** (hoje só imagem/nome/preço/descrição) — `backend/app/modules/storefront/{schemas,services}.py`. Doc [10 — Página de produto](../concepts/10_storefront_and_layouts.md)/[07](../concepts/07_database_strategy.md).
- [ ] Página de produto (3 templates): **escolher a variação** + ver disponibilidade; o add-to-cart envia o `variant_id` (o backend já guarda em `cart_items` desde `P6-CART-01`). Fecha o follow-up "Vitrine expõe variações + disponibilidade" (Fase 3, `P3-SF-01`/`P3-SF-02`) — marcar na origem ao concluir.
- [ ] **Modos de falha:** variação sem estoque (desabilita/avisa); produto sem variação (compra direta).

## Testes (doc [16](../concepts/16_testing_strategy.md))
- [ ] **Catálogo:** seed popula a caneca; admin habilita/desabilita e edita a área; só modelos habilitados aparecem pro lojista.
- [ ] **Isolamento** (sessão só da loja); **arte privada** (URL assinada); **congelamento** da personalização no pedido (não depende da sessão viva); item `image_3d_customizable` só entra no carrinho com sessão `approved`.
- [ ] **Assistida:** `public_token` abre read-only; aprovar exige confirmar o contato; editar a área no admin **não** muda pedido congelado.
- [ ] **Modos de falha** (doc [30 §11](../concepts/30_3d_customization_technical_design.md)): GLB/WebGL indisponível → fallback; upload inválido (422)/baixa resolução (aviso); falha de snapshot bloqueia aprovação; sessão expirada → clonar.
- [ ] **Variação na vitrine (Etapa 8):** integração — variações/estoque no payload público; e2e (`P3-SF-03`) — escolher variação → carrinho com o `variant_id` certo.

---

## Reconciliações (registrar aqui)
- **Modelos 3D = catálogo público da plataforma**, por **seed** (GLB) + **parâmetros no banco editáveis no admin** (área imprimível/limites). O **admin** habilita/desabilita **e edita a área** — a **mesma ferramenta** vira a base da **[Fase 12](./phase-12-merchant-3d-generation.md)** (lojista mapeia o próprio GLB). Doc [30](../concepts/30_3d_customization_technical_design.md)/[22](../concepts/22_product_customization_3d.md).
- **Editor = react-three-fiber + drei**, **2 painéis** (2D edita / 3D gira-zoom-move), **decal projetado** pra área (não UV), **snapshot client-side** na aprovação. Doc [30](../concepts/30_3d_customization_technical_design.md).
- **Sem troca de cor do produto na V1** (caneca branca = branca); **recolor é follow-up** (precisa de `color_palette` + material nomeado + seletor). **Arte só raster (PNG/JPG)**; SVG/PDF é follow-up. Doc [30 §12](../concepts/30_3d_customization_technical_design.md).
- **Storage:** GLB **público** no CDN (`public/3d-models/...`); arte/snapshot **privados** (`private/<store_id>/...`, URL assinada). Doc [30 §6](../concepts/30_3d_customization_technical_design.md).
- **Personalização assistida** = **link público** (`public_token`, read-only) + **confirmação de contato** pra aprovar (sem conta; a conta é Fase 8). Resolve a decisão antes em aberto. Doc [30 §9](../concepts/30_3d_customization_technical_design.md).
- **O lojista gerar o próprio GLB via API externa + mapear a área** = **[Fase 12](./phase-12-merchant-3d-generation.md)** (a decisão do provedor de geração fica lá).
- **Restringir a personalização a plano pago** é da **Fase 8** (aqui é livre). O gancho já existe em `require_permission` (Fase 1).
