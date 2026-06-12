# Multitenancy and Domains

## Decisão principal

A Kriar será multi-tenant por loja.

Cada loja será um tenant.

A estratégia inicial será:

```text
banco compartilhado + coluna store_id nas tabelas comerciais
```

Não haverá banco separado por loja na V1.

## Conceito central

O modelo correto é:

```text
usuário acessa loja
loja tem produtos
loja tem pedidos
loja tem clientes
loja tem personalizações
```

E não:

```text
usuário tem produtos
```

Isso permite:

- um usuário gerenciar várias lojas;
- uma loja ter vários usuários;
- permissões diferentes por loja;
- dados separados por `store_id`.

## Entidades principais

| Entidade | Função |
|---|---|
| `User` | Pessoa que acessa a plataforma |
| `Store` | Loja/tenant |
| `StoreMember` | Ligação entre usuário e loja |
| `Role` | Papel do usuário dentro da loja |
| `Permission` | Permissão granular |
| `DomainHost` | Domínio/subdomínio da loja |

## Resolução da loja pelo domínio

Quando alguém acessa uma loja pública, o sistema precisa identificar a loja pelo domínio.

Exemplo:

```text
Host: empresaexemplo.kriar.shop
```

Fluxo:

1. Requisição chega no storefront.
2. O storefront/backend lê o `Host`.
3. Busca na tabela `domain_hosts`.
4. Encontra o `store_id`.
5. Carrega dados públicos daquela loja.
6. Toda consulta usa aquele `store_id`.

## Tabela domain_hosts

Uma mesma loja pode ter mais de um host.

Exemplo:

```text
brindesfortaleza.kriar.shop
www.brindesfortaleza.com.br
brindesfortaleza.com.br
```

A V1 não terá conceito de domínio principal.
Qualquer host ativo ligado à loja deve renderizar a mesma loja.

Campos sugeridos:

| Campo | Descrição |
|---|---|
| `id` | Identificador |
| `store_id` | Loja dona do domínio |
| `host` | Exemplo: `empresa.kriar.shop` |
| `type` | `platform_subdomain` ou `custom_domain` |
| `status` | `pending`, `active`, `failed`, `blocked` |
| `ssl_status` | `pending`, `issued`, `failed` |
| `verified_at` | Data de verificação |
| `created_at` | Criação |
| `updated_at` | Atualização |
| `deleted_at` | Arquivamento/remoção lógica |

## Subdomínio automático

Na V1, todo lojista deve receber um subdomínio automático.

Exemplo:

```text
minhaloja.kriar.shop
```

O DNS deve ser configurado com wildcard uma única vez:

```text
*.kriar.shop -> aponta para a entrada da plataforma
```

Com isso, a plataforma não precisa criar DNS manualmente para cada loja.

Quando o lojista cria uma loja:

1. escolhe slug/subdomínio;
2. backend verifica disponibilidade;
3. backend salva domínio no banco;
4. loja fica disponível imediatamente;
5. Traefik/ALB/CloudFront envia a requisição para o storefront;
6. storefront identifica a loja pelo `Host`.

## Exemplo de criação de subdomínio

Loja:

```text
id: 123
name: Empresa Exemplo
slug: empresaexemplo
```

Domínio:

```text
store_id: 123
host: empresaexemplo.kriar.shop
type: platform_subdomain
status: active
```

## Domínio próprio

Na V1, domínio próprio pode ser implementado se não atrasar muito. Caso contrário, pode ser controlado manualmente no começo.

Fluxo ideal:

1. Lojista informa `www.empresa.com.br`.
2. Plataforma salva domínio como pendente.
3. Plataforma mostra instrução de DNS.
4. Lojista cria CNAME apontando para a Kriar.
5. Plataforma verifica DNS.
6. Plataforma ativa domínio.
7. Plataforma emite/associa certificado.
8. Domínio passa a renderizar a loja.

Exemplo:

```text
www.empresa.com.br CNAME custom.kriar.shop
```

## Traefik e wildcard

No desenvolvimento local/dev, Traefik pode rotear:

```text
api.kriar.shop        -> backend-api
app.kriar.shop        -> frontend-dashboard
admin.kriar.shop      -> frontend-admin
*.kriar.shop          -> frontend-storefront
```

Traefik não precisa saber quais lojas existem. Ele só roteia qualquer subdomínio para o storefront.

A existência da loja é validada pelo banco.

## Loja não encontrada

Se o domínio não existir ou estiver inativo, o storefront deve mostrar uma página amigável:

```text
Loja não encontrada.
Verifique o endereço ou entre em contato com o lojista.
```

Não deve vazar informação interna.

## Regras de segurança multi-tenant

Toda consulta comercial deve usar `store_id`.

Errado:

```text
buscar produto por product_id
```

Certo:

```text
buscar produto por store_id + product_id
```

Ou:

```text
buscar produto por store_id + slug
```

Isso se aplica a:

- produtos;
- categorias;
- clientes;
- pedidos;
- carrinhos;
- sessões de personalização;
- cupons;
- frete;
- pagamentos;
- imagens;
- páginas;
- templates;
- configurações;
- equipe.

## Cache de domínio

A resolução de domínio deve ser cacheada.

Chaves possíveis:

```text
domain:{host}
store:{store_id}:settings
store:{store_id}:theme
```

Quando um domínio for alterado, o cache deve ser invalidado.

## Decisão canônica

Subdomínios das lojas serão criados automaticamente no banco. O DNS wildcard fará todo subdomínio cair na plataforma. O storefront detectará a loja pelo `Host` da requisição e todas as consultas serão filtradas por `store_id`.
