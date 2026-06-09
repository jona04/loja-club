# Templates da vitrine — workflow + prompts (uxpilot.ai)

> Decisões de `P3-TPL-01`. Designs gerados no **uxpilot.ai** (HTML + Tailwind), salvos aqui, portados para componentes no `frontend-storefront`. **Cada template é único** (layout próprio, inclusive checkout).

## Workflow
1. **1 tela = 1 prompt completo** no uxpilot. **5 telas por template** → **10 prompts** pra 2 templates:
   `Home` · `Categoria` · `Produto` · `Checkout (single-page)` · `Confirmação do pedido`.
   - **Carrinho não é página separada:** é um **drawer** (mini-carrinho que desliza no ícone do header) **+** o **bloco de itens no topo do checkout**.
2. Salva os `.html` em **`docs/design/templates/<nome>/`**: `home.html`, `category.html`, `product.html`, `checkout.html`, `confirmation.html` + `print.png` (vira o `preview_image_url` por **seed/hardcoded**).
3. **Claude** adapta cada `.html` em árvore de componentes em `frontend-storefront/templates/<nome>/` (resolver por `active_template_id`), faz o **seed** em `content_theme_templates` e garante o **contrato**.
4. Cadastro de templates por UI (admin da plataforma) é **futuro** → **Fase 7**.

## Contexto geral (overall context) — cole **1×** no uxpilot; serve os **2 templates**
> É **neutro de estética**: a aparência (premium/vibrante) vem em cada prompt de tela.

```
Projeto: a vitrine pública (storefront) de uma loja de e-commerce hospedada na plataforma Loja Club. O cliente final navega, escolhe produtos e finaliza o pedido SEM criar conta. Por enquanto NÃO há pagamento online — o pedido é registrado e a loja entra em contato depois.

Tecnologia: HTML + Tailwind CSS, responsivo (mobile-first), em português (pt-BR). Cada tela é um arquivo independente (sem navegação entre páginas por JS). Use sample data realista (produtos, preços em R$, categorias, imagens placeholder).

Dados da loja (base de todas as telas):
- Loja: nome, logo, descrição curta, WhatsApp, redes sociais.
- Banners: 1 imagem = banner estático; 2+ imagens = carrossel.
- Categorias: nome + imagem. Produtos: nome, preço em R$, imagens, descrição.

Elementos CONSISTENTES em todas as telas:
- Header sticky: logo + nome da loja (esq), navegação de categorias (centro/dir), ícone de carrinho (dir).
- Mini-carrinho em DRAWER: desliza ao clicar no ícone do carrinho — itens resumidos (imagem, nome, qtd, preço), subtotal, botão "Finalizar compra".
- Card de produto consistente em toda parte: imagem, nome, preço em R$.
- Footer: sobre a loja, WhatsApp, redes sociais, copyright.
- Botão flutuante de WhatsApp (canto inferior direito).

Fluxo de compra: card → página de produto → "Adicionar ao carrinho" (abre o drawer) → Checkout em página única (single-page) → Confirmação do pedido. Sem login; sem pagamento online.

Futuro (reservar, sem função agora): na página de produto, um botão secundário "Personalizar em 3D" (placeholder).

A estética específica (premium/minimalista ou vibrante/colorida) vem no prompt de CADA tela — este contexto é o mesmo para os dois templates.
```

## Contrato de conteúdo (TODO template respeita — só muda o visual)
- **Loja:** nome, logo, descrição, WhatsApp, redes sociais.
- **Tema:** cor de destaque; **banners** ordenados → **1 = banner; 2+ = carrossel** (config no painel do lojista).
- **Categorias:** `{nome, slug, imagem}`. **Produtos:** `{nome, slug, preço R$, imagens[], descrição}` (+ futuro: variações, `is_featured`, 3D).
- **Telas (V1 + Fase 4):** Home · Categoria · Produto · Checkout single-page · Confirmação.
- **Checkout (Fase 4, SEM pagamento):** contato (nome, e-mail, telefone com **seletor de país** p/ E.164) + endereço + **4 opções de entrega** (frete fixo / grátis acima de X / retirada local / **entrega combinada** com aviso) + resumo → "Confirmar pedido" cria o pedido (a loja contata depois; pagamento é **Fase 6**).
- **Interações que não podem quebrar entre templates:** card → produto; "Adicionar ao carrinho" → drawer/checkout; "Personalizar em 3D" → placeholder (**Fase 5**); WhatsApp = botão flutuante.
- **Fora dos templates agora:** editor 3D (Fase 5, só o slot no Produto); área do cliente/login/acompanhar pedido (Fase 6); página institucional (reusa o shell — sem prompt); busca e "loja não encontrada" (derivo do shell).

---

# Template "Aurora" (premium minimalista)

### Aurora — Home
```
Crie UMA tela: HOME de uma loja e-commerce premium, em HTML + Tailwind CSS, responsivo (mobile-first), pt-BR, com sample data realista (produtos, preços em R$, categorias, imagens placeholder).
Estética minimalista/editorial: muito espaço em branco, imagens grandes, tipografia elegante, paleta neutra (off-white/cinza/quase-preto) + 1 cor de destaque, hover sutil.
Header sticky: logo + nome (esq), nav de categorias (centro/dir), ícone de carrinho (dir).
Inclua um DRAWER de mini-carrinho que desliza da direita ao clicar no ícone do carrinho: lista resumida de itens (imagem, nome, qtd, preço), subtotal e botão "Finalizar compra".
Conteúdo da home:
- Hero: CARROSSEL full-bleed com 1+ banners (imagem + headline + botão CTA "Ver produtos"); com 1 banner vira estático (sem setas).
- Faixa de categorias (imagem + nome).
- Seção "Destaques": grid arejado de produtos (4 col desktop / 2 mobile). Card: imagem quadrada, nome, preço R$, hover com leve zoom.
- Seção editorial secundária: banner largo (imagem + texto + link).
Footer: sobre a loja, WhatsApp, redes sociais, copyright. Botão flutuante de WhatsApp.
```

### Aurora — Categoria
```
Crie UMA tela: PÁGINA DE CATEGORIA (listagem) de uma loja e-commerce premium, HTML + Tailwind, responsivo (mobile-first), pt-BR, sample data.
Estética minimalista/editorial. Header sticky (logo+nome / nav categorias / ícone de carrinho) e footer consistentes. Botão flutuante de WhatsApp.
Conteúdo:
- Breadcrumb + título da categoria + descrição curta.
- Barra de ordenação simples (visual): "Mais recentes", "Menor preço".
- Grid arejado de produtos (4 col desktop / 2 mobile). Card: imagem quadrada, nome, preço R$, hover com leve zoom.
```

### Aurora — Produto
```
Crie UMA tela: PÁGINA DE PRODUTO de uma loja e-commerce premium, HTML + Tailwind, responsivo (mobile-first), pt-BR, sample data.
Estética minimalista/editorial (espaço em branco, tipografia elegante, neutra + 1 cor de destaque). Header sticky (logo+nome / nav categorias / ícone de carrinho) e footer consistentes. Botão flutuante de WhatsApp.
Conteúdo:
- Breadcrumb (Início / Categoria / Produto).
- 2 colunas (desktop): GALERIA (imagem grande + miniaturas clicáveis) | INFOS (nome, preço grande, descrição, botão primário "Adicionar ao carrinho", botão secundário "Personalizar em 3D" — placeholder/área reservada, sem função).
- Seção "Você também pode gostar": grid de relacionados (card: imagem quadrada, nome, preço R$).
```

### Aurora — Checkout (single-page)
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

### Aurora — Confirmação do pedido
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

---

# Template "Bazar" (vibrante / marketplace)

### Bazar — Home
```
Crie UMA tela: HOME de uma loja e-commerce vibrante (vibe de marketplace popular), HTML + Tailwind, responsivo (mobile-first), pt-BR, sample data realista (produtos, preços R$, categorias, imagens placeholder).
Estética colorida e promocional: cores fortes e acentos, badges de promoção/desconto, energia, densidade maior.
Header sticky: logo + nome (esq), nav de categorias (centro/dir), ícone de carrinho (dir).
Inclua um DRAWER de mini-carrinho que desliza da direita ao clicar no ícone do carrinho: itens (imagem, nome, qtd, preço), subtotal e botão "Finalizar compra".
Conteúdo da home:
- Hero: CARROSSEL full-bleed com 1+ banners chamativos (imagem + headline + CTA); com 1 banner vira estático.
- Faixa de categorias: cards coloridos com ícone/imagem + nome.
- Seção "Ofertas" e seção "Mais vendidos": cada uma com título + grid denso de produtos (4–5 col desktop / 2 mobile). Card: imagem, nome, preço R$ destacado, badge opcional ("-20%"/"Novo"), moldura/sombra, hover com elevação.
- Banner promocional largo entre as seções.
Footer: sobre a loja, WhatsApp, redes sociais, copyright. Botão flutuante de WhatsApp.
```

### Bazar — Categoria
```
Crie UMA tela: PÁGINA DE CATEGORIA (listagem) de uma loja e-commerce vibrante (marketplace), HTML + Tailwind, responsivo (mobile-first), pt-BR, sample data.
Estética colorida/promocional. Header sticky (logo+nome / nav categorias / ícone de carrinho) e footer consistentes. Botão flutuante de WhatsApp.
Conteúdo:
- Breadcrumb + título da categoria + descrição.
- Filtros simples (lateral/topo, visual) + ordenação ("Mais vendidos", "Menor preço").
- Grid denso de produtos (4–5 col desktop / 2 mobile). Card com moldura/sombra, imagem, nome, preço R$ destacado, badge opcional.
```

### Bazar — Produto
```
Crie UMA tela: PÁGINA DE PRODUTO de uma loja e-commerce vibrante (marketplace), HTML + Tailwind, responsivo (mobile-first), pt-BR, sample data.
Estética colorida/promocional (cores fortes, badges, energia). Header sticky (logo+nome / nav categorias / ícone de carrinho) e footer consistentes. Botão flutuante de WhatsApp.
Conteúdo:
- Breadcrumb (Início / Categoria / Produto).
- 2 colunas (desktop): GALERIA (imagem grande + miniaturas) | INFOS (nome, preço grande em destaque, descrição, botão primário "Adicionar ao carrinho", botão secundário "Personalizar em 3D" — placeholder/área reservada).
- Seção "Quem viu, viu também": grid de relacionados (card com moldura/sombra, imagem, nome, preço R$ destacado, badge opcional).
```

### Bazar — Checkout (single-page)
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

### Bazar — Confirmação do pedido
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

## Em definição (próximas conversas)
- Blocos **configuráveis** por template (o que o lojista liga/desliga).
- Variações/disponibilidade/relacionados no V1 ou follow-up.
- Models: carrossel via `content_banners` (confirmado); seções via config (a definir).
- Reformulação da **ordem/prioridade das fases** (o usuário vai reorganizar).
