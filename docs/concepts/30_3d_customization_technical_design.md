# Design Técnico — Personalização 3D (Fase 7)

> **O que é este doc.** O doc [22](./22_product_customization_3d.md) descreve a **experiência** (personalizar → aprovar → carrinho → congelar no pedido). Este doc fixa o **contrato técnico** que a Fase 7 vai implementar: como o GLB é preparado, como a **área imprimível** é representada, a arquitetura do **editor 3D**, o **`state_json`** que vai e volta do editor e congela no pedido, o **snapshot** de aprovação, **storage/segurança** dos assets e o **link público** da personalização assistida. As tabelas estão no doc [07](./07_database_strategy.md); aqui detalho os campos que a Fase 7 precisa.
>
> Regra de ouro: o código imita este doc. Se uma limitação técnica obrigar a divergir, **atualiza-se este doc** — nunca deixar doc e código divergentes.

## Decisões fechadas (entrada da Fase 7)

| Tema | Decisão |
|---|---|
| **Primeiro modelo** | **Caneca branca de cerâmica** (GLB já gerado no Tripo3D). A Fase 7 entra com **1 modelo**; outros (camiseta, ecobag…) entram depois pelo mesmo seed. |
| **Escopo do editor** | **Imagem + transform + camadas de texto.** O cliente envia 1+ imagens e adiciona texto, e posiciona/escala/rotaciona cada camada dentro da área imprimível. **Sem troca de cor do produto na V1** (a caneca branca fica branca) — recolor é follow-up (§12). |
| **Arte aceita** | **Só raster: PNG/JPG** (vetor/SVG e PDF ficam como follow-up — ver Fora de escopo). |
| **Personalização assistida** | **Link público compartilhável** pra ver; **aprovar/comprar pede confirmação de contato** (e-mail/telefone), **sem conta** (a conta do cliente é a Fase 8). |
| **Lib do editor** | **react-three-fiber** (`@react-three/fiber`) + **`@react-three/drei`**, componente client-only no storefront Next.js, carregado sob demanda. (Engenharia — justificada abaixo.) |
| **Área imprimível** | **Decal projetado sobre o mesh** (projetor com retângulo limitado), **não** dependente da UV do GLB. **Parametrizada e guardada no banco** (não hardcoded) — **editável no admin** dos modelos 3D públicos; é o **mesmo mecanismo de mapeamento** que o lojista vai usar na Fase 12 pro próprio GLB. (Engenharia — justificada abaixo.) |
| **Snapshot** | Gerado **no cliente** (canvas → PNG) e enviado como imagem de aprovação. (Engenharia.) |

## 1. Pipeline do asset GLB (o que o dev faz antes do seed)

> **Origem dos GLBs:** os modelos a subir ficam em **`glb-models/`** na raiz do repo (gitignored — binário pesado). A caneca está em `glb-models/ceramic-mug-3d-model.glb`. **Ao subir um novo modelo público, o dev parte dessa pasta.**

O Tripo3D entrega um GLB com **topologia/UV automáticas** — bom pra visualização, **não confiável** pra mapear área de impressão por UV. Além disso o source **vem sempre em 4K** (texturas 4096²) → **pesado** (a caneca crua tem ~56 MB, longe de web-ready). Por isso **todo GLB passa por um pré-processamento obrigatório** antes de virar seed. Checklist para a caneca:

1. **Importar** o GLB do Tripo no Blender.
2. **Escala real e orientação:** dimensionar pro tamanho físico (caneca ≈ 9,5 cm de altura, ø ≈ 8 cm), **Y-up**, origem na base, centralizada em XZ. A escala real importa pro aviso de baixa resolução (DPI) e pra proporção do decal.
3. **Pré-processamento (otimização web — obrigatório, o gate da pipeline):** o source 4K precisa virar web-ready **antes** do resto — reamostrar texturas **4K → ~1–2K**, **reduzir geometria** (decimate, **< ~150k triângulos**) e aplicar **Draco**. Derruba os ~56 MB pra **poucos MB**. **Automatizável por CLI (`gltf-transform`)**, sem Blender; só o passo 5 (área imprimível) é manual/visual.
4. **Materiais limpos:** a superfície cerâmica fica com seu **material branco** (a V1 **não** troca a cor do produto). Um material **nomeado** pra superfície só será necessário quando o recolor voltar (follow-up, §12).
5. **Definir a(s) área(s) imprimível(is):** um **projetor planar** em espaço-modelo cobrindo a faixa frontal da caneca (o "wrap" onde a arte vai). Guardar a **transform do projetor** + o **tamanho do retângulo em cm** + a **proporção** no banco (ver §3). O seed só dá o **valor inicial**; depois isso é **editável no admin** (§3).
6. **Exportar a versão final** — 1 GLB (já otimizado/Draco do passo 3) por versão.
7. **Subir ao CDN da plataforma** sob chave **imutável e versionada** (`public/3d-models/<slug>/v<N>/model.glb`) via `app.core.storage.public_url`.
8. **Seed** de `platform_3d_models` + `platform_3d_model_versions` apontando pra essa URL, com áreas imprimíveis e limites de arte (ver §3 e §8). Mesmo padrão de `seed_content_templates`/`demo_store` — mas aqui o seed dá só o **estado inicial**: a **área imprimível e os limites são editáveis no admin** depois (§3).

> **Versão = imutável.** Trocar o **GLB** **cria uma nova versão** (`v2`), nunca sobrescreve a anterior — sessões/pedidos que fixaram `v1` continuam válidos (ver §7). Já a **área imprimível e os limites** são **editáveis no admin** dentro da versão (são parâmetros, não o arquivo) — ver a regra de edição vs. pedido congelado em §3 e §7.

## 2. Arquitetura do editor (storefront)

### Layout — dois painéis sincronizados

O editor tem **dois painéis lado a lado** que se atualizam **em tempo real**:

- **Painel 2D (área de edição):** um **retângulo plano** com a proporção da área imprimível (no caso da caneca, a faixa frontal). É **onde o cliente edita** — arrasta, escala e rotaciona a **imagem** e o **texto**, sempre **dentro** do retângulo (nada vaza pros lados/fundo). É o WYSIWYG plano, fácil de posicionar com precisão.
- **Painel 3D (preview ao vivo):** a **caneca (GLB)** renderizada; o cliente **gira** (orbit), **dá zoom** e **move** (pan) pra ver de todos os ângulos. Usa `OrbitControls` (drei): arrastar = rotacionar · scroll/pinça = **zoom** · botão direito / dois dedos = mover.
- **Sincronização automática:** qualquer mudança no painel 2D **aplica na hora** o decal sobre a caneca 3D. Os dois painéis leem o **mesmo estado** (`state_json`/camadas) — uma fonte só, sem cópia divergente. O 3D é só **visualização** (girar/zoom/mover a câmera); a **edição** acontece no retângulo 2D.

```text
┌──────────────────────────┬──────────────────────────┐
│   Painel 2D (editar)      │   Painel 3D (preview)     │
│  ┌────────────────────┐   │         ___               │
│  │   [ sua arte ]     │   │        (   )  ← caneca    │
│  │    João & Maria    │   │     girar / zoom / mover  │
│  └────────────────────┘   │                           │
│  retângulo = área          │   OrbitControls (câmera)  │
└──────────────────────────┴──────────────────────────┘
```

> **Responsivo:** em telas pequenas (mobile) os dois painéis **empilham** ou viram **abas** (Editar / Visualizar 3D) — não cabem lado a lado.

### Detalhes técnicos

- **react-three-fiber + drei**, componente **client-only** (`"use client"`), **lazy-loaded** (`next/dynamic`, `ssr: false`) — o editor não entra no bundle da página de produto até o cliente clicar em **Personalizar**.
- **Carregamento do GLB:** `useGLTF` (drei) com **DRACOLoader** apontando o decoder; URL = CDN da versão escolhida. `Suspense` com placeholder enquanto carrega.
- **Camadas (layers):** lista ordenada; cada camada é `image` (textura raster enviada) ou `text` (renderizada num canvas → textura). Cada camada vive **dentro de uma área imprimível** e tem transform própria (offset, escala, rotação) + z-order.
- **Aplicação na peça — decal:** cada camada vira um **decal** projetado sobre o mesh da área (via projetor da versão; `DecalGeometry`/material com a textura da camada). O preview renderizado é a **fonte de verdade visual** (o que o cliente vê é o que ele aprova).
- **Texto:** renderizado num `<canvas>` 2D (conteúdo + fonte + tamanho + cor) → `CanvasTexture` → vira camada decal como uma imagem. **Fontes:** conjunto pequeno e embutido (web-safe + 2–3 display) carregado via `FontFace`; sem upload de fonte na V1.
- **Transform UI:** mover/escalar/rotacionar a camada selecionada (handles 2D sobre a área, não gizmo 3D livre — mantém dentro do retângulo imprimível).
- **Autosave:** debounce (~1–2 s) que faz `PUT` do `state_json` na sessão. Restaurável pela `guest_session_id`.
- **Aprovação:** botão habilita só com ≥1 camada válida; ao aprovar, o editor **gera o snapshot** (§5) e chama o endpoint de aprovar.

## 3. Representação da área imprimível

Cada **versão do modelo** define 1+ **áreas imprimíveis**. Para a caneca, **1 área** (faixa frontal). A estrutura é **guardada no banco** em `platform_3d_model_versions` (não hardcoded) e é **editável no admin** — o seed só dá o valor inicial:

```jsonc
{
  "id": "front",
  "label": "Frente",
  "target_mesh": "body",        // mesh onde o decal é projetado
  "projector": {                 // espaço-modelo (metros, Y-up)
    "position": [0, 0.05, 0.041],
    "normal":   [0, 0, 1],       // direção da projeção
    "up":       [0, 1, 0],
    "size_m":   [0.18, 0.085]    // largura x altura do retângulo no mundo
  },
  "size_cm":      [18.0, 8.5],   // mesma área em cm → DPI/aviso de resolução
  "aspect_ratio": 2.1,           // guia de proporção recomendada
  "max_layers":   5
}
```

- O **decal** projeta a textura da camada sobre `target_mesh` usando `projector`; o retângulo limita a área (nada "vaza" pra fora).
- `size_cm` + a resolução da imagem enviada ⇒ **DPI estimado** ⇒ **aviso de baixa resolução** (não bloqueia, só avisa).
- A proporção é **guia**, não trava: o cliente pode escalar dentro do limite.

**O que é um "decal" projetado (em linguagem simples):** é como um **carimbo/adesivo** que a gente "projeta" sobre a superfície da peça. Imagine apontar um projetor pra frente da caneca: a imagem da arte é jogada na superfície curva e "gruda" nela, acompanhando a curvatura. O `projector` (posição, direção, tamanho) diz **de onde** e **com que tamanho** esse carimbo é projetado; o retângulo limita pra arte não vazar pros lados/fundo. Vantagem: funciona em **qualquer** formato de malha sem depender da UV (o "mapa plano" do modelo), que no GLB do Tripo vem automática e bagunçada.

> **Por que decal e não UV:** a UV do Tripo é automática e imprevisível; depender dela quebraria a cada novo asset. O projetor é definido pelo dev (valor inicial no seed) e ajustável no admin, e é robusto a qualquer topologia. Custo: leve distorção em superfícies muito curvas — mitigado pelo preparo no Blender e pelo retângulo limitado; o **preview é a verdade**. **Vamos validar na caneca real** antes de fechar (se o resultado não ficar bom, a alternativa é uma região de UV dedicada feita no Blender).

> **Editável no admin (e seam da Fase 12):** os parâmetros da área (`projector`, `size_cm`, `aspect_ratio`, `max_layers`) e os `art_limits` são **editados por uma ferramenta visual no admin** dos modelos 3D públicos — o dev semeia o inicial, mas dá pra **refinar sem novo deploy**. Essa **mesma ferramenta de mapear a área** é a que o **lojista** vai usar na **[Fase 12](../backlog/phase-12-merchant-3d-generation.md)** pra mapear o GLB que ele mesmo gerar — por isso ela nasce genérica desde a Fase 7.
>
> **Editar a área x pedido congelado:** editar os parâmetros afeta **sessões novas**. Pedidos/itens já aprovados **não mudam** — eles guardam o **snapshot** (a imagem aprovada, §5) e o `state_json` (§7); a edição da área não re-renderiza nada que já foi congelado.

## 4. `state_json` — o contrato que vai/volta/congela

Estado único, versionado por schema, suficiente pra **restaurar o editor**, **renderizar o preview** e **congelar no pedido** sem depender da sessão viva:

```jsonc
{
  "schema_version": 1,
  "model": { "model_id": "...", "version_id": "..." },  // versão fixada
  "layers": [
    {
      "id": "l1",
      "kind": "image",
      "area_id": "front",
      "upload_id": "...",            // referência ao customization_uploads (privado)
      "transform": { "x": 0.5, "y": 0.5, "scale": 0.8, "rotation_deg": 0 },
      "z": 0
    },
    {
      "id": "l2",
      "kind": "text",
      "area_id": "front",
      "text": "João & Maria",
      "font": "inter",               // de um conjunto fechado
      "font_size": 48,
      "color": "#222222",
      "transform": { "x": 0.5, "y": 0.85, "scale": 1.0, "rotation_deg": 0 },
      "z": 1
    }
  ]
}
```

- `transform.x/y` são **normalizados [0..1] dentro da área** (não pixels) — independem da resolução de tela.
- `font` e os limites são **validados contra a versão** no backend (não confiar no cliente).
- Mudar o `schema_version` exige migração/compat — pedidos antigos guardam o schema com que foram criados.

## 5. Snapshot e preview de aprovação

**O que é "snapshot no cliente" (em linguagem simples):** o editor 3D roda **no navegador do cliente** desenhando a cena 3D num `<canvas>`. "Snapshot no cliente" = quando o cliente clica em **Aprovar**, o próprio navegador **tira uma foto** desse canvas (a cena exatamente como está na tela) e gera um **PNG** — sem o servidor precisar re-renderizar o 3D. Esse PNG é a **"arte aprovada"**: é o que o lojista vê no pedido e o que fica **congelado**. A alternativa seria o **servidor** abrir o 3D e renderizar a imagem ("render no servidor/headless") — mais robusto, porém bem mais complexo (precisa de GPU/headless browser); por isso a V1 tira a foto no cliente.

- Ao aprovar, o editor renderiza a cena num canvas e faz **`toDataURL('image/png')`** (a "foto" do canvas) → **1 snapshot frontal obrigatório** (a "arte aprovada"). Opcionalmente um segundo ângulo (3/4) pra ajudar o lojista.
- O snapshot é **enviado** e guardado como **privado** (chave por `store_id`), junto do `state_json` e da `version_id`.
- **A aprovação só conclui com snapshot gerado** — se a geração falhar (canvas "tainted", OOM), bloqueia e oferece retry; nunca aprovar sem snapshot.

## 6. Storage e segurança

**Convenção de chaves (top-level `public/` vs `private/`):**

```text
public/3d-models/<slug>/v<N>/model.glb          # GLB do catálogo (CDN, imutável)
private/<store_id>/customizations/<session_id>/<file>   # arte enviada + snapshot da sessão
private/<store_id>/orders/<order_id>/<file>     # cópia congelada (arte/snapshot) no pedido
```

O split `public/` × `private/` é **top-level** (o `public/` já é a convenção do storage hoje — ex.: `public/templates/...`); o `private/` entra agora, sempre **prefixado por `store_id`** (isolamento por loja).

| Asset | Visibilidade | Como |
|---|---|---|
| **GLB do catálogo** (plataforma) | **Público (CDN)**, imutável, versionado | `public/3d-models/<slug>/v<N>/model.glb` via `public_url` |
| **Arte enviada pelo cliente** | **Privado** | `private/<store_id>/customizations/<session_id>/...`; **URL assinada** (`generate_presigned_url`) só pro editor/lojista |
| **Snapshot/preview** | **Privado** | idem; ao virar pedido, **copiado** pra `private/<store_id>/orders/<order_id>/...` (§7) |

- **Validação de upload:** mime `image/png`/`image/jpeg`; tamanho máx. (ex.: **15 MB**); dimensão mínima → **aviso** de baixa resolução (não bloqueia). Sanitizar (strip de metadados).
- **Nunca** expor o arquivo original em URL pública permanente. Auditar acesso do lojista (doc [14](./14_security_strategy.md)).
- Tudo separado por `store_id` (mixin de scoping); sessão/upload/cart/order item carregam `store_id`.

## 7. Versionamento e congelamento no pedido (INV-P5)

- A **sessão** referencia `platform_3d_model_version_id` (a versão que o cliente está usando).
- Ao **criar o pedido**, copiar pra `customization_order_items`: o **`state_json` inteiro** + a **`version_id`** + a **chave do snapshot** (copiado pra uma chave do pedido) + a referência dos uploads. O pedido **não depende da sessão viva**.
- Alterar a sessão depois **não muda** um pedido já criado. Re-seed do modelo (nova versão) **não muda** pedidos que fixaram a versão anterior.
- O gate de carrinho já existe: [`assert_addable_to_cart(product, has_approved_customization=...)`](../../backend/app/modules/catalog/services.py) — na Fase 7 o carrinho passa `True` quando há sessão `approved` vinculada ao item.

## 8. Campos que a Fase 7 precisa nas tabelas (sobre o doc 07)

As tabelas já estão nomeadas no doc [07](./07_database_strategy.md). O design acima exige, em concreto:

- **`platform_3d_models`** (sem `store_id`): `name`, `category`, `slug`, `is_active`, soft delete.
- **`platform_3d_model_versions`**: `model_id` (FK), `version` (int), `glb_url` (CDN), `printable_areas` (JSON, §3), `text_config` (JSON: fontes permitidas, tamanho min/máx), `art_limits` (JSON: mimes, tamanho máx, dimensão mín), `is_active`. *(Recolor é follow-up: quando voltar, entra `color_palette` aqui — §12.)*
- **`customization_product_settings`** (por loja): `product_id` → `platform_3d_model_id` (escolhido do catálogo) + observações de produção.
- **`customization_sessions`**: campos do doc 07 + `state_json` (§4), `platform_3d_model_version_id`, `status`, `guest_session_id`, `customer_id?`, `created_by?` (usuário da loja na assistida), `snapshot_key?`, `expires_at`, `public_token?` (§9).
- **`customization_uploads`**: `customization_session_id`, `store_id`, `key` (privado), `mime`, `size_bytes`, `width`/`height`.
- **`customization_cart_items`** / **`customization_order_items`**: cópia congelada (§7).

> Se algum campo acima **não** estiver no doc 07 ao implementar, **atualizar o 07** junto (não divergir).

## 9. Personalização assistida + link público

- O lojista cria a sessão com `created_by` = usuário da loja, pré-cadastrando o cliente por contato (`create_or_update_customer`, normaliza e-mail/telefone — Fase 6).
- A sessão ganha um **`public_token`** assinado e expirável (escopo = aquela sessão, **read-only**). O link `/p/<token>` abre a personalização **sem login** — o cliente vê e **compartilha**.
- **Aprovar/comprar** pelo link exige **confirmar o contato** (digitar o e-mail/telefone pré-cadastrado) — sem conta (a conta é Fase 8). Confirmado o contato, segue o fluxo normal (carrinho/checkout) pelas mesmas regras de aprovação/congelamento.
- O token **não** expõe arquivos originais por URL pública permanente — o preview vem por URL assinada de curta duração.

## 10. Performance (doc 13)

- **Draco** no GLB; `useGLTF.preload` ao focar o produto; editor **lazy** (não pesa a página de produto).
- Cap de textura (ex.: reamostrar a arte enviada pra ≤ 2048 px no maior lado antes de virar textura).
- Mobile: limitar pixel ratio do renderer; `dispose` de texturas/geometrias ao trocar de camada/fechar o editor.

## 11. Modos de falha / edge cases (vira follow-up/teste na Fase 7)

- **GLB não carrega / WebGL indisponível:** cair pro fallback de imagens do produto + aviso; botão Personalizar desabilitado com explicação.
- **Upload inválido** (tipo/tamanho): `422`. **Baixa resolução:** avisa, não bloqueia.
- **Falha ao gerar snapshot:** bloqueia a aprovação com retry; nunca aprovar sem snapshot.
- **Sessão expirada (30 dias) no meio da edição:** autosave responde "expirada"; o editor oferece **clonar** num rascunho novo.
- **Duas abas na mesma sessão:** autosave é **last-write-wins** (aceitável na V1).
- **Decal distorcido** em malha muito curva/Tripo: mitigado no preparo (Blender) + retângulo limitado; o preview é a verdade.
- **Glifo ausente** na fonte embutida: fonte de fallback + aviso.
- **Pedido x sessão:** o snapshot é **copiado** pra chave do pedido no congelamento — apagar a sessão depois não quebra o pedido.

## 12. Fora de escopo da Fase 7 (follow-up / outra fase)

- **Múltiplas faces / múltiplas áreas** além da frontal da caneca (o schema suporta N áreas; camiseta frente/verso entra quando o modelo entrar).
- **Troca de cor do produto (recolor):** a caneca branca fica **branca** na V1. Quando voltar, precisa de **paleta curada** (`color_palette` na versão) + **material nomeado** na superfície do GLB + o **seletor de cor** no editor.
- **Arte vetorial (SVG) e PDF** (grau gráfico) — follow-up; pesa pra gráficas.
- **Render server-side/headless** do snapshot — V1 é client-side.
- **Geração de arte por IA.**
- **Lojista gerar o próprio GLB via API** (Meshy/Tripo/Hyper3D) + mapear a área pelo painel → **[Fase 12](../backlog/phase-12-merchant-3d-generation.md)**.
- **Restringir personalização a plano pago** → **Fase 8**.
- **Conta/login do cliente** (a assistida na Fase 7 usa confirmação de contato, não conta) → **Fase 8**.
