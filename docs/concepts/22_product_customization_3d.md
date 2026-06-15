# Product Customization 3D

> **Escopo (ver [Fase 7 — Produtos 3D](../backlog/phase-7-3d-products.md)):**
> - **O 3D é a Fase 7.** A Fase 2 (catálogo) entrega **só imagem**; o 3D e o 3D personalizável vêm na **Fase 7 (Produtos 3D)**.
> - **Dois caminhos pros modelos 3D:**
>   - **Catálogo da plataforma (Fase 7 — padrão):** a Kriar disponibiliza modelos GLB personalizáveis **prontos** (caneca, camiseta…), **populados por seed** pelo dev (rápido/barato; o lojista não gera GLB de item comum). O **admin só habilita/desabilita**; o lojista **escolhe** do catálogo público.
>   - **Gerado pelo lojista ([Fase 12](../backlog/phase-12-merchant-3d-generation.md) — avançado):** o lojista **gera o próprio GLB via API de terceiros** (image/text → GLB): candidatos **Meshy / Tripo3D / Hyper3D** (decisão no doc [18](./18_open_decisions.md)), por loja (`store_id`), e **mapeia a área personalizável pelo painel**.
> - **Personalização restrita a plano pago = Fase 8:** na Fase 7 qualquer lojista personaliza (livre, com o catálogo); na **Fase 8** (planos/pagamentos) a personalização fica restrita a **plano pago** (e a geração própria, Fase 12, também é premium).
>
> Este doc descreve a experiência (sessão, aprovação, congelar no pedido), válida pros **dois caminhos** — muda só a **origem do modelo** (catálogo da plataforma vs gerado pela loja).
>
> **Contrato técnico (como implementar) está no doc [30](./30_3d_customization_technical_design.md):** preparo do GLB, área imprimível (decal), editor (react-three-fiber), `state_json`, snapshot, storage/segurança e o link público da assistida.

## Objetivo

A Kriar V1 não deve começar como uma plataforma genérica igual a qualquer ecommerce.

O foco inicial será atender empresas de:

- brindes;
- gráficas;
- comunicação visual;
- produtos personalizados.

Essas lojas precisam vender produtos que o cliente consegue personalizar antes da compra, como canecas, squeezes, camisas, ecobags, placas, adesivos e itens similares.

O diferencial da Kriar será permitir que o cliente personalize o produto no storefront usando uma experiência 3D, aprove o resultado visual e envie essa personalização para o lojista junto com o pedido.

## Decisão principal

A personalização 3D é um diferencial da Kriar, mas entra na **Fase 7** (a Fase 2 de catálogo entrega só imagem). Ela **não substitui** o ecommerce comum: produtos com apenas foto/descrição/preço/variações continuam sendo o padrão.

Tipos de produto (a partir da Fase 7): **imagem**; **imagem + 3D** (foto opcional); **imagem + 3D personalizável** (foto opcional).

Produtos personalizáveis terão uma experiência adicional:

```text
Ver produto -> Personalizar -> Aprovar arte -> Adicionar ao carrinho -> Comprar
```

## Tecnologia recomendada

O editor 3D do storefront deve usar:

```text
Three.js
```

Motivos:

- roda no navegador;
- funciona bem com React/Next.js;
- suporta modelos 3D em formatos comuns;
- permite aplicar texturas/imagens no produto;
- permite preview visual antes da compra;
- evita dependência de ferramenta proprietária na V1.

Se no futuro aparecer uma lib melhor para um caso específico, ela pode ser avaliada, mas a decisão inicial é Three.js.

## Modelos 3D

Há **dois caminhos** pra origem do modelo (a experiência de personalização é a mesma):

- **Catálogo da plataforma (Fase 7 — padrão):** modelos GLB personalizáveis **prontos**, da Kriar, **populados por seed** (com a área imprimível já definida); o **admin habilita/desabilita** e o lojista **escolhe** do catálogo público. Evita que cada lojista gere o GLB de um item comum.
- **Gerado pelo lojista ([Fase 12](../backlog/phase-12-merchant-3d-generation.md) — avançado):** o lojista **gera o próprio GLB via API de terceiros** (image/text → GLB) — candidatos **Meshy**, **Tripo3D**, **Hyper3D** (decisão no doc [18](./18_open_decisions.md)) — **por loja** (`store_id`), e **mapeia a área personalizável pelo painel**.

Exemplos de produtos típicos (no catálogo da plataforma ou gerados pela loja):

- caneca;
- squeeze;
- camisa;
- ecobag;
- copo;
- garrafa;
- chaveiro;
- placa;
- banner;
- adesivo.

Na **Fase 7** o lojista personaliza usando o **catálogo da plataforma** (livre); na **Fase 8** a personalização fica restrita a **planos pagos**; a **geração do próprio modelo** (Fase 12) é recurso premium.

## Tipo de produto

Um produto tem um `type` (em `catalog_products`, default `image`):

```text
image                  # produto comum (fotos), pode ter variações, vai direto ao carrinho
image_3d               # tem modelo 3D para visualização, sem personalização do cliente
image_3d_customizable  # tem modelo 3D personalizável: editor + aprovação antes do carrinho
```

Produto `image`:

- usa fotos normais;
- pode ter variações;
- vai direto para carrinho.

Produto `image_3d`:

- usa fotos normais na listagem;
- mostra o modelo 3D para visualização;
- vai direto para carrinho (sem personalização).

Produto `image_3d_customizable`:

- usa fotos normais na listagem;
- tem botão de personalização;
- abre editor 3D;
- permite upload de arte;
- salva sessão de personalização;
- exige aprovação visual antes de adicionar ao carrinho.

> **Faseamento:** o campo `type` nasce na **Fase 6** (default `image`), com o **portão do add-to-cart** — `image`/`image_3d` vão direto ao carrinho; `image_3d_customizable` exige sessão `approved`. O **catálogo de modelos da plataforma + o editor** são a **Fase 7**; a **geração do modelo pelo lojista (via API) + mapear a área** são a **Fase 12**.

## Parâmetros de personalização

Cada modelo 3D deve definir quais partes podem ser alteradas.

> **Na V1 (Fase 7):** imagem + texto + posição/escala/rotação dentro da área. A **cor do produto (recolor)** é **follow-up** — fora da V1 (doc [30 §12](./30_3d_customization_technical_design.md)).

Exemplo para caneca:

```text
cor da caneca
imagem aplicada
posição da imagem
escala da imagem
rotação da imagem
área imprimível
preview frontal
preview lateral
```

Exemplo para camisa:

```text
cor da camisa
imagem frontal
imagem traseira, se habilitada
posição da imagem
escala da imagem
tamanho escolhido
```

O modelo deve informar limites seguros:

- área máxima de impressão;
- proporção recomendada;
- tipos de arquivo aceitos;
- tamanho máximo do upload;
- aviso de baixa resolução quando possível.

O estado salvo deve ser suficiente para restaurar o editor exatamente no ponto em que o cliente parou.
Isso inclui textos, imagens, posição, escala, rotação, face/lado do modelo, área imprimível usada e — quando habilitada (fora da V1) — a cor do produto.

## Sessão de personalização

Quando o cliente abrir o editor, o sistema deve criar uma sessão de personalização.

Essa sessão deve ser salva para permitir:

- continuar depois;
- recuperar se o cliente recarregar a página;
- continuar sem login usando sessão anônima;
- recuperar por link seguro depois que informar e-mail/telefone;
- adicionar ao carrinho com segurança;
- anexar a arte aprovada ao pedido;
- permitir que o lojista visualize o que o cliente estava montando.

Dados da sessão:

- loja;
- produto;
- guest session;
- customer, se já existir;
- modelo 3D usado;
- parâmetros escolhidos;
- arquivos enviados pelo cliente;
- preview renderizado;
- status da sessão;
- data de expiração;
- referência do carrinho, se houver.

Validade:

```text
30 dias
```

Depois disso, a sessão deve virar `expired`.
O registro deve continuar no banco por soft delete/status para auditoria.
Arquivos temporários não aprovados podem seguir política de limpeza, mas sem apagar o histórico de negócio.

Status sugeridos:

| Status | Significado |
|---|---|
| `draft` | Cliente está editando |
| `approved` | Cliente aprovou visualmente |
| `added_to_cart` | Personalização foi adicionada ao carrinho |
| `ordered` | Personalização virou pedido |
| `abandoned` | Sessão não avançou |
| `expired` | Sessão expirou |

## Aprovação visual

Antes de adicionar ao carrinho, o cliente deve confirmar que aprovou a personalização.

Texto sugerido:

```text
Confirmo que revisei a arte e quero usar esta personalização no produto.
```

Ao aprovar, o sistema deve salvar:

- JSON com os parâmetros da personalização;
- arquivo original enviado pelo cliente;
- preview renderizado;
- imagem final/snapshot de aprovação;
- versão do modelo 3D usado;
- data/hora da aprovação.

O pedido deve usar esse estado aprovado.
Alterações posteriores na sessão não devem mudar um pedido já criado.

## Personalização assistida pelo lojista

Nem todo cliente quer ou consegue personalizar sozinho. Um caminho comum: o cliente chega pelo site e vai **direto falar com o vendedor** (ex.: WhatsApp), não personaliza online e **pede para o lojista montar a personalização por ele**.

Fluxo:

- O lojista monta a personalização **em nome do cliente**, usando o **contato do cliente** (e-mail ou telefone) para **pré-cadastrá-lo** (reusa `create_or_update_customer` — e-mail/telefone normalizados).
- A **sessão de personalização** é salva vinculada a esse cliente (mesma `customization_session`, marcada como criada pela loja — `created_by`).
- O cliente **acessa a sua personalização** pelo e-mail/telefone que o lojista pré-cadastrou e **revisa**.
- Ao **aprovar**, ele segue o **fluxo normal** — carrinho, pagamento etc. — **como se tivesse feito tudo sozinho** (a sessão aprovada vira item de carrinho/pedido pelas mesmas regras de Aprovação visual e Carrinho e pedido).

**Acesso à personalização — decidido** (doc [30 §9](./30_3d_customization_technical_design.md)): os **dois caminhos**:

- **Fase 7 — link público compartilhável** (read-only, sem login): o cliente vê e **compartilha com amigos**; **aprovar/comprar** pede só **confirmação de contato** (e-mail/telefone pré-cadastrado), **sem conta**.
- **Fase 8 — logado:** com **conta do cliente**, ele também vê/aprova suas personalizações na **área do cliente**.

> **Quando:** o link público + confirmação de contato é **Fase 7**; o acesso **logado** depende da conta do cliente (**Fase 8**).

## Carrinho e pedido

Um item de carrinho pode apontar para uma sessão de personalização aprovada.

Quando o pedido for criado, a personalização deve ser congelada em uma cópia própria do pedido.

O lojista precisa receber:

- produto comprado;
- quantidade;
- variação escolhida;
- preview da personalização;
- arquivo original enviado pelo cliente;
- parâmetros usados no modelo;
- observações do cliente, se houver;
- status da arte.

Isso garante que o que o cliente aprovou no storefront seja o que o lojista verá no painel.

## Painel do lojista

No painel, o lojista deve conseguir:

- marcar produto como personalizável;
- escolher modelo 3D disponível para o produto;
- ver pedidos com personalização;
- abrir preview da arte aprovada;
- baixar arquivos enviados pelo cliente;
- ver parâmetros da personalização;
- atualizar status operacional da produção.

**Status de produção** (`CustomizationProductionStatus`) — vive no **item do pedido** (`customization_order_items`, congelado), começa em `received` quando o pedido é feito e é avançado pelo lojista no painel:

| Status | Significado |
|---|---|
| `received` | Arte recebida |
| `reviewing` | Lojista está avaliando |
| `needs_contact` | Precisa falar com cliente |
| `approved_for_production` | Pode produzir |
| `in_production` | Em produção |
| `production_done` | Produção finalizada |

> O painel lista as **sessões** da loja (atualização quase em tempo real por **polling**, [31 §4](./31_configuration_and_constants.md)); abre o detalhe pra **baixar** a arte de produção (composite) + prévia + uploads (URLs assinadas) e, quando a sessão virou pedido, **avançar o status de produção**. Montar **assistida** gera o `public_token` e o link pra o cliente aprovar.

## Admin da Kriar

**A plataforma mantém um catálogo público de modelos 3D** (Fase 7), **populado por seed** pelo dev (o GLB em si vem por seed — não há modelagem no admin). Os **parâmetros** (área imprimível, limites de arte) ficam **no banco e são editáveis no admin** — o seed dá só o valor inicial (doc [30](./30_3d_customization_technical_design.md)). O admin, no que toca a 3D, cuida de:

- **habilitar/desabilitar** modelos do catálogo (visibilidade pro lojista) + preview;
- **editar a área imprimível** e os limites do modelo (ferramenta visual de mapeamento) — a **mesma** que o lojista usará na [Fase 12](../backlog/phase-12-merchant-3d-generation.md) pro próprio GLB;
- (**Fase 12**) configurar a **API de geração 3D** (provedor/chaves, limites de uso) pro caminho em que o **lojista gera o próprio GLB**;
- moderar conteúdo/abuso, se necessário;
- (Fase 8) amarrar a capacidade de personalizar ao **plano pago**.

Os modelos do catálogo são curados via seed; quando o lojista gera o próprio (Fase 12), a qualidade é responsabilidade dele (a API + os limites do produto ajudam).

## Storefront

A página de produto deve mostrar claramente quando o produto é personalizável.

Fluxo:

1. Cliente acessa produto personalizável.
2. Clica em `Personalizar`.
3. Storefront abre editor 3D.
4. Cliente envia imagem.
5. Cliente ajusta posição, escala, rotação e opções permitidas.
6. Sistema salva a sessão automaticamente.
7. Cliente aprova visualmente.
8. Cliente adiciona ao carrinho.
9. Carrinho mantém a personalização vinculada ao item.
10. Pedido congela a personalização aprovada.

## WhatsApp

Na V1, não haverá chat interno completo.

O storefront deve permitir um botão flutuante de WhatsApp, quando a loja configurar um número de atendimento.

Objetivo:

- tirar dúvidas durante a personalização;
- permitir conversa rápida entre cliente e loja;
- ajudar o lojista a orientar sobre qualidade da arte ou viabilidade de produção.

O botão pode incluir contexto na mensagem:

```text
Olá, estou personalizando este produto e tenho uma dúvida: {product_url}
```

Se existir uma sessão de personalização, a mensagem pode incluir um identificador seguro ou link público temporário, desde que não exponha dados sensíveis.

## Visualização pelo lojista

A V1 deve permitir que o lojista veja sessões de personalização salvas.

Essa visualização pode ser quase em tempo real usando autosave da sessão.
Na V1, polling simples é suficiente.
WebSocket pode ficar para depois se a experiência exigir.

Isso ajuda o lojista a entender:

- qual produto está sendo personalizado;
- qual imagem foi enviada;
- como a arte está posicionada;
- se parece haver problema de qualidade;
- se o cliente pode precisar de ajuda.

Essa visualização deve ser usada com cuidado.
O lojista não deve interromper o cliente dentro do site.
O contato ativo deve acontecer pelo WhatsApp quando o cliente pedir ajuda ou quando houver um pedido/lead claro.

## Segurança e privacidade

Uploads de personalização devem ser tratados como arquivos privados até virarem parte pública de um pedido ou preview autorizado.

Regras:

- validar tipo de arquivo;
- validar tamanho;
- gerar URLs assinadas quando necessário;
- não expor arquivos originais em URLs públicas permanentes;
- registrar auditoria de acesso do lojista;
- apagar sessões expiradas conforme política definida;
- separar arquivos por `store_id`.

## Fora da V1

Não entram na V1:

- marketplace de modelos 3D para terceiros;
- upload de modelo 3D pelo lojista;
- chat interno completo;
- IA gerando arte final automaticamente;
- validação profissional completa de pré-impressão;
- integração automática com softwares de gráfica;
- orçamento automático complexo por área de impressão.

## Decisão canônica

A Kriar nasce como **ecommerce comum** (catálogo só imagem) e ganha **personalização 3D na Fase 7**. O foco comercial inicial é brindes, gráficas e comunicação visual.
Os modelos 3D vêm do **catálogo da plataforma** (Fase 7, via seed) ou são **gerados pelo lojista via API** (Fase 12, por loja); o cliente final aprova uma personalização salva no carrinho e **congelada no pedido**. Na **Fase 8**, a personalização fica restrita a **planos pagos** (sem plano grátis).
