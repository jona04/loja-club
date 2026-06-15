---
id: P7-EDITOR-02
title: Editor — camadas (imagem+texto) + decal + aprovação + snapshot + link público
phase: 7
etapa: "Etapa 5 — Editor 3D no storefront (react-three-fiber)"
area: EDITOR
status: done
depends_on: [P7-EDITOR-01]
blocks: [P7-ORD-01]
tests: [unit]
---

# P7-EDITOR-02 — Camadas, decal, aprovação, snapshot e link público

## Contexto
O **conteúdo** do editor: aplicar **imagem** e **texto** como camadas (decal) dentro da área, a **aprovação** obrigatória com **snapshot client-side**, e a **visão pública read-only** (link da assistida) com aprovação por confirmação de contato.

## Docs de referência
- [30 — §2 Camadas/decal / §4 state_json / §5 Snapshot / §9 Link público](../../concepts/30_3d_customization_technical_design.md)

## Escopo (o que ENTRA)
> A arte é **composta numa textura na região de UV** da área e **mapeada pela UV do GLB** → cola na superfície real (enrola na caneca, acompanha dobras). Não é projeção (doc [30 §3](../../concepts/30_3d_customization_technical_design.md)).
- **Camada imagem:** upload raster (PNG/JPG) → composta na **região de UV**; transform (mover/escalar/rotacionar) **dentro da região**; z-order.
- **Camada texto:** conteúdo + **fonte** (conjunto fechado) + **cor do texto** + tamanho → canvas → composto na **região de UV**.
- **Aprovação:** habilita com ≥1 camada válida; **gera o snapshot** (canvas → PNG, doc [30 §5](../../concepts/30_3d_customization_technical_design.md)) → envia + chama `aprovar` (`P7-SESS-01`).
- **Link público read-only** (`/p/<token>`): reusa o editor em modo leitura; **aprovar** pede **confirmação de contato** (sem conta).

## Fora de escopo (o que NÃO entra)
- **Cor do produto** (recolor): fora da V1 (a cor aqui é do **texto**).
- **SVG/PDF**: só raster na V1.
- Congelar no pedido: `P7-ORD-01`. Montar a assistida (lado lojista): `P7-OPS-01`.

## Arquivos a criar/alterar
- `frontend-storefront/...` (alterar) — camadas (imagem/texto), decal, handles 2D, painel de aprovação, geração de snapshot.
- `frontend-storefront/app/p/[token]/...` (criar) — visão pública read-only + aprovar por contato.

## Passos
1. Camada imagem (upload → decal + transform na área).
2. Camada texto (canvas→textura → decal; fonte/cor/tamanho).
3. Aprovação + **snapshot** client-side → enviar/aprovar.
4. Visão pública `/p/<token>` (read-only) + aprovar por confirmação de contato.

## Testes
- **Níveis:** unit (vitest).
- **Quando escrever:** durante.
- **Cobrir:** unit — adicionar imagem/texto atualiza o `state_json`; aprovação bloqueada sem camada/snapshot; transform fica **dentro** da área; visão pública é read-only e aprovar exige contato.

## Definition of Done
- [x] Cliente aplica imagem + texto, aprova com snapshot; link público abre read-only e aprova por contato.
- [x] **Modos de falha mapeados** — **snapshot falha/canvas tainted** → `try/catch` bloqueia a aprovação + mostra retry (não aprova sem snapshot); **glifo/fonte ausente** → canvas cai no stack `sans-serif`; arte inválida/tamanho → erro do backend (`P7-SESS-01`); GLB/WebGL indisponível → fallback (herdado do `P7-EDITOR-01`). → tratados.
- [x] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- A **cor** no editor é só a **cor do texto** (camada). A cor **do produto** (recolor) é follow-up.
- **Composição na UV (base do admin, reescrita no storefront):** as camadas são desenhadas num canvas (`lib/customizer/compose.renderArt`) no espaço físico da área (§3.1) e o canvas vira `CanvasTexture` no **canal `TEXCOORD_1`** (cilíndrico limpo) de um overlay que compartilha a geometria → a arte **cola na superfície** (não projeção). Mesmo compositor pinta o painel 2D (região inteira) e a textura 3D — uma fonte de verdade. **Sem chamar o admin** (frontends separados): o storefront fala só com `/storefront/*`.
- **UX resolvida agora (não adiada):** painel 2D **proporcional à superfície real** (`computeUnwrapAspect` × proporção da `uv_rect` = `regionAspect`), então a arte tem o formato certo (caneca ~2:1); arrastar a camada selecionada **clampa** o centro em [0,1] (fica dentro da área).
- **Segurança resolvida agora (não adiada):** todo upload é **re-encodado** no backend (`_sanitize_image`, PIL) → **remove EXIF/metadados** (foto do cliente pode ter GPS) e valida; o snapshot idem. Imagens carregadas com `crossOrigin` pra não "tingir" o canvas (senão o `toDataURL` falha).
- **Aprovação:** habilita com **≥1 camada** + snapshot; o backend **também exige ≥1 camada** (`empty_design` 422 — não confia no cliente) e snapshot PNG. Snapshot = `gl.domElement.toDataURL` (`preserveDrawingBuffer`) → multipart pro `approve`.
- **Sessão/estado:** camadas tipadas (`lib/customizer/types`) vivem no `state_json` (autosave debounced do `P7-EDITOR-01`); uploads voltam no `SessionPublic.uploads` (presigned) pra **restaurar** camadas-imagem (não só as desta aba).
- **Link público** (`/p/[token]`, server-fetch read-only) reusa os 2 painéis + `Panels`; aprovar exige **confirmar contato** (e-mail/telefone) que o backend casa com o `CustomerProfile`.

### Melhorias de qualidade (refinamento do editor — doc [30 §3.1/§5](../../concepts/30_3d_customization_technical_design.md))
- **Compositor unificado (corrige distorção de imagem/texto + 2D≠3D):** a arte é renderizada **uma vez** num "espaço físico" (proporção real = `regionAspect`) por `compose.renderArt`; o 2D mostra direto e o 3D desenha esse canvas na sub-região de UV (a UV cilíndrica desfaz a compressão) → **sem esticar** e **2D idêntico ao 3D**. Imagem mantém **aspecto natural** por padrão; **distorcer** é opt-in (`scale_y` + botão "Distorcer").
- **Cor 2D=3D:** `CanvasTexture.colorSpace = sRGB` no overlay (sem isso as cores divergiam).
- **Composite de produção:** o cliente renderiza o **retângulo achatado em alta-res** (`COMPOSITE_WIDTH`) e envia **junto do approve** (sem fila); backend valida/re-encoda e guarda **privado** (`composite_key`), congelando no pedido. Approve falha se o composite falhar (garante envio).
- **Imagem do carrinho = snapshot:** a linha de um item customizado mostra o **mockup 3D** (não a imagem genérica) → distingue 2 personalizações do mesmo produto.

### Refinamentos de UX + resiliência de GPU
- **Arrasto por extensão (não por centro):** o limite do arraste usa a **extensão da camada** (`clampAxis`) — imagem maior que a área **paneia** até a borda encostar (sempre cobre, sem buraco); menor fica **dentro**; o marcador vermelho fica **fixo na borda** (não some). Arraste **relativo** (pega no ponto e move pelo delta; clicar não recentraliza).
- **Sempre uma camada selecionada:** se a seleção some (ex.: refresh), o editor seleciona a **camada do topo** automaticamente — o usuário sempre consegue arrastar.
- **Ordem da lista = z:** o **topo da lista é a camada mais por cima** (z maior); `↑` traz pra frente, `↓` manda pra trás.
- **Composite com fundo transparente** (PNG com alpha) — só a arte, pronto pra impressão (o xadrez do painel 2D é CSS, não entra).
- **Mitigações de GPU (NVIDIA+Wayland é frágil):** canvas offscreen **reusado** no repaint (menos alocação); handler de **`webglcontextlost`** → mostra fallback em vez de tela preta. (Tentei remover o `preserveDrawingBuffer` pra economizar GPU, mas a captura ficou instável → **revertido**: o snapshot usa `toDataURL` com `preserveDrawingBuffer` ligado, que é confiável; o ganho era marginal.) Um crash de driver continua sendo do navegador/driver.
- **Envio com progresso + limites (UX resolvida agora):** upload de arte (≤ **30 MB**/imagem) e aprovação (snapshot + composite) vão por **Route Handlers** (`app/api/customizer/*`, `lib/backend-proxy`) via **XHR** com **barra de progresso** (%, tamanho, velocidade, tempo restante — `ProgressBar`/`upload-xhr`); Server Action não reporta progresso. O editor **mostra o limite por imagem** e **barra antes de enviar** (imagem grande demais, ou payload de aprovação > 48 MB → avisa o tamanho). O `serverActions.bodySizeLimit` fica em **50 MB** (default do Next é **1 MB** → dava **413** "Body exceeded 1 MB limit").

## Follow-ups
- [ ] **Recolor do produto** (paleta + material nomeado + seletor) — fora da V1 (doc [30 §12](../../concepts/30_3d_customization_technical_design.md)). → README da fase.
- [ ] **Arte vetorial (SVG/PDF)** pra gráficas — *Quando:* depois da V1. → README da fase.
- [ ] **e2e Playwright** do fluxo personalizar→aprovar→carrinho → `P3-SF-03`. → README da fase.
- [ ] **Fontes web (Inter/Roboto/Montserrat) carregadas no editor** (hoje dependem da fonte do SO; sem isso o canvas usa o fallback) + **aviso de glifo ausente**. → README da fase.
- [ ] **Handles 2D ricos** (escala/rotação por alça, não só sliders + arrastar) — polir UX. → README da fase.
- [ ] **Progresso cobre só o trecho navegador→Next** (a etapa Next→backend→S3 é opaca → mostra "Processando…"). Pra progresso real até o CDN: **upload direto ao S3 via presigned PUT** (bypassa o Next; o backend só registra o objeto). → README da fase.
