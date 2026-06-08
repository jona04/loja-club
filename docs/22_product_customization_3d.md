# Product Customization 3D

> **Escopo (ver [Fase 5 — Produtos 3D](./backlog/phase-5-3d-products.md)):**
> - **O 3D é a Fase 5.** A Fase 2 (catálogo) entrega **só imagem**; o 3D e o 3D personalizável vêm na **Fase 5 (Produtos 3D)**.
> - **Os modelos 3D são gerados pelo lojista**, via **API de terceiros** (image/text → GLB): candidatos **Meshy / Tripo3D / Hyper3D** (decisão no doc [18](./18_open_decisions.md)). Os modelos são **por loja** (`store_id`); não há catálogo 3D da plataforma.
> - **Personalização restrita a plano pago = Fase 6:** na Fase 5 qualquer lojista personaliza (livre); na **Fase 6** (planos/pagamentos) só lojista com **plano pago** personaliza (sem plano grátis).
>
> Este doc descreve a experiência (sessão, aprovação, congelar no pedido), com o **modelo gerado pelo lojista via API**.

## Objetivo

A Loja Club V1 não deve começar como uma plataforma genérica igual a qualquer ecommerce.

O foco inicial será atender empresas de:

- brindes;
- gráficas;
- comunicação visual;
- produtos personalizados.

Essas lojas precisam vender produtos que o cliente consegue personalizar antes da compra, como canecas, squeezes, camisas, ecobags, placas, adesivos e itens similares.

O diferencial da Loja Club será permitir que o cliente personalize o produto no storefront usando uma experiência 3D, aprove o resultado visual e envie essa personalização para o lojista junto com o pedido.

## Decisão principal

A personalização 3D é um diferencial da Loja Club, mas entra na **Fase 5** (a Fase 2 de catálogo entrega só imagem). Ela **não substitui** o ecommerce comum: produtos com apenas foto/descrição/preço/variações continuam sendo o padrão.

Tipos de produto (a partir da Fase 5): **imagem**; **imagem + 3D** (foto opcional); **imagem + 3D personalizável** (foto opcional).

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

**Os modelos 3D são gerados pelo próprio lojista, via API de terceiros** (image/text → GLB) — candidatos **Meshy**, **Tripo3D**, **Hyper3D** (decisão no doc [18](./18_open_decisions.md)). **Não há mais biblioteca/catálogo 3D da plataforma**; os modelos são **por loja** (`store_id`).

O lojista gera o GLB a partir de uma imagem/descrição do seu produto e o vincula ao produto do catálogo. Exemplos de produtos típicos:

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

Os modelos são **por loja** (gerados pelo lojista via API). Na **Fase 5** qualquer lojista cria/personaliza; na **Fase 6** a personalização fica restrita a **planos pagos**.

## Produto personalizável

Um produto pode ser:

```text
simple
customizable_3d
```

Produto `simple`:

- usa fotos normais;
- pode ter variações;
- vai direto para carrinho.

Produto `customizable_3d`:

- usa fotos normais na listagem;
- tem botão de personalização;
- abre editor 3D;
- permite upload de arte;
- salva sessão de personalização;
- exige aprovação visual antes de adicionar ao carrinho.

## Parâmetros de personalização

Cada modelo 3D deve definir quais partes podem ser alteradas.

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
Isso inclui textos, imagens, cor do produto, posição, escala, rotação, face/lado do modelo e área imprimível usada.

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

Status de arte sugeridos:

| Status | Significado |
|---|---|
| `received` | Arte recebida |
| `reviewing` | Lojista está avaliando |
| `needs_contact` | Precisa falar com cliente |
| `approved_for_production` | Pode produzir |
| `in_production` | Em produção |
| `production_done` | Produção finalizada |

## Admin da Loja Club

**Não há mais biblioteca de modelos 3D da plataforma.** Quem gera e gerencia os modelos é o **lojista**, via API de terceiros (Fase 5).

O admin da plataforma, no que toca a 3D, cuida só da **integração**:

- configurar a API de geração 3D (provedor/chaves, limites de uso);
- moderar conteúdo/abuso, se necessário;
- (Fase 6) amarrar a capacidade de personalizar ao **plano pago**.

A qualidade do modelo gerado é responsabilidade do lojista (a API + os limites do produto ajudam).

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

A Loja Club nasce como **ecommerce comum** (catálogo só imagem) e ganha **personalização 3D na Fase 5**. O foco comercial inicial é brindes, gráficas e comunicação visual.
Os modelos 3D são **gerados pelo lojista via API de terceiros** (não pela Loja Club) e ficam **por loja**; o cliente final aprova uma personalização salva no carrinho e **congelada no pedido**. Na **Fase 6**, a personalização fica restrita a **planos pagos** (sem plano grátis).
