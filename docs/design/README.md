# Templates da vitrine — GUIA (consultar SEMPRE antes de criar/ajustar prompts)

> Fonte única do **contrato e das convenções** dos templates da vitrine (`P3-TPL-01`).
> Os prompts de cada template estão em [`prompts/`](prompts/) (`aurora.md`, `bazar.md`, `studio.md`) e **devem seguir este guia**.

## O que é
A vitrine pública (storefront) de uma loja de e-commerce na plataforma Kriar. O cliente final **navega, compra sem login** e finaliza o pedido. Por enquanto **sem pagamento online** (o pedido é registrado; a loja contata depois). Nicho inicial: brindes/gráficas (3D personalizável vem na Fase 5).

## O contrato (3 camadas)
| Camada | Igual entre templates? | O quê |
|---|---|---|
| **Dados** | ✅ Sim | loja, banners, categorias, produtos (destaques **e** por categoria) |
| **Composição da home** | ❌ Não — por template + **configurável pelo lojista** | quais blocos e quantos |
| **Fluxo de compra** | ✅ Sim | produto → carrinho → checkout → confirmação |

**Regra de ouro:** trocar de template **nunca quebra** o fluxo do cliente. O que muda é a **apresentação** e a **composição da home** — os dados e o fluxo são os mesmos.

## Telas (5 por template) = 5 prompts
`Home` · `Categoria` · `Produto` · `Checkout (single-page)` · `Confirmação do pedido`.
- **Carrinho** não é página: é um **drawer** (mini-carrinho no ícone do header) + o bloco de itens no topo do checkout.

## Blocos da home (composição configurável)
A home é montada por **blocos**, dos mesmos dados. Tipos:
- **Hero:** banner único **ou carrossel** (1 imagem = banner; **2+ = carrossel**).
- **Destaques:** grid de produtos `is_featured`.
- **Seção de categoria:** uma categoria + os **N primeiros produtos** + "ver todos da categoria".
- **Faixa de categorias** / **banner promocional**.

Defaults dos templates atuais:
- **Aurora** (premium/minimal): hero + **destaques** (curado — "menos é mais").
- **Bazar** (vibrante/marketplace): hero + **seções de categoria** (as primeiras M categorias, N produtos cada).

> O lojista controla a **ordem** das categorias (define quais entram primeiro na home/nav). **Home 100% configurável** (ligar/desligar blocos) é evolução futura.

## Regras importantes (valem pra todos os templates)
- **Nav de categorias:** mostrar as **primeiras N** (ex.: 5–6) + um item **"Todas as categorias"** (menu/dropdown ou página). **Nunca** uma barra com 20 categorias.
- **Home curada:** não despejar 20 seções (scroll gigante) — só as primeiras M + **"Ver todas as categorias"**.
- **Preço:** formatado pelo **locale da loja** (`R$` / `$` / `€` …). O `R$` nos prompts é **só sample data** — a moeda/símbolo real é por loja na implementação (`P3-LOC-01`).
- **Checkout:** **single-page** (itens + contato + endereço + resumo numa página). Contato: nome, e-mail, **telefone com seletor de país** (E.164). **4 opções de entrega:** frete fixo, frete grátis acima de X, retirada local, **entrega combinada** (aviso "a loja entrará em contato"). **Sem pagamento** ("Confirmar pedido" só cria o pedido).
- **Confirmação:** "Pedido recebido", resumo, "a loja vai entrar em contato".
- **3D (Fase 5):** na página de produto, um botão secundário **"Personalizar em 3D"** como **placeholder** (sem função agora).
- **WhatsApp:** só **botão flutuante** de contato (canto inferior direito). **Não** há "comprar pelo WhatsApp".

## Convenções técnicas (todo prompt)
- HTML + **Tailwind CSS**, **responsivo** (mobile-first), **pt-BR**, **sample data realista**.
- **1 tela = 1 arquivo** (`.html`); **sem** navegação entre páginas por JS (o roteamento é feito no React depois).
- Header + footer **consistentes** entre as telas do template.

## Workflow
1. Gerar no **uxpilot** com o **overall context** (abaixo, cole 1×) + o prompt de **cada tela** (em [`prompts/<template>.md`](prompts/) — **um arquivo por template**).
2. Salvar em `docs/design/templates/<nome>/`: `home/category/product/checkout/confirmation.html` + `print.png` (= `preview_image_url`).
3. Claude porta para `frontend-storefront/templates/<nome>/` (resolver por `active_template_id`) + seed em `content_theme_templates`.

## Overall context (cole 1× no uxpilot — serve os 3 templates)
> Neutro de estética; a aparência + os blocos vêm em cada prompt de tela.

```
Projeto: a vitrine pública (storefront) de uma loja de e-commerce na plataforma Kriar. O cliente final navega, escolhe produtos e finaliza o pedido SEM criar conta. Por enquanto NÃO há pagamento online — o pedido é registrado e a loja entra em contato depois.

Tecnologia: HTML + Tailwind CSS, responsivo (mobile-first), pt-BR, sample data realista (produtos, preços em R$, categorias, imagens placeholder). Cada tela é um arquivo independente (sem navegação entre páginas por JS).

Dados da loja (base de todas as telas):
- Loja: nome, logo, descrição curta, WhatsApp, redes sociais.
- Banners: 1 imagem = banner estático; 2+ imagens = carrossel.
- Categorias: nome + imagem. Produtos: nome, preço em R$, imagens, descrição.

Elementos CONSISTENTES em todas as telas (a posição pode variar por template):
- Marca: logo + nome da loja. Acesso às categorias (nav no topo OU sidebar, conforme o template), com as PRIMEIRAS categorias + um item "Todas as categorias" (NUNCA listar 20 numa barra). Ícone de carrinho.
- Mini-carrinho em DRAWER: desliza ao clicar no ícone do carrinho — itens (imagem, nome, qtd, preço), subtotal, botão "Finalizar compra".
- Card de produto consistente: imagem, nome, preço em R$.
- Footer: sobre a loja, WhatsApp, redes sociais, copyright. Botão flutuante de WhatsApp (canto inferior direito).

Fluxo de compra: card → produto → "Adicionar ao carrinho" (abre o drawer) → Checkout single-page → Confirmação. Sem login; sem pagamento.

Observações:
- A HOME é montada por BLOCOS — a composição vem em cada prompt de tela (cada template compõe diferente).
- O preço aparece como R$ no sample, mas o símbolo real é por loja (R$/$/€) — só siga o sample.
- A página de produto reserva um botão secundário "Personalizar em 3D" (placeholder, futuro).

A estética e os blocos específicos vêm no prompt de CADA tela.
```

## Estrutura de cada arquivo em `prompts/`
**Um arquivo por template** (`prompts/aurora.md`, `prompts/bazar.md`, `prompts/studio.md`, …). Cada um traz, no topo, a **estética** + a **composição da home** do template, e os **5 prompts de tela**: `Home · Categoria · Produto · Checkout · Confirmação` — cada prompt seguindo as **regras** deste guia. Para um template novo: copie a estrutura de um existente e troque **só** a estética e os blocos (o contrato é o mesmo).

## Fora de escopo agora (anotado)
**Editor 3D** → Fase 5 (só o slot no Produto). **Área do cliente / login / acompanhar pedido** → Fase 6. **Busca** → futuro. **Página institucional** → reusa o shell (sem prompt). **Admin pra cadastrar templates** → Fase 7.

## Templates atuais
- **Aurora** — premium, minimalista, editorial. Home: hero + **destaques** (curado).
- **Bazar** — vibrante, colorido, marketplace. Home: hero + **seções de categoria**.
- **Studio** — catálogo limpo/utilitário com **sidebar** (categorias + filtros à esquerda) + grid denso. Home: **sidebar + grid** (categorias na sidebar, não no topo). *Deliberadamente **bem diferente** dos outros em **blocos/estrutura** — serve de **teste** de que o storefront resolve composições distintas com o **mesmo contrato**.*
