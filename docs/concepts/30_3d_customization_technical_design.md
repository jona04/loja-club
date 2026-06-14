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
| **Área imprimível** | **Região de UV** do modelo (retângulo no espaço UV 0..1). A arte é composta numa textura e **mapeada pela UV do GLB**, então **cola na superfície real** — enrola na caneca, acompanha dobras de tecido, qualquer geometria. **Parametrizada no banco**, **editável no admin** (picker 2D de UV + preview 3D ao vivo); é o mesmo mecanismo que o lojista usa na [Fase 12](../backlog/phase-12-merchant-3d-generation.md). (Engenharia — justificada abaixo.) |
| **Snapshot** | Gerado **no cliente** (canvas → PNG) e enviado como imagem de aprovação. (Engenharia.) |

## 1. Pipeline do asset GLB (o que o dev faz antes do seed)

> **Origem dos GLBs:** os modelos a subir ficam em **`glb-models/`** na raiz do repo (gitignored — binário pesado). A caneca está em `glb-models/ceramic-mug-3d-model.glb`. **Ao subir um novo modelo público, o dev parte dessa pasta.**

O Tripo3D entrega um GLB com **UV automática FRAGMENTADA** — `TEXCOORD_0` preenche 0..1, mas em **ilhas espalhadas** (otimizadas pra bake, não pra uma faixa contínua). Um retângulo de UV nessa UV cai em **pedaços soltos** pela peça. Por isso, pra produtos **cilíndricos** (caneca, garrafa), o pré-processamento **gera uma UV cilíndrica limpa** (`--cylindrical-uv`) que a arte usa. O source **vem sempre em 4K** (texturas 4096²) → **pesado** (~56 MB). Pré-processamento **obrigatório** antes do seed. Checklist para a caneca:

1. **Importar** o GLB de `glb-models/`.
2. **Escala/orientação:** o modelo deve ficar **em pé e centralizado** (Y-up). A caneca do Tripo vem ~0,9 unidade e centrada; se vier torta, endireitar no Tripo (o editor auto-enquadra qualquer escala). A UV cilíndrica assume o eixo no Y.
3. **Pré-processamento (otimização web):** reamostrar texturas **4K → ~1–2K**, `simplify` (a malha; o look branco da cerâmica não denuncia a distorção da UV assada) e **Draco**. Derruba ~56 MB pra ~1–1,5 MB. CLI `gltf-transform`.
4. **Re-unwrap (cilíndrico) pra produtos cilíndricos — `--cylindrical-uv`:** gera uma UV limpa (`u`=ângulo em volta do eixo, `v`=altura) como **2º canal `TEXCOORD_1`**, **preservando** o `TEXCOORD_0` (texturas assadas). A **arte usa o canal 1** → um retângulo de UV vira uma **faixa contínua** colada na superfície. Modelos com unwrap limpo (ex.: tecido desembrulhado no Blender) **não** precisam — usam o `TEXCOORD_0` deles.
5. **Definir a(s) área(s) imprimível(is):** a **região de UV** (no canal usado) onde a arte vai (ver §3). Seed dá o **valor inicial**; **editável no admin** (picker 2D + preview 3D).
6. **Exportar a versão final** — 1 GLB (otimizado/Draco) por versão.
7. **Subir ao CDN da plataforma** sob chave **imutável e versionada** (`public/3d-models/<slug>/v<N>/model.glb`) via `app.core.storage.public_url`.
8. **Seed** de `platform_3d_models` + `platform_3d_model_versions` apontando pra essa URL, com áreas imprimíveis e limites de arte (ver §3 e §8). Mesmo padrão de `seed_content_templates`/`demo_store` — mas aqui o seed dá só o **estado inicial**: a **área imprimível e os limites são editáveis no admin** depois (§3).

> **Versão = imutável.** Trocar o **GLB** **cria uma nova versão** (`v2`), nunca sobrescreve a anterior — sessões/pedidos que fixaram `v1` continuam válidos (ver §7). Já a **área imprimível e os limites** são **editáveis no admin** dentro da versão (são parâmetros, não o arquivo) — ver a regra de edição vs. pedido congelado em §3 e §7.

## 2. Arquitetura do editor (storefront)

### Layout — dois painéis sincronizados

O editor tem **dois painéis lado a lado** que se atualizam **em tempo real**:

- **Painel 2D (área de edição):** a **região imprimível desembrulhada** (o retângulo de UV achatado). É **onde o cliente edita** — arrasta, escala e rotaciona a **imagem** e o **texto**, sempre **dentro** da região. É o WYSIWYG plano.
- **Painel 3D (preview ao vivo):** o modelo (GLB) renderizado com a arte **mapeada pela UV** → ela aparece **na superfície real** (enrola na caneca, acompanha dobras). O cliente **gira/zoom/move** a câmera (`OrbitControls`).
- **Sincronização automática:** a arte do painel 2D é **composta na textura** (na sub-região de UV) e o 3D mostra na hora, **na superfície**. Os dois leem o **mesmo estado** (`state_json`/camadas) — uma fonte só.

```text
┌──────────────────────────┬──────────────────────────┐
│  Painel 2D (UV desembrul.)│   Painel 3D (preview)     │
│  ┌────────────────────┐   │         ___               │
│  │   [ sua arte ]     │   │        (•••) ← arte na    │
│  │    João & Maria    │   │              superfície   │
│  └────────────────────┘   │     girar / zoom / mover  │
│  região de UV imprimível   │   (mapeada pela UV)       │
└──────────────────────────┴──────────────────────────┘
```

> **Responsivo:** em telas pequenas (mobile) os dois painéis **empilham** ou viram **abas** (Editar / Visualizar 3D) — não cabem lado a lado.

### Detalhes técnicos

- **react-three-fiber + drei**, componente **client-only** (`"use client"`), **lazy-loaded** (`next/dynamic`, `ssr: false`) — o editor não entra no bundle da página de produto até o cliente clicar em **Personalizar**.
- **Carregamento do GLB:** `useGLTF` (drei) com **DRACOLoader** apontando o decoder; URL = CDN da versão escolhida. `Suspense` com placeholder enquanto carrega.
- **Camadas (layers):** lista ordenada; cada camada é `image` (raster enviado) ou `text` (renderizada num canvas). Cada camada vive **dentro da região de UV** com transform própria (offset, escala, rotação) + z-order.
- **Aplicação na peça — composição na UV:** todas as camadas são desenhadas num **canvas** posicionado na **sub-região de UV** da área; esse canvas vira a textura (sobreposta ao basecolor, mesma UV do mesh) → o three mapeia pela **UV do GLB** e a arte **cola na superfície real** (curva/dobras). O preview é a **fonte de verdade visual**.
- **Texto:** renderizado num `<canvas>` 2D (conteúdo + fonte + tamanho + cor). **Fontes:** conjunto pequeno e embutido (web-safe + 2–3 display) via `FontFace`; sem upload de fonte na V1.
- **Transform UI:** mover/escalar/rotacionar a camada (handles 2D sobre a região desembrulhada — mantém dentro da área).
- **Autosave:** debounce (~1–2 s) que faz `PUT` do `state_json` na sessão. Restaurável pela `guest_session_id`.
- **Aprovação:** botão habilita só com ≥1 camada válida; ao aprovar, o editor **gera o snapshot** (§5) e chama o endpoint de aprovar.

## 3. Representação da área imprimível

Cada **versão do modelo** define 1+ **áreas imprimíveis**. Cada área é uma **região do espaço UV** do modelo (um retângulo em UV 0..1). Para a caneca, **1 área**. Guardada no banco em `platform_3d_model_versions`, **editável no admin** — o seed só dá o valor inicial:

```jsonc
{
  "id": "front",
  "label": "Frente",
  "uv_rect": { "u0": 0.05, "v0": 0.3, "u1": 0.95, "v1": 0.7 },  // retângulo no espaço UV (0..1)
  "max_layers": 5
}
```

- A arte é composta na **sub-região de UV** da textura; o **mesh usa essa UV** → a arte **cola na superfície real** (enrola na caneca, acompanha dobras de tecido, qualquer geometria). É o jeito certo de aplicar imagem em superfície arbitrária.
- No admin, o **picker 2D** mostra o espaço UV (0..1) com o retângulo **arrastável/redimensionável**; o **preview 3D** mostra a região na superfície **ao vivo** (acompanhando a curvatura). O admin ajusta até cobrir a faixa desejada.
- O picker 2D é **proporcional à superfície desembrulhada** (não quadrado): o preview 3D mede a geometria e devolve o **aspecto** (largura/altura) — pra um cilindro, `circunferência ÷ altura` (`2πr ÷ h`, `r` = raio mediano em XZ, `h` = vão em Y). Assim a região imprimível aparece nas proporções reais (a faixa de uma caneca é bem mais larga que alta) e o lojista enxerga o formato verdadeiro da arte.

**Por que UV e não projeção (em linguagem simples):** uma projeção plana/cilíndrica é uma **aproximação** — ela "flutua" e não cola em superfície curva/ondulada arbitrária (um tecido com dobras desliza). As **coordenadas UV** do modelo dizem, pra cada ponto da malha, qual ponto da textura fica ali; com elas a arte **segue a superfície real**. É exatamente pra isso que as UVs existem.

> **Requisito — uma UV LIMPA** (onde um retângulo de UV = uma faixa **contígua**). A UV automática do Tripo é **fragmentada** (ilhas espalhadas) → não serve. Soluções: **(a) produtos cilíndricos** (caneca, garrafa) → o pré-processamento gera uma **UV cilíndrica limpa** (`--cylindrical-uv`, §1) num 2º canal; **(b) outros** → unwrap limpo no **Blender** (ou a UV própria do modelo, se boa). **Atenção:** auto-unwrap genérico (`xatlas`) re-empacota em ilhas — **fragmenta de novo**, não dá faixa contígua.
>
> **Editar a área x pedido congelado:** editar a `uv_rect` afeta **sessões novas**. Pedidos/itens já aprovados **não mudam** — guardam o **snapshot** (§5) e o `state_json` (§7). A **mesma ferramenta de mapeamento** (picker 2D + preview 3D) é a que o lojista usa na **[Fase 12](../backlog/phase-12-merchant-3d-generation.md)**.

### 3.1 Compositor — renderização da arte (sem distorção)

O editor compõe as camadas (imagem/texto) **num único "espaço físico de arte"**: um canvas cuja proporção (`w/h`) é a **proporção real** da região imprimível — `regionAspect = (Δu/Δv) × unwrapAspect`, onde `unwrapAspect = 2πr/h` (§3). Esse render é a **fonte única**:
- **Painel 2D** mostra o espaço físico **direto** → o que o cliente vê é fiel.
- **3D** desenha esse mesmo canvas na **sub-região de UV** (a textura é quadrada, `EDITOR_TEXTURE_SIZE`): `drawImage(art, u0·TEX, v0·TEX, Δu·TEX, Δv·TEX)`. A textura quadrada "comprime" a arte na horizontal, e a **UV cilíndrica desfaz** essa compressão na superfície → **sem distorção** e **idêntico ao 2D**.
- **Imagem:** mantém o **aspecto natural** por padrão (`largura = scale·w`, `altura = largura·(imgH/imgW)`). Distorcer é **opt-in**: um botão "Distorcer" libera `scale_y` (largura/altura independentes) — começa no valor natural pra não dar salto.
- **Texto:** renderizado no espaço físico (sem esticar); fonte de um conjunto fechado; cai num stack `sans-serif` se a fonte não estiver carregada.
- **Cor:** o overlay 3D usa `CanvasTexture` com `colorSpace = sRGB` — sem isso as cores saem diferentes do painel 2D. Com isso, **a cor no 2D e no 3D batem**.
- **Composite de produção (§5):** é exatamente esse render do espaço físico, em **alta resolução** (`COMPOSITE_WIDTH`, [31 §4](./31_configuration_and_constants.md)) — o retângulo achatado que a gráfica usa.

> Constantes (`EDITOR_TEXTURE_SIZE`, `COMPOSITE_WIDTH`, autosave) em [31 §4](./31_configuration_and_constants.md). Implementação: `frontend-storefront/lib/customizer/{compose,aspect}.ts`.

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

- `transform.x/y` = **centro** da camada em coordenadas normalizadas da região (não pixels) — independem da resolução de tela. **Podem sair de [0..1]** quando a camada é maior que a região (é "paneada" até a borda encostar, §3.1); o backend só **limita a um teto de sanidade** (`_MAX_TRANSFORM`, [31 §4](./31_configuration_and_constants.md)) — a contenção exata é do cliente e o composite recorta.
- `transform.scale` = largura (fração da largura da região); `transform.scale_y?` = altura livre (distorção opt-in; ausente = aspecto natural).
- `font` e os limites são **validados contra a versão** no backend (não confiar no cliente).
- Mudar o `schema_version` exige migração/compat — pedidos antigos guardam o schema com que foram criados.

## 5. Snapshot e preview de aprovação

**O que é "snapshot no cliente" (em linguagem simples):** o editor 3D roda **no navegador do cliente** desenhando a cena 3D num `<canvas>`. "Snapshot no cliente" = quando o cliente clica em **Aprovar**, o próprio navegador **tira uma foto** desse canvas (a cena exatamente como está na tela) e gera um **PNG** — sem o servidor precisar re-renderizar o 3D. Esse PNG é a **"arte aprovada"**: é o que o lojista vê no pedido e o que fica **congelado**. A alternativa seria o **servidor** abrir o 3D e renderizar a imagem ("render no servidor/headless") — mais robusto, porém bem mais complexo (precisa de GPU/headless browser); por isso a V1 tira a foto no cliente.

A aprovação gera e envia **dois PNGs obrigatórios** (ambos **privados**, por `store_id`):
- **Snapshot** = a "foto" do canvas 3D (`gl.domElement.toDataURL('image/png')`, com `preserveDrawingBuffer`). É o **mockup** — mostra a caneca personalizada de um ângulo. Usado pra o cliente reconhecer o item (inclusive **a imagem da linha do carrinho** é o snapshot, pra distinguir 2 personalizações do mesmo produto) e pro lojista ver no pedido.
- **Composite** = o **retângulo achatado** da área imprimível, renderizado no espaço físico (§3.1) em **alta resolução** (`COMPOSITE_WIDTH`). É a **arte de produção** (o que vai pra gráfica) — qualidade independente da tela, mostra a área inteira (não só um lado).
- Os dois saem do **mesmo compositor** do editor (sem fila): o navegador renderiza, anexa no `approve` (multipart). **Se um falhar (canvas "tainted"/OOM), o approve falha** → garante que foi enviado; bloqueia e oferece retry; nunca aprova sem os dois.
- O snapshot é capturado com **`toDataURL`** sobre um canvas com `preserveDrawingBuffer` (leitura confiável entre drivers — a prévia de produção não pode falhar silenciosamente). O composite tem **fundo transparente** (PNG com alpha) — só a arte, pronto pra impressão.
- **Envio com progresso + limites:** o upload de arte (≤ 30 MB por imagem) e a aprovação (snapshot + composite) vão por **Route Handlers** (`app/api/customizer/*`) chamados via **XHR**, que reporta **progresso real** (%, tamanho, velocidade, tempo restante) — Server Action não reporta progresso. O Route Handler repassa host + cookie de convidado ao backend (igual à Server Action). O editor **mostra o limite por imagem** e **barra antes de enviar** se a imagem ou o payload de aprovação (≤ 48 MB) passar do teto ([31 §4](./31_configuration_and_constants.md)). O composite é **uma única imagem achatada** (não a soma dos uploads), então mais camadas **não** somam tamanho indefinidamente. O `serverActions.bodySizeLimit` (default **1 MB**) fica em **50 MB** como folga geral.
- Re-render **server-side/headless** em altíssima fidelidade (fila) é follow-up; a V1 gera no cliente.

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
| **Snapshot** (mockup 3D) | **Privado** | idem; ao virar pedido, **copiado** pra `private/<store_id>/orders/<order_id>/...` (§7). Também é a imagem da linha no carrinho. |
| **Composite** (arte de produção, §5) | **Privado** | `private/<store_id>/customizations/<session_id>/composite-*.png`; copiado pra `.../orders/...` no congelamento. **Não** público (é o design do cliente). |

- **Validação de upload:** mime `image/png`/`image/jpeg`; tamanho máx. (ex.: **15 MB**); dimensão mínima → **aviso** de baixa resolução (não bloqueia). **Sanitização real:** o backend **re-encoda** a imagem (PIL) → remove EXIF/metadados (foto do cliente pode ter GPS) e valida; o snapshot/composite idem.
- **Nunca** expor o arquivo original em URL pública permanente. Auditar acesso do lojista (doc [14](./14_security_strategy.md)).
- Tudo separado por `store_id` (mixin de scoping); sessão/upload/cart/order item carregam `store_id`.

> **CORS no CDN (obrigatório pro 3D):** o GLB é carregado pelo `three.js` via **fetch cross-origin** (admin e vitrine → CloudFront), então o CDN **precisa** devolver `Access-Control-Allow-Origin` — senão o navegador bloqueia (`NetworkError`). Solução: response-headers-policy **`SimpleCORS`** na distribuição (+ invalidar o cache ao ligar). Configurado no dev; **reproduzir no provisionamento de produção**.

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
- **`customization_sessions`**: campos do doc 07 + `state_json` (§4), `platform_3d_model_version_id`, `status`, `guest_session_id`, `customer_id?`, `created_by_user_id?` (usuário da loja na assistida), `snapshot_key?`, `approved_at?`, `expires_at`, `public_token?` (§9).
- **`customization_uploads`**: `customization_session_id`, `store_id`, `key` (privado), `mime`, `size_bytes`, `width`/`height`.
- **`customization_cart_items`** / **`customization_order_items`**: cópia congelada (§7).

> Se algum campo acima **não** estiver no doc 07 ao implementar, **atualizar o 07** junto (não divergir).

## 9. Personalização assistida + link público

- O lojista cria a sessão com `created_by` = usuário da loja, pré-cadastrando o cliente por contato (`create_or_update_customer`, normaliza e-mail/telefone — Fase 6).
- A sessão ganha um **`public_token`** opaco e inadivinhável (`secrets.token_urlsafe`), expirável pelo `expires_at` da sessão (escopo = aquela sessão, **read-only**). O link `/p/<token>` abre a personalização **sem login** — o cliente vê e **compartilha**.
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
- **UV ruim/distorcida** (unwrap fraco) → arte distorcida na superfície: mitigado **preservando a UV** no preprocess (decimate conservador) e, pra modelos sem UV boa, **auto-unwrap**; o preview é a verdade.
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
