# Storefront and Layouts

## Objetivo

O storefront é a loja pública do lojista.

Ele será acessado por subdomínio ou domínio próprio.

Além das páginas tradicionais de ecommerce, o storefront deve suportar produtos personalizáveis em 3D para lojas de brindes, gráficas e comunicação visual.

Exemplos:

```text
brindesfortaleza.loja.club
presentescriativos.loja.club
www.minhaloja.com.br
```

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

1. usuário acessa `empresa.loja.club`;
2. storefront lê o host;
3. consulta backend ou cache;
4. backend busca em `domains`;
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

## Configuração no banco

Tabelas:

```text
theme_templates
store_theme_settings
```

### theme_templates

Templates globais.

Campos sugeridos:

| Campo | Descrição |
|---|---|
| `id` | `classic`, `modern` |
| `name` | Nome exibido |
| `description` | Descrição |
| `is_active` | Se está disponível |
| `preview_image_url` | Imagem de preview |

### store_theme_settings

Configuração da loja.

Campos sugeridos:

| Campo | Descrição |
|---|---|
| `store_id` | Loja |
| `active_template_id` | Template ativo |
| `logo_url` | Logo |
| `banner_image_url` | Banner principal |
| `headline` | Texto principal |
| `description` | Descrição da home |
| `featured_collection_id` | Coleção em destaque |
| `primary_color` | Preparado para futuro |
| `background_color` | Preparado para futuro |
| `font_family` | Preparado para futuro |

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
app.loja.club/layout/preview/classic
app.loja.club/layout/preview/modern
```

Ou:

```text
preview.loja.club/{store_slug}?template=classic
```

Para V1, o preview dentro do painel é suficiente.

## Cache e invalidação

Dados de tema podem ser cacheados.

Chaves possíveis:

```text
storefront:store:{store_id}:settings
storefront:store:{store_id}:theme
storefront:store:{store_id}:home
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

Se o produto for personalizável, o caminho principal deve ser `Personalizar`.
O cliente só deve adicionar ao carrinho depois de aprovar visualmente a arte.

## Editor de personalização 3D

O editor deve permitir personalização do produto usando modelo 3D.

Recursos da V1:

- carregar modelo 3D publicado pela Loja Club;
- upload de imagem/arte pelo cliente;
- escrever nomes e frases dentro da area personalizável;
- quando houver escrita permitir editar fonte, cores, tamanho e etc;
- escolha de cor do produto quando o modelo permitir;
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
- quantidades;
- subtotal;
- cupom;
- frete estimado;
- opção de entrega escolhida;
- preview da personalização, se o item for personalizável;
- botão para checkout.

## Checkout

Pode ser parte do storefront.

Deve:

- coletar dados do cliente;
- coletar endereço;
- exibir frete;
- permitir entrega combinada quando habilitada pela loja;
- criar pedido pendente;
- anexar personalização aprovada ao pedido;
- redirecionar ou integrar gateway;
- aguardar confirmação por webhook.

Quando o cliente escolher entrega combinada, o checkout deve mostrar uma mensagem clara:

```text
A loja entrará em contato após a compra para combinar a entrega.
```

## Decisão canônica

A V1 terá 2 templates prontos e suporte a produtos personalizáveis em 3D. O lojista poderá escolher o template no painel, visualizar preview e aplicar. Produtos comuns usam fotos normais. Produtos personalizáveis abrem editor 3D no storefront, salvam a sessão do cliente e congelam a arte aprovada no pedido.
