# FastAPI Template Adaptation

## Base escolhida

A Loja Club V1 será construída a partir do **Full Stack FastAPI Template** oficial.

O template já traz uma base full-stack com:

- FastAPI;
- PostgreSQL;
- SQLModel;
- Pydantic;
- Alembic;
- JWT;
- recuperação de senha;
- e-mails;
- React;
- TypeScript;
- Vite;
- Tailwind;
- shadcn/ui;
- client gerado via OpenAPI;
- Docker Compose;
- Traefik;
- Adminer;
- Mailcatcher;
- Pytest;
- Playwright;
- GitHub Actions;
- Sentry.

## Decisão

Não vamos substituir o template por Django.

Motivos:

- o usuário já conhece e já usou esse template;
- acelera muito a base do projeto;
- encaixa bem em um produto API-first;
- facilita integração com frontend React;
- gera client baseado no OpenAPI;
- combina bem com checkout, gateways e webhooks;
- já vem com Docker e Traefik;
- é mais próximo do stack que será usado no produto.

## O que será mantido

Do template original, vamos manter:

- estrutura full-stack inicial;
- FastAPI;
- SQLModel inicialmente;
- PostgreSQL;
- Alembic;
- autenticação base;
- JWT;
- recuperação de senha;
- e-mails;
- Docker Compose;
- Traefik local/staging;
- frontend React/Vite para painel;
- Tailwind/shadcn;
- OpenAPI client gerado;
- testes backend;
- testes E2E;
- GitHub Actions;
- Sentry;
- Adminer e Mailcatcher apenas para desenvolvimento.

## O que será alterado

O template original é genérico. A Loja Club precisa de uma estrutura de SaaS multi-tenant.

Alterações principais:

1. Transformar backend em monólito modular.
2. Remover ou substituir exemplos genéricos como `items`.
3. Criar módulo de lojas/tenants.
4. Criar `store_id` nas entidades comerciais.
5. Criar permissões por loja.
6. Criar resolução de loja por domínio.
7. Separar painel do lojista de storefront público.
8. Adicionar gateway com split.
9. Adicionar worker/fila.
10. Adicionar upload para S3.
11. Adicionar CDN para imagens.
12. Adicionar admin interno da plataforma em frontend próprio.
13. Adicionar módulos de ecommerce.

## Estrutura backend desejada

Em vez de manter tudo em arquivos muito centralizados, o backend deve ser dividido em módulos.

Estrutura conceitual:

```text
backend/
  app/
    core/
    db/
    api/
    modules/
      accounts/
      stores/
      tenancy/
      domains/
      catalog/
      media/
      storefront/
      cart/
      checkout/
      payments/
      orders/
      customers/
      shipping/
      discounts/
      billing/
      notifications/
      audit/
      reports/
      platform_admin/
```

Cada módulo pode ter:

```text
models.py
schemas.py
routes.py
services.py
repositories.py
permissions.py
exceptions.py
```

## SQLModel

O template usa SQLModel. Para a V1, é aceitável manter SQLModel porque acelera o desenvolvimento e já está integrado ao template.

Cuidados:

- não deixar models gigantes em um único arquivo;
- separar por módulo;
- revisar relacionamentos complexos;
- usar Alembic com disciplina;
- criar índices desde o início;
- usar SQLAlchemy diretamente se algum caso complexo exigir.

## Frontend do template

O frontend original do template deve ser reaproveitado principalmente para o **painel do lojista**.

Ele já vem com:

- React;
- TypeScript;
- Vite;
- TanStack;
- Tailwind;
- shadcn/ui;
- client gerado pela API.

A loja pública deve ser um frontend separado.

O admin interno da Loja Club também deve ser um frontend separado do painel do lojista.
Ele pode reaproveitar componentes, client OpenAPI e padrões visuais, mas não deve morar no mesmo projeto do dashboard.

## Traefik no template

O Traefik será mantido para:

- desenvolvimento local;
- staging;
- beta barato em EC2;
- roteamento por subdomínio;
- simulação de URLs reais;
- roteamento de `api`, `app`, `admin` e `*.loja.club`.

Em produção AWS mais robusta, Traefik pode ser substituído por ALB/CloudFront/ACM.

## O que não usar em produção pública

Do template, os seguintes serviços não devem ficar expostos em produção:

- Adminer;
- Mailcatcher;
- Traefik dashboard;
- ferramentas de debug;
- endpoints internos sem autenticação.

## Estratégia de migração do template para Loja Club

1. Criar projeto a partir do template.
2. Ajustar nome, domínio, envs e branding.
3. Validar ambiente local.
4. Refatorar backend para módulos.
5. Criar entidades centrais: `Store`, `StoreMember`, `Domain`.
6. Criar middleware/contexto multi-tenant.
7. Adaptar autenticação para múltiplas lojas.
8. Criar permissões por loja.
9. Criar módulos de ecommerce.
10. Separar storefront em projeto próprio.
11. Criar admin interno em projeto frontend próprio.
12. Adicionar S3/CDN.
13. Adicionar Redis/fila.
14. Adicionar gateway com split.
15. Preparar staging com Traefik.
16. Preparar produção AWS.

## Decisão canônica

A Loja Club será construída com FastAPI usando o template como base, mas o template será profundamente adaptado para um SaaS multi-tenant de ecommerce.
