# Aurora — premium minimalista

> **Estética:** minimalista/editorial — muito espaço em branco, imagens grandes, tipografia elegante, paleta neutra (off-white/cinza/quase-preto) + 1 cor de destaque, hover sutil.
> **Home:** curada — hero + faixa de categorias + **destaques** + banner editorial.
> Cole o **overall context** do [guia](../README.md) 1× antes de gerar; depois cada tela abaixo.

### Home
```
Crie UMA tela: HOME de uma loja e-commerce premium, HTML + Tailwind, responsivo (mobile-first), pt-BR, sample data realista.
Estética minimalista/editorial: muito espaço em branco, imagens grandes, tipografia elegante, paleta neutra (off-white/cinza/quase-preto) + 1 cor de destaque, hover sutil.
Header sticky: logo + nome (esq); nav com as PRIMEIRAS 5 categorias + um item "Todas as categorias"; ícone de carrinho (dir). Inclua um DRAWER de mini-carrinho (itens, subtotal, "Finalizar compra") que desliza ao clicar no ícone do carrinho.
Composição da home (curada):
- Hero: CARROSSEL full-bleed com 1+ banners (imagem + headline + botão CTA "Ver produtos"); com 1 banner vira estático.
- Faixa de categorias (imagem + nome).
- Seção "Destaques": grid arejado de produtos (4 col desktop / 2 mobile). Card: imagem quadrada, nome, preço R$, hover com leve zoom.
- Seção editorial secundária: banner largo (imagem + texto + link).
Footer: sobre a loja, WhatsApp, redes sociais, copyright. Botão flutuante de WhatsApp.
```

### Categoria
```
Crie UMA tela: PÁGINA DE CATEGORIA (listagem) de uma loja e-commerce premium, HTML + Tailwind, responsivo (mobile-first), pt-BR, sample data.
Estética minimalista/editorial. Header sticky (logo+nome / nav categorias + "Todas as categorias" / ícone de carrinho) e footer consistentes. Botão flutuante de WhatsApp.
Conteúdo:
- Breadcrumb + título da categoria + descrição curta.
- Barra de ordenação simples (visual): "Mais recentes", "Menor preço".
- Grid arejado de produtos (4 col desktop / 2 mobile). Card: imagem quadrada, nome, preço R$, hover com leve zoom.
```

### Produto
```
Crie UMA tela: PÁGINA DE PRODUTO de uma loja e-commerce premium, HTML + Tailwind, responsivo (mobile-first), pt-BR, sample data.
Estética minimalista/editorial (espaço em branco, tipografia elegante, neutra + 1 cor de destaque). Header sticky e footer consistentes. Botão flutuante de WhatsApp.
Conteúdo:
- Breadcrumb (Início / Categoria / Produto).
- 2 colunas (desktop): GALERIA (imagem grande + miniaturas clicáveis) | INFOS (nome, preço grande, descrição, botão primário "Adicionar ao carrinho", botão secundário "Personalizar em 3D" — placeholder/área reservada, sem função).
- Seção "Você também pode gostar": grid de relacionados (card: imagem quadrada, nome, preço R$).
```

### Checkout (single-page)
```
Crie UMA tela: CHECKOUT em PÁGINA ÚNICA (single-page) de uma loja e-commerce premium, HTML + Tailwind, responsivo, pt-BR, sample data. SEM etapa de pagamento.
Estética minimalista/editorial. Header simples (logo + nome).
Layout 2 colunas no desktop (1 coluna no mobile):
COLUNA PRINCIPAL:
- Bloco "Seu pedido": lista de itens (imagem, nome, preço unitário, seletor de quantidade, remover).
- Bloco "Contato": nome, e-mail, telefone com SELETOR DE PAÍS (bandeira + código) — sem cadastro/senha.
- Bloco "Entrega": endereço + opções (escolher uma): frete fixo, frete grátis acima de X, retirada local, "entrega combinada" (aviso: "A loja entrará em contato após a compra para combinar a entrega").
COLUNA LATERAL (resumo, sticky):
- Subtotal, campo de cupom, frete, total.
- Botão "Confirmar pedido" (NÃO há pagamento — só cria o pedido).
Sem exigir login. Estado vazio com link para produtos.
```

### Confirmação do pedido
```
Crie UMA tela: CONFIRMAÇÃO DO PEDIDO de uma loja e-commerce premium, HTML + Tailwind, responsivo, pt-BR, sample data.
Estética minimalista/editorial. Header simples (logo + nome).
Conteúdo:
- Destaque "Pedido recebido!" com ícone de sucesso e número do pedido (ex.: #1042).
- Mensagem: "A loja vai entrar em contato para confirmar pagamento e entrega." (Se entrega combinada: "A loja entrará em contato para combinar a entrega.")
- Resumo do pedido: itens (imagem, nome, qtd, preço), subtotal, frete, total.
- Dados de entrega informados (endereço/forma).
- Nota: "Enviamos os detalhes para o seu e-mail/WhatsApp."
- Botão "Voltar à loja".
```
