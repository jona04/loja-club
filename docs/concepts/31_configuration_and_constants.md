# 31 — Configuração, constantes e valores mágicos

**Registro único** de tudo que é **ajustável**: settings de ambiente, números mágicos hard-coded (TTLs, limites, tamanhos, agendamentos), defaults e enums. É a **fonte de verdade** desses valores — o código os reflete, não o contrário.

> **Regra (ver [CLAUDE.md](../../CLAUDE.md)):** todo **número mágico**, **constante de configuração** ou **valor default** novo (no código ou em tabela) **entra aqui** — não pode ficar só na task nem solto no código. Ao mudar o valor no código, atualizar esta doc na mesma mudança.

> **Futuro:** muitos destes valores vão virar **configuração em tabela** (por plataforma e por loja). Enquanto isso, esta doc é o catálogo. Quando migrarem pro banco, a coluna/tabela passa a ser a fonte e esta doc aponta pra ela.

**Legenda de origem:**
- **env** — vem de variável de ambiente ([`backend/app/core/config.py`](../../backend/app/core/config.py)); default abaixo.
- **const** — constante hard-coded no código (módulo indicado).
- **seed/DB** — valor inicial semeado, **editável** e persistido em tabela (já é "config no banco").

---

## 1. Settings de ambiente (`app/core/config.py`)

| Setting | Default | Significado |
|---|---|---|
| `ENVIRONMENT` | `development` | `development` / `staging` / `production`. |
| `SECRET_KEY` | `token_urlsafe(32)` | Assinatura de JWT (em prod vem de segredo). |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60*24*8` (**8 dias**) | Validade do JWT de acesso (painel/admin). |
| `EMAIL_RESET_TOKEN_EXPIRE_HOURS` | `48` | Validade do token de reset de senha. |
| `FRONTEND_HOST` | `http://localhost:5173` | Origem do front (CORS/links). |
| `DOMAIN` | `localhost` | Domínio base. |
| `POSTGRES_PORT` | `5432` (dev `5442`) | Porta do Postgres. |
| `REDIS_PORT` | `6379` (dev `6399`) | Porta do Redis. |
| `REDIS_DB` | `0` | Índice do banco Redis. |
| `SMTP_PORT` | `587` | Porta SMTP. |
| `S3_REGION` | `us-east-2` | Região AWS do bucket/CDN. |
| `CDN_BASE_URL` | — | Base pública (CloudFront) dos objetos `public/`. |

> Lista completa (incl. credenciais/segredos, nunca commitados) em `config.py` + [`.env.example`](../../backend/.env.example). Segurança em [14](./14_security_strategy.md).

## 2. Portas de dev (não-padrão)

Definidas no `compose.override.yml` (origem: [`P0-CFG-02`](../backlog/phase-0-foundation/P0-CFG-02-env-config.md)):

| Serviço | Porta |
|---|---|
| Postgres (`db`) | `5442` |
| Redis | `6399` |
| Backend | `8800` |
| Painel (`frontend-dashboard`) | `5180` |
| Admin (`frontend-admin`) | `5181` |
| Adminer | `8810` |
| Mailcatcher | `1090` / `1035` |
| Traefik | `8088` / `8091` |

## 3. Tokens, sessões e cache

| Valor | Onde | Origem | Significado |
|---|---|---|---|
| `token_urlsafe(32)` | `SECRET_KEY`, `guest_session_id`, `public_token` | const | Tamanho dos tokens opacos/inadivinháveis. |
| Presigned URL = **3600 s** (1 h) | `app/core/storage.generate_presigned_url` (default) | const | Validade da URL assinada de objeto privado. |
| Cache de domínio→loja = **300 s** | `tenancy.services._DOMAIN_CACHE_TTL` | const | TTL da resolução de host. |
| Cache da vitrine = **300 s** | `storefront.services._TTL` | const | TTL das leituras read-through da vitrine ([13](./13_performance_cache_and_cdn.md)). |
| Checkout = **24 h** | `checkout.services._CHECKOUT_TTL` | const | Janela de um checkout ativo. |
| Guest session = **30 dias** | `customers.services.GUEST_SESSION_TTL` | const | Validade do cookie/sessão anônima. |

## 4. Personalização 3D (Fase 7 — doc [30](./30_3d_customization_technical_design.md))

| Valor | Onde | Origem | Significado |
|---|---|---|---|
| **Sessão = 30 dias** | `customization.sessions.SESSION_TTL` | const | TTL da sessão de personalização (doc [07](./07_database_strategy.md)). |
| **Expiração: cron diário, 03:00 UTC** | `core/queue.WorkerSettings.cron_jobs` | const | Varre sessões `draft`/`approved` vencidas → `expired` + `deleted_at`. **Hora não-crítica:** a expiração também é aplicada **no acesso** (autosave/upload/approve/link vencido → **410**); o cron é só faxina. Granularidade diária basta pra janela de 30 dias. (É o 1º `cron_job`; sem convenção de agendamento ainda.) |
| Upload: **30 MiB** máx. | `sessions._DEFAULT_MAX_BYTES` (fallback) / `art_limits.max_bytes` (seed/DB) | const + seed/DB | Tamanho máx. **por imagem** enviada (o editor avisa o limite e barra antes de enviar). |
| Upload: **`image/png`, `image/jpeg`** | `sessions._DEFAULT_MIMES` / `art_limits.mimes` | const + seed/DB | Tipos aceitos (raster). |
| Upload: **dimensão mín. 300 px** | `sessions._DEFAULT_MIN_DIMENSION` / `art_limits.min_dimension` | const + seed/DB | Abaixo disso = **aviso** de baixa resolução (não bloqueia). |
| Snapshot de aprovação = **PNG** | `sessions.SNAPSHOT_MIME` | const | Foto do canvas no approve (doc 30 §5). |
| Autosave do editor = **1500 ms** (debounce) | `frontend-storefront/lib/use-customizer.AUTOSAVE_DEBOUNCE_MS` | const | Espera após a **última** edição antes de salvar o `state_json` (só dispara 1× quando o cliente para de editar; não salva durante o arrasto/rotação). |
| Textura do editor = **1024 px** | `frontend-storefront/lib/customizer/compose.EDITOR_TEXTURE_SIZE` | const | Resolução do canvas do overlay 3D (qualidade/perf do preview). |
| Composite de produção = **2048 px** (largura) | `frontend-storefront/lib/customizer/compose.COMPOSITE_WIDTH` | const | Resolução do retângulo de produção (a arte achatada de alta qualidade, §5 doc 30). |
| Teto de sanidade do transform = **20** | `customization.sessions._MAX_TRANSFORM` | const | Limite de `transform.x/y/scale/scale_y` no `state_json` — centros saem de [0,1] ao panear; só rejeita lixo (NaN/∞/absurdo). |
| Server Action body = **50 MB** | `frontend-storefront/next.config.ts` (`serverActions.bodySizeLimit`) | const | Folga geral pro Next (default é **1 MB** → causava 413). O upload de arte (≤ 30 MB) + snapshot + composite vão por **Route Handlers** (`app/api/customizer/*`, via XHR p/ progresso), não Server Actions. |
| Teto do payload de aprovação = **48 MB** | `frontend-storefront/lib/customizer/snapshot.APPROVE_PAYLOAD_LIMIT_BYTES` | const | Snapshot + composite; um pouco abaixo do body de 50 MB (folga p/ multipart). O cliente mostra o tamanho e barra se passar. |
| Polling do painel de personalizações = **10 s** | `frontend-dashboard/.../customizations.POLL_INTERVAL_MS` | const | Atualização quase em tempo real da lista de sessões (doc [22](./22_product_customization_3d.md)); WebSocket é follow-up. |

**Seed/DB da caneca** (`platform_3d_model_versions`, **editável no admin** — `P7-ADM-01`):

| Campo (JSON) | Valor semeado |
|---|---|
| `printable_areas` | 1 área `front`, `uv_rect` `{u0:0.2, v0:0.3, u1:0.8, v1:0.7}`, `max_layers: 5` |
| `text_config` | `fonts: [inter, roboto, montserrat]`, `min_size: 8`, `max_size: 96` |
| `art_limits` | `mimes: [image/png, image/jpeg]`, `max_bytes: 30 MiB`, `min_dimension: 300` |

**Pipeline GLB** ([`scripts/glb/optimize-glb.mjs`](../../scripts/glb/optimize-glb.mjs)):

| Valor | Default | Significado |
|---|---|---|
| `textureSize` | `2048` | Aresta máx. da textura (4K→2K). |
| `simplifyError` | `0.001` | Tolerância do `simplify`. |
| `--simplify` da caneca v1 | `0.25` | Perfil publicado (~2 MB, 491k tris). |

## 5. Uploads de mídia (catálogo)

| Valor | Onde | Significado |
|---|---|---|
| **10 MiB** máx. | `media.services.MAX_UPLOAD_BYTES` | Tamanho máx. de imagem de produto. |
| `image/jpeg, png, webp, gif` | `media.services.ALLOWED_CONTENT_TYPES` | Tipos aceitos. |
| Variantes: `thumbnail 150` · `card 400` · `product 800` · `zoom 1600` (px) | `media.services.VARIANT_MAX_SIZES` | Caixa máx. por variante (mantém proporção). |
| **5 MiB** máx. (assets de template) | `platform_admin.services._MAX_ASSET_BYTES` | Upload de asset no admin da plataforma. |

## 6. Paginação

| Valor | Onde | Significado |
|---|---|---|
| `skip` default `0` | `core/api.pagination_params` | Offset. |
| `limit` default `100`, **máx. `100`** | `core/api.pagination_params` | Itens por página (`1..100`). |

## 7. Enums (status / tipos)

> Valores **persistidos** — alterar é migração. Cada um tem leitura em código (regra "status tem que ter serventia").

| Enum | Arquivo | Valores |
|---|---|---|
| `ProductStatus` | `catalog/enums.py` | `draft`, `published`, `archived` |
| `ProductType` | `catalog/enums.py` | `image`, `image_3d`, `image_3d_customizable` |
| `ProductVariantStatus` | `catalog/enums.py` | `active`, `archived` |
| `CustomizationSessionStatus` | `customization/enums.py` | `draft`, `approved`, `added_to_cart`, `ordered`, `abandoned`, `expired` |
| `CustomizationProductionStatus` | `customization/enums.py` | `received`, `reviewing`, `needs_contact`, `approved_for_production`, `in_production`, `production_done` (eixo de produção no item do pedido, doc [22](./22_product_customization_3d.md)) |
| `OrderStatus` | `orders/enums.py` | `pending_payment`, `paid`, `processing`, `shipped`, `delivered`, `canceled` |
| `CheckoutStatus` | `checkout/enums.py` | `active`, `completed` |
| `CartStatus` | `cart/enums.py` | `active`, `converted` |
| `ShippingMethodType` | `shipping/enums.py` | `fixed_shipping`, `free_shipping`, `local_pickup`, `private_delivery` |
| `CouponType` | `discounts/enums.py` | `percentage`, `fixed` |
| `StoreStatus` | `stores/enums.py` | `draft`, `active`, `paused`, `suspended`, `blocked` |
| `MembershipStatus` | `stores/enums.py` | `invited`, `active`, `removed` |
| `MediaStatus` | `media/enums.py` | `processing`, `ready`, `failed` |
| `MenuLocation` | `content/enums.py` | `header`, `footer` |
| `DomainType` | `domains/enums.py` | `platform_subdomain`, `custom_domain` |
| `DomainStatus` | `domains/enums.py` | `pending`, `active`, `failed`, `blocked` |
| `SslStatus` | `domains/enums.py` | `pending`, `issued`, `failed` |
| `PlatformRole` | `platform_admin/enums.py` | `platform_owner`, `platform_ops`, `platform_finance`, `platform_support`, `platform_catalog` |

**Pagamentos (Fase 8 — planejado, ainda NÃO no código):** valores de referência pra quando os enums forem implementados (`payments/enums.py` ainda não existe).

| Enum (planejado) | Valores |
|---|---|
| `PaymentProvider` | `asaas_baas`, `mercado_pago` (`pagarme` futuro) |
| `PaymentAccountMode` | `native`, `connected` |
| `PaymentAccountStatus` | `pending`, `active`, `blocked`, `rejected` |
| `PaymentStatus` | `created`, `pending`, `authorized`, `paid`, `refused`, `canceled`, `refunded`, `chargeback` |

> **Permissões de loja** (catálogo + mapa papel→permissão) **não** ficam aqui: fonte = [08](./08_modules_and_permissions.md) e `stores/permissions.py`.
