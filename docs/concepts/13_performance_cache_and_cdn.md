# Performance, Cache and CDN

## Objetivo

A Kriar precisa suportar várias lojas usando a mesma infraestrutura, sem ficar lenta.

A performance virá de:

- banco bem modelado;
- índices por `store_id`;
- cache;
- CDN;
- imagens otimizadas;
- modelos 3D otimizados;
- filas assíncronas;
- paginação;
- separação entre vitrine pública e operações administrativas.

## Princípios

1. A loja pública precisa ser muito rápida.
2. O painel administrativo pode tolerar consultas um pouco mais pesadas.
3. Imagens nunca devem ser servidas diretamente pelo backend.
4. Tarefas pesadas não devem rodar dentro da requisição.
5. Relatórios não devem impactar checkout ou vitrine.
6. Toda query comercial deve usar `store_id`.
7. Modelos 3D devem ser otimizados para web antes de publicação.

## Cache com Redis

Redis será usado para:

- domínio -> loja;
- configurações da loja;
- tema ativo;
- menus;
- categorias;
- produtos públicos;
- homepage;
- rate limit;
- locks de checkout;
- sessões temporárias;
- sessões de personalização;
- fila leve se necessário.

## Chaves de cache sugeridas

```text
domain:{host}
store:{store_id}:settings
store:{store_id}:theme
store:{store_id}:home
store:{store_id}:categories
store:{store_id}:product:{slug}
store:{store_id}:menu
customization_session:{session_id}
product_3d_model:{model_id}:{version_id}
```

## Invalidação de cache

Quando alterar produto:

```text
limpar produto específico
limpar lista de categoria
limpar home, se produto for destaque
```

Quando alterar layout:

```text
limpar store:{store_id}:theme
limpar store:{store_id}:home
limpar store:{store_id}:settings
```

Quando alterar domínio:

```text
limpar domain:{host}
```

## CDN

CloudFront deve entregar:

- imagens;
- modelos 3D públicos;
- texturas públicas;
- thumbnails;
- banners;
- logos;
- assets estáticos;
- possivelmente storefront público.

## Imagens

Fluxo de imagem:

1. lojista faz upload;
2. backend valida tipo/tamanho;
3. imagem original vai para S3;
4. worker gera versões otimizadas;
5. versões otimizadas vão para S3;
6. CloudFront entrega ao cliente final.

Versões sugeridas:

| Versão | Uso |
|---|---|
| `thumbnail` | miniaturas |
| `card` | cards de vitrine |
| `product` | página do produto |
| `zoom` | imagem ampliada |

## O que não fazer

Não servir imagem do backend.

Não salvar imagem no banco.

Não carregar imagem original gigante na vitrine.

Não processar imagem dentro da requisição principal.

## Modelos 3D

Modelos 3D devem ser preparados para web.

Cuidados:

- usar formato otimizado, preferencialmente GLB;
- limitar tamanho do arquivo;
- comprimir texturas;
- versionar modelos;
- servir assets públicos por CDN;
- cachear por versão do modelo;
- evitar carregar editor 3D em produto que não é personalizável.

Arquivos enviados pelo cliente para personalização não devem ser tratados como assets públicos permanentes.
Devem usar URLs assinadas quando forem acessados pelo lojista ou pelo próprio cliente.

## Fila assíncrona

Tarefas para fila:

- geração de thumbnails;
- geração de previews/snapshots de personalização, se feita no backend;
- limpeza de sessões de personalização expiradas;
- envio de e-mail;
- processamento de webhook;
- atualização de relatório;
- limpeza de carrinhos abandonados;
- sincronização com gateway;
- rotinas de assinatura;
- invalidação de caches pesados.

## Paginação

Toda lista precisa ser paginada.

Exemplos:

- produtos;
- pedidos;
- clientes;
- transações;
- logs;
- webhooks;
- cupons.

## Índices

A performance começa no banco.

Esta seção lista índices principais de performance.
A lista completa fica em [Database Strategy](./07_database_strategy.md).

- `store_id + slug` em produtos;
- `store_id + status` em produtos/pedidos;
- `store_id + product_id + status` em sessões de personalização;
- `store_id + created_at` em pedidos;
- `store_id + customer_id` em pedidos;
- `host` em domínios;
- `gateway_event_id` em webhooks.

## Checkout

Checkout deve ser rápido e seguro.

Cuidados:

- validar estoque no momento da criação do pedido;
- validar personalização aprovada antes de criar pedido;
- evitar chamadas externas desnecessárias antes de criar pedido;
- usar locks quando necessário;
- não processar pagamento sem pedido pendente;
- confiar na confirmação via webhook.

## Relatórios

Relatórios devem ser simples na V1.

Relatórios pesados devem ser:

- pré-calculados;
- cacheados;
- processados por worker;
- filtrados por período.

## Escalabilidade horizontal

Backend e frontends devem ser stateless.

Estado fica em:

- PostgreSQL;
- Redis;
- S3;
- gateway;
- fila.

Assim, é possível subir mais containers para atender mais tráfego.

## Decisão canônica

A performance da V1 será garantida por PostgreSQL bem indexado, Redis para cache, S3/CloudFront para imagens e modelos 3D, fila assíncrona para tarefas pesadas e frontends stateless escaláveis em containers.
