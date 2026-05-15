# Storefront and Layouts

## Objetivo

O storefront é a loja pública do lojista.

Ele será acessado por subdomínio ou domínio próprio.

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

Para acelerar a V1, é possível começar com React/Vite, mas a recomendação final para loja pública é Next.js.

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
        CategoryPage
        CartPage
        CheckoutPage
      modern/
        HomePage
        ProductPage
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
- botão comprar/adicionar ao carrinho;
- produtos relacionados simples.

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
- botão para checkout.

## Checkout

Pode ser parte do storefront.

Deve:

- coletar dados do cliente;
- coletar endereço;
- exibir frete;
- criar pedido pendente;
- redirecionar ou integrar gateway;
- aguardar confirmação por webhook.

## Decisão canônica

A V1 terá 2 templates prontos. O lojista poderá escolher o template no painel, visualizar preview e aplicar. Ao salvar, o storefront público deve refletir a alteração usando os dados da loja e o template ativo salvo no banco.
