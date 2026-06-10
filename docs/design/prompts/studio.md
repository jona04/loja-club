# Studio — catálogo com sidebar (teste do contrato)

> **Estética:** limpa, utilitária e moderna (vibe de catálogo/SaaS) — neutra (branco/cinza) + 1 cor de acento, linhas finas, funcional.
> **Home:** **sidebar + grid** — categorias e filtros numa **sidebar à esquerda** (não no topo), busca na topbar, grid denso de produtos.
> **Deliberadamente bem diferente** de Aurora/Bazar em **blocos e estrutura** — mesmo **contrato de dados e fluxo**. Serve de teste de que o storefront resolve composições distintas.
> Cole o **overall context** do [guia](../README.md) 1× antes de gerar; depois cada tela abaixo.

### Home
```
Crie UMA tela: HOME de uma loja e-commerce estilo CATÁLOGO, HTML + Tailwind, responsivo (mobile-first), pt-BR, sample data realista.
Estética: limpa, utilitária e moderna (vibe de catálogo/SaaS) — neutra (branco/cinza) + 1 cor de acento, linhas finas, funcional e direta.
ESTRUTURA COM SIDEBAR (diferente de templates com nav no topo):
- Topbar fina: logo + nome (esq); BARRA DE BUSCA ao centro; ícone de carrinho (dir). As categorias NÃO ficam no topo.
- SIDEBAR ESQUERDA (fixa no desktop; vira drawer no mobile via botão "menu"): lista de categorias (com contagem de itens) + filtros simples (faixa de preço, ordenação). No fim da lista, um item "Todas as categorias".
- ÁREA PRINCIPAL: um BANNER SLIM no topo (1 imagem; carrossel se 2+) + um GRID DENSO de produtos (3-4 col). Card: imagem, nome, preço R$, hover discreto.
- Inclua um DRAWER de mini-carrinho (itens, subtotal, "Finalizar compra") que desliza ao clicar no ícone do carrinho.
Footer: sobre a loja, WhatsApp, redes sociais, copyright. Botão flutuante de WhatsApp.
```

### Categoria
```
Crie UMA tela: PÁGINA DE CATEGORIA (listagem) de uma loja e-commerce estilo CATÁLOGO, HTML + Tailwind, responsivo, pt-BR, sample data.
Estética limpa/utilitária. MESMA estrutura com SIDEBAR da home:
- Topbar fina: logo + nome / barra de busca / ícone de carrinho.
- SIDEBAR ESQUERDA: categorias (a atual destacada) + filtros (faixa de preço, ordenação).
- ÁREA PRINCIPAL: breadcrumb + título da categoria + GRID DENSO de produtos (3-4 col). Card: imagem, nome, preço R$.
Footer + botão flutuante de WhatsApp.
```

### Produto
```
Crie UMA tela: PÁGINA DE PRODUTO de uma loja e-commerce estilo CATÁLOGO, HTML + Tailwind, responsivo, pt-BR, sample data.
Estética limpa/utilitária. Topbar fina (logo + nome / busca / carrinho) — SEM sidebar nesta tela (página de produto full-width, limpa). Footer + botão flutuante de WhatsApp.
Conteúdo:
- Breadcrumb (Início / Categoria / Produto).
- 2 colunas (desktop): GALERIA (imagem grande + miniaturas) | INFOS (nome, preço grande, descrição, botão primário "Adicionar ao carrinho", botão secundário "Personalizar em 3D" — placeholder/área reservada).
- Seção "Itens relacionados": grid de relacionados (card: imagem, nome, preço R$).
```

### Checkout (single-page)
```
Crie UMA tela: CHECKOUT em PÁGINA ÚNICA (single-page) de uma loja e-commerce estilo CATÁLOGO, HTML + Tailwind, responsivo, pt-BR, sample data. SEM etapa de pagamento.
Estética limpa/utilitária. Header simples (logo + nome).
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
Crie UMA tela: CONFIRMAÇÃO DO PEDIDO de uma loja e-commerce estilo CATÁLOGO, HTML + Tailwind, responsivo, pt-BR, sample data.
Estética limpa/utilitária. Header simples (logo + nome).
Conteúdo:
- Destaque "Pedido recebido!" com ícone de sucesso e número do pedido (ex.: #1042).
- Mensagem: "A loja vai entrar em contato para confirmar pagamento e entrega." (Se entrega combinada: "A loja entrará em contato para combinar a entrega.")
- Resumo do pedido: itens (imagem, nome, qtd, preço), subtotal, frete, total.
- Dados de entrega informados.
- Nota: "Enviamos os detalhes para o seu e-mail/WhatsApp."
- Botão "Voltar à loja".
```
