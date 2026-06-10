# Bazar — vibrante / marketplace

> **Estética:** colorida e promocional — cores fortes, badges de promoção, energia, densidade maior.
> **Home:** orientada a **categorias** — hero + seções de categoria (N produtos cada) + "ver todas".
> Cole o **overall context** do [guia](../README.md) 1× antes de gerar; depois cada tela abaixo.

### Home
```
Crie UMA tela: HOME de uma loja e-commerce vibrante (marketplace popular), HTML + Tailwind, responsivo (mobile-first), pt-BR, sample data realista.
Estética colorida e promocional: cores fortes e acentos, badges de promoção/desconto, energia, densidade maior.
Header sticky: logo + nome (esq); nav com as PRIMEIRAS 6 categorias + um item "Todas as categorias"; ícone de carrinho (dir). Inclua um DRAWER de mini-carrinho (itens, subtotal, "Finalizar compra") que desliza ao clicar no ícone do carrinho.
Composição da home (orientada a CATEGORIAS):
- Hero: CARROSSEL full-bleed com 1+ banners chamativos (imagem + headline + CTA); com 1 banner vira estático.
- Faixa de categorias: cards coloridos com ícone/imagem + nome.
- SEÇÕES DE CATEGORIA: para as PRIMEIRAS 4 a 6 categorias, uma seção POR categoria com o NOME da categoria + um link "ver todos", e um grid dos 6-8 PRIMEIROS produtos dela (4-5 col desktop / 2 mobile). Card: imagem, nome, preço R$ destacado, badge opcional ("-20%"/"Novo"), moldura/sombra, hover com elevação.
- Link "Ver todas as categorias" ao final.
- Banner promocional largo entre as seções.
Footer: sobre a loja, WhatsApp, redes sociais, copyright. Botão flutuante de WhatsApp.
```

### Categoria
```
Crie UMA tela: PÁGINA DE CATEGORIA (listagem) de uma loja e-commerce vibrante (marketplace), HTML + Tailwind, responsivo (mobile-first), pt-BR, sample data.
Estética colorida/promocional. Header sticky (logo+nome / nav categorias + "Todas as categorias" / ícone de carrinho) e footer consistentes. Botão flutuante de WhatsApp.
Conteúdo:
- Breadcrumb + título da categoria + descrição.
- Filtros simples (lateral/topo, visual) + ordenação ("Mais vendidos", "Menor preço").
- Grid denso de produtos (4-5 col desktop / 2 mobile). Card com moldura/sombra, imagem, nome, preço R$ destacado, badge opcional.
```

### Produto
```
Crie UMA tela: PÁGINA DE PRODUTO de uma loja e-commerce vibrante (marketplace), HTML + Tailwind, responsivo (mobile-first), pt-BR, sample data.
Estética colorida/promocional (cores fortes, badges, energia). Header sticky e footer consistentes. Botão flutuante de WhatsApp.
Conteúdo:
- Breadcrumb (Início / Categoria / Produto).
- 2 colunas (desktop): GALERIA (imagem grande + miniaturas) | INFOS (nome, preço grande em destaque, descrição, botão primário "Adicionar ao carrinho", botão secundário "Personalizar em 3D" — placeholder/área reservada).
- Seção "Quem viu, viu também": grid de relacionados (card com moldura/sombra, imagem, nome, preço R$ destacado, badge opcional).
```

### Checkout (single-page)
```
Crie UMA tela: CHECKOUT em PÁGINA ÚNICA (single-page) de uma loja e-commerce vibrante (marketplace), HTML + Tailwind, responsivo, pt-BR, sample data. SEM etapa de pagamento.
Estética colorida/promocional. Header simples (logo + nome).
Layout 2 colunas no desktop (1 coluna no mobile):
COLUNA PRINCIPAL:
- Bloco "Seu pedido": lista de itens (imagem, nome, preço unitário, seletor de quantidade, remover).
- Bloco "Contato": nome, e-mail, telefone com SELETOR DE PAÍS (bandeira + código) — sem cadastro/senha.
- Bloco "Entrega": endereço + opções (escolher uma): frete fixo, frete grátis acima de X, retirada local, "entrega combinada" (aviso: "A loja entrará em contato após a compra para combinar a entrega").
COLUNA LATERAL (resumo, sticky), destacada:
- Subtotal, campo de cupom, frete, total.
- Botão "Confirmar pedido" chamativo (NÃO há pagamento — só cria o pedido).
Sem exigir login. Estado vazio com link para produtos.
```

### Confirmação do pedido
```
Crie UMA tela: CONFIRMAÇÃO DO PEDIDO de uma loja e-commerce vibrante (marketplace), HTML + Tailwind, responsivo, pt-BR, sample data.
Estética colorida/promocional. Header simples (logo + nome).
Conteúdo:
- Destaque animado/colorido "Pedido recebido!" com ícone de sucesso e número do pedido (ex.: #1042).
- Mensagem: "A loja vai entrar em contato para confirmar pagamento e entrega." (Se entrega combinada: "A loja entrará em contato para combinar a entrega.")
- Resumo do pedido: itens (imagem, nome, qtd, preço), subtotal, frete, total.
- Dados de entrega informados.
- Nota: "Enviamos os detalhes para o seu e-mail/WhatsApp."
- Botão "Voltar à loja".
```
