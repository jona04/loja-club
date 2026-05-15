# Product Customization 3D

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

A V1 deve incluir personalização 3D de produtos.

Isso não substitui o ecommerce comum.
Produtos simples continuam podendo usar apenas fotos, descrição, preço e variações.

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

Os modelos 3D serão criados, preparados e publicados pela equipe da Loja Club.

O lojista não precisa subir modelo 3D próprio na V1.
Ele apenas vincula um produto do catálogo a um modelo disponibilizado pela Loja Club.

Exemplos de modelos:

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

Os modelos devem ser globais da plataforma, mas podem ser habilitados por categoria, plano ou loja.

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

## Sessão de personalização

Quando o cliente abrir o editor, o sistema deve criar uma sessão de personalização.

Essa sessão deve ser salva para permitir:

- continuar depois;
- recuperar se o cliente recarregar a página;
- adicionar ao carrinho com segurança;
- anexar a arte aprovada ao pedido;
- permitir que o lojista visualize o que o cliente estava montando.

Dados da sessão:

- loja;
- produto;
- modelo 3D usado;
- parâmetros escolhidos;
- arquivos enviados pelo cliente;
- preview renderizado;
- status da sessão;
- data de expiração;
- referência do carrinho, se houver.

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

O admin interno deve gerenciar a biblioteca de modelos 3D.

Funcionalidades:

- cadastrar modelo 3D;
- subir arquivos do modelo;
- definir categoria do modelo;
- definir áreas personalizáveis;
- definir parâmetros permitidos;
- publicar/despublicar modelo;
- vincular modelo a categorias ou planos;
- manter versões dos modelos.

O lojista usa os modelos publicados.
A curadoria e a qualidade técnica dos modelos são responsabilidade da Loja Club.

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

A Loja Club V1 deve nascer com ecommerce comum e personalização 3D de produtos.
O foco comercial inicial será brindes, gráficas e comunicação visual.
Os modelos 3D serão criados e publicados pela Loja Club, os lojistas vinculam esses modelos aos seus produtos, e o cliente final aprova uma personalização que fica salva no carrinho e congelada no pedido.
