# Storefront and Layouts

## Objetivo

O storefront é a loja pública do lojista.

Ele será acessado por subdomínio ou domínio próprio.

Além das páginas tradicionais de ecommerce, o storefront deve suportar produtos personalizáveis em 3D para lojas de brindes, gráficas e comunicação visual.

Exemplos:

```text
brindesfortaleza.kriar.shop
presentescriativos.kriar.shop
www.minhaloja.com.br
```

> **Estado da Fase 3 (V1) — o que o código entrega vs. esta visão.** A Fase 3 entrega o **storefront base (imagem)**: resolução por `Host`, templates `classic`/`modern` (realizados por **renderização condicional** nas páginas do App Router — a home difere por template; produto/categoria compartilham com o estilo do tema —, sem árvores `classic/`+`modern/` separadas), **home** (logo, banner, headline, destaques por `is_featured`, categorias, rodapé e **botão flutuante de WhatsApp** de contato), **produto** (imagem/nome/preço/descrição, **sem CTA de compra**) e **categoria** (nome + produtos), com cache por-loja no backend. **Deferido** (follow-ups no [README da Fase 3](../backlog/phase-3-storefront-and-layouts/README.md)): carrinho/checkout/entrega → **Fase 6**; editor 3D/`Personalizar` → **Fase 7**; e, como follow-up dentro da Fase 3: variações/disponibilidade/relacionados (produto), paginação-UI/filtros/ordenação (categoria), menu configurável + links sociais (home), destaque por **coleção** (hoje `is_featured`) e **i18n-readiness** (o V1 sai em pt-BR; ver `INV-G7`).

## Tecnologia recomendada

A recomendação para o storefront é Next.js.

Motivos:

- SEO;
- performance em páginas públicas;
- renderização server-side;
- possibilidade de cache;
- melhor adequação para ecommerce.

Para produtos personalizáveis, o storefront deve usar Three.js no navegador.
O editor 3D é uma experiência interativa da página de produto, não um frontend separado.

Decisão:

```text
O storefront deve usar Next.js desde a V1.
```

Não começar com React/Vite no storefront, para evitar refatoração posterior em SEO, roteamento, cache e renderização.

## Resolução da loja

Toda requisição do storefront deve resolver a loja pelo domínio.

Fluxo:

1. usuário acessa `empresa.kriar.shop`;
2. storefront lê o host;
3. consulta backend ou cache;
4. backend busca em `domain_hosts`;
5. encontra `store_id`;
6. carrega dados públicos da loja;
7. renderiza template ativo.

## Templates da V1

A V1 terá 2 templates prontos.

Sugestão:

| Template | Descrição |
|---|---|
| `classic` | Layout tradicional, simples e direto |
| `modern` | Layout visual, com banner forte e cards maiores |

O lojista não vai montar layout livre na V1. Ele escolhe entre templates prontos.

## Estrutura dos templates

Estrutura conceitual:

```text
frontend-storefront/
  src/
    templates/
      classic/
        HomePage
        ProductPage
        ProductCustomizer
        CategoryPage
        CartPage
        CheckoutPage
      modern/
        HomePage
        ProductPage
        ProductCustomizer
        CategoryPage
        CartPage
        CheckoutPage
```

> **`ProductCustomizer` (editor 3D) é da Fase 7.** Na Fase 3 os templates trazem Home/Product/Category (produtos de **imagem**); Cart/Checkout completam na Fase 6.

## Sistema de templates (evolução — `P3-TPL-01`)

> O V1 entrega **2 templates simples** (`classic`/`modern`) por renderização condicional. A [`P3-TPL-01`](../backlog/phase-3-storefront-and-layouts/P3-TPL-01-template-architecture-aurora.md) eleva isso a um **sistema de templates profissionais** (spec em definição). Direção:

- **Cada template = uma árvore de componentes própria** no `frontend-storefront` (`templates/<nome>/{Home,Category,Product,blocos}`), não só estilo condicional; um **resolver** mapeia `active_template_id` → a árvore.
- **2–3 templates** bem distintos (carrossel no topo, hero, seções ricas), adaptados de **referências de design** fornecidas.
- **Registro:** `content_theme_templates` lista os disponíveis, cada um com **`preview_image_url`**. O painel mostra **lista + imagem** (o lojista escolhe pela imagem; **não há preview ao vivo** ainda). Por ora os templates entram via **seed/código** — a **tela de admin** (kriar.shop) pra cadastrá-los é **futura** (Fase 4 — admin).
- **Models mais ricos:** carrossel (vários banners ordenados → `content_banners`), seções configuráveis, etc. — reaproveita `content_banners`/`content_menus`/`content_pages`; campos/tabelas novos **a definir** no spec.
- **Contrato (invariante):** trocar de template **não quebra** o fluxo do cliente — todos consomem o mesmo contrato de dados e levam ao mesmo **fluxo de compra** (Fase 6); e **todos reservam um slot pro editor 3D** (Fase 7).
- **Telas por template (V1 + Fase 6):** Home · Categoria · Produto · **Checkout single-page** · Confirmação. O **carrinho é um drawer** (mini-carrinho no header), não página separada. Editor 3D (Fase 7) e área do cliente/login/acompanhar pedido (Fase 8) entram depois; **página institucional** reusa o *shell* do template.
- **Estado (implementado em `P3-TPL-01`):** o storefront tem um **resolver** (`lib/templates.ts`) que mapeia `active_template_id` → árvore de componentes (`templates/<nome>/{Home,Category,Product}`), com **fallback** pro `base` (render legado `classic`/`modern`). **Aurora** portado (navegação: home/categoria/produto + drawer + slot 3D); **Bazar/Studio** caem no `base` até `P3-TPL-02`; checkout/confirmação dos templates = Fase 6.

## Configuração no banco

Tabelas:

```text
content_theme_templates
content_store_theme_settings
content_store_template_settings
```

### content_theme_templates

Templates globais.

Campos sugeridos:

| Campo | Descrição |
|---|---|
| `id` | `aurora`, `bazar`, `studio` |
| `name` | Nome exibido |
| `description` | Descrição |
| `is_active` | Se está disponível |
| `preview_image_url` | Imagem de preview |
| `settings_schema` | Manifesto dos campos editáveis do chrome (vem do código; seedado no deploy) |

### content_store_theme_settings

Configuração da loja.

Campos sugeridos:

| Campo | Descrição |
|---|---|
| `store_id` | Loja |
| `active_template_id` | Template ativo |
| `banner_image_url` | Banner principal |
| `headline` | Texto principal |
| `featured_collection_id` | Coleção em destaque |
| `primary_color` | Preparado para futuro |
| `background_color` | Preparado para futuro |
| `font_family` | Preparado para futuro |

### content_store_template_settings

Overrides do chrome **específico de cada template**, por **loja × template** (os defaults vêm do `settings_schema` do template).

| Campo | Descrição |
|---|---|
| `store_id` | Loja |
| `template_id` | Template a que os valores pertencem |
| `settings` | Objeto JSON `{chave: valor}` (chaves do `settings_schema`) |

`store_id + template_id` é único entre linhas ativas (soft delete); **resetar = excluir** (re-selecionar volta aos defaults). A vitrine expõe `theme.settings` = defaults do schema **⊕** overrides do template ativo.

> **`logo_url` e a descrição da loja vêm de `store_settings` (Fase 1)** — o theme cuida só de aparência/layout, sem duplicar contato/negócio.

## Fluxo de alteração de layout

No painel do lojista:

1. usuário acessa `Layout da Loja`;
2. vê os 2 templates;
3. clica em `Visualizar`;
4. visualiza com dados reais da loja;
5. clica em `Aplicar`;
6. backend salva `active_template_id`;
7. cache da loja é invalidado;
8. loja pública passa a usar o novo template.

## Preview

A V1 deve permitir preview simples.

Possíveis URLs:

```text
app.kriar.shop/layout/preview/classic
app.kriar.shop/layout/preview/modern
```

Ou:

```text
preview.kriar.shop/{store_slug}?template=classic
```

Para V1, o preview dentro do painel é suficiente.

## Cache e invalidação

Dados de tema podem ser cacheados.

Chaves possíveis:

```text
store:{store_id}:settings
store:{store_id}:theme
store:{store_id}:home
```

Quando mudar layout:

- limpar cache da loja;
- limpar home cacheada;
- limpar configurações de tema;
- forçar storefront a buscar nova configuração.

## Componentes da home

Na V1, a home pode ter:

- logo;
- menu;
- banner principal;
- texto principal;
- produtos em destaque;
- categorias;
- rodapé;
- dados de contato;
- links sociais.

## Página de produto

Deve mostrar:

- imagens;
- nome;
- preço;
- descrição;
- variações;
- disponibilidade;
- opções de entrega;
- indicação de produto personalizável, quando aplicável;
- botão comprar/adicionar ao carrinho;
- botão `Personalizar`, quando o produto tiver modelo 3D vinculado;
- produtos relacionados simples.

> **Faseamento:** na Fase 3 a página é **informativa** (imagem/nome/preço/descrição). A **ação de compra** (adicionar ao carrinho), a **disponibilidade** (estoque) e a **seleção de variação** chegam na **Fase 6** (venda sem pagamento) — o `cart_item`/`order_item` guarda a **variação escolhida**, e a vitrine precisa expor variações + estoque no `StorefrontProduct` (hoje só imagem/nome/preço/descrição). **Produtos relacionados** = follow-up; **`Personalizar`** = Fase 7. O botão flutuante de WhatsApp (contato, em toda a loja, `whatsapp_number`) já existe desde a Fase 3.

Se o produto for personalizável, o caminho principal deve ser `Personalizar`.
O cliente só deve adicionar ao carrinho depois de aprovar visualmente a arte.

## Editor de personalização 3D

O editor deve permitir personalização do produto usando modelo 3D.

Recursos (Fase 7 — editor 3D do storefront):

- carregar o modelo 3D **do catálogo da plataforma** (versão escolhida, CDN);
- **dois painéis**: edição 2D na área imprimível + preview 3D ao vivo (girar/zoom/mover) — doc [30 §2](./30_3d_customization_technical_design.md);
- upload de imagem/arte (raster) pelo cliente;
- escrever nomes e frases dentro da área personalizável;
- quando houver escrita, editar fonte, **cor do texto**, tamanho etc;
- mover arte e escrita dentro da área imprimível;
- ajustar escala;
- ajustar rotação;
- ver preview em tempo real;
- salvar sessão automaticamente;
- aprovar personalização antes de adicionar ao carrinho.

Exemplo de produtos:

- caneca;
- squeeze;
- camisa;
- ecobag;
- copo;
- placa;
- adesivo;
- outros podem surgir com o tempo.

A sessão salva permite que o cliente continue depois, especialmente quando tiver dúvida e conversar com a loja pelo WhatsApp.

O editor deve gerar ou salvar:

- parâmetros da personalização;
- imagem original enviada;
- preview da personalização;
- snapshot aprovado;
- versão do modelo 3D usado.

### Opções de entrega no produto

A página de produto deve deixar visível quais formas de entrega a loja oferece.

Opções esperadas na V1:

- frete fixo;
- frete grátis acima de valor mínimo;
- retirada local;
- entrega combinada.

Para entrega combinada, o texto deve explicar que a loja entrará em contato após a compra para combinar envio particular, como motoboy, 99, Uber ou serviço semelhante da região.
Essa opção é útil para clientes próximos da loja física, especialmente na mesma cidade, região metropolitana ou estado.

## Página de categoria

Deve mostrar:

- nome da categoria;
- lista paginada de produtos;
- filtros simples, se possível;
- ordenação simples.

## Carrinho

Deve mostrar:

- itens;
- **variação escolhida** (quando o produto tiver variações);
- quantidades;
- subtotal;
- cupom;
- frete estimado;
- opção de entrega escolhida;
- preview da personalização, se o item for personalizável;
- botão para checkout.

O carrinho deve funcionar sem login.
Antes do checkout, ele fica associado a uma sessão anônima com cookie seguro e validade de 30 dias.
Se o cliente voltar no mesmo navegador, o carrinho deve ser restaurado.

> **Carrinho de servidor (Fase 6):** o carrinho real vive em `cart_carts`/`cart_items` (servidor), chaveado pelo `guest_session_id` do cookie. Na Fase 3 a vitrine usa um carrinho **client** (localStorage) como placeholder; a Fase 6 o substitui pelo carrinho de servidor — drawer e checkout passam a ler a **mesma** fonte.

Depois que o cliente informar e-mail ou telefone, a loja pode enviar link seguro para continuar compra.

## Checkout

Pode ser parte do storefront.

Deve:

- coletar dados do cliente;
- coletar endereço;
- exibir frete;
- permitir entrega combinada quando habilitada pela loja;
- criar pedido pendente;
- anexar personalização aprovada ao pedido;
- redirecionar ou integrar provider de pagamento;
- aguardar confirmação por webhook.

Checkout não deve exigir senha ou cadastro prévio.
Ao preencher dados de contato, o sistema cria ou atualiza o customer daquela loja.

Quando o cliente escolher entrega combinada, o checkout deve mostrar uma mensagem clara:

```text
A loja entrará em contato após a compra para combinar a entrega.
```

> **Sem pagamento online (Fase 6):** na venda sem pagamento, o checkout **cria o pedido pendente** e segue direto para a **confirmação** — sem redirecionar/integrar provider nem esperar webhook (isso é a Fase 8). A confirmação mostra o **número do pedido**, as **políticas da loja** (troca/devolução/privacidade) e um **handoff por WhatsApp** com a mensagem pré-preenchida (pedido + itens) para combinar o pagamento. Ver [11 — Venda sem gateway (MVP local — Fase 6)](11_checkout_payments_and_split.md).

## Decisão canônica

A V1 terá 2 templates prontos e suporte a produtos personalizáveis em 3D. O lojista poderá escolher o template no painel, visualizar preview e aplicar. Produtos comuns usam fotos normais. Produtos personalizáveis abrem editor 3D no storefront, salvam a sessão do cliente e congelam a arte aprovada no pedido.
