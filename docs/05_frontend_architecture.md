# Frontend Architecture

## Decisão principal

A Loja Club terá três áreas de frontend:

1. Loja pública dos lojistas.
2. Painel do lojista.
3. Admin interno da plataforma.

Na V1, a recomendação é ter três projetos frontend principais:

```text
frontend-dashboard
frontend-admin
frontend-storefront
```

O `frontend-dashboard` atende apenas o painel do lojista.

O `frontend-admin` atende apenas o admin interno da Loja Club.

O `frontend-storefront` atende as lojas públicas dos lojistas.

## URLs

| Frontend | URL | Função |
|---|---|---|
| Site institucional | `loja.club` / `www.loja.club` | Página da própria Loja Club |
| Dashboard | `app.loja.club` | Painel do lojista |
| Admin | `admin.loja.club` | Admin interno da plataforma |
| Storefront | `*.loja.club` | Lojas públicas |
| API | `api.loja.club` | Backend FastAPI |

## Frontend dashboard

O dashboard é o painel usado pelo lojista.

URL:

```text
app.loja.club
```

Tecnologia recomendada:

- React;
- TypeScript;
- Vite;
- Tailwind;
- shadcn/ui;
- client gerado via OpenAPI;
- TanStack Query/Router, se mantido do template.

Responsabilidades:

- login;
- seleção de loja ativa;
- dashboard de vendas;
- produtos;
- pedidos;
- clientes;
- checkout;
- pagamentos;
- frete;
- layout da loja;
- cupons;
- relatórios;
- domínios;
- equipe;
- configurações;
- plano.

## Admin interno

O admin interno é o painel usado pela equipe Loja Club para operar a plataforma.

URL:

```text
admin.loja.club
```

Na V1, o admin deve ser um projeto separado:

```text
frontend-admin
```

Ele pode reutilizar componentes, client OpenAPI e padrões visuais do painel do lojista, mas deve ter build, rotas, deploy e permissões próprias.

Exemplo:

```text
admin.loja.club/stores
admin.loja.club/platform-users
admin.loja.club/webhooks
admin.loja.club/plans
```

Responsabilidades:

- ver todas as lojas;
- bloquear/desbloquear loja;
- ver usuários;
- ver pedidos por loja;
- ver volume transacionado;
- gerenciar planos;
- ver webhooks com erro;
- gerenciar templates/layouts;
- consultar logs de auditoria;
- suporte ao lojista.

## Storefront público

O storefront é a loja pública do lojista.

URLs:

```text
minhaloja.loja.club
empresaexemplo.loja.club
www.dominio-do-lojista.com.br
```

Responsabilidades:

- homepage;
- página de categoria;
- página de produto;
- carrinho;
- checkout;
- páginas institucionais;
- SEO;
- renderização do template escolhido;
- leitura de configurações públicas da loja;
- navegação rápida com cache/CDN.

Tecnologia recomendada:

- Next.js para storefront público.

Motivos:

- SEO;
- renderização server-side;
- possibilidade de cache;
- boa experiência em páginas públicas;
- melhor adequação para ecommerce público.

Alternativa para acelerar a V1:

- usar Vite também no storefront inicialmente.

Decisão recomendada:

- usar React/Vite do template para painel;
- usar React/Vite para admin interno em projeto separado;
- usar Next.js para loja pública.

## Containers frontend

No desenvolvimento/staging:

```text
frontend-dashboard
frontend-admin
frontend-storefront
```

Em produção:

```text
frontend-dashboard -> ECS/Fargate ou build estático
frontend-admin -> ECS/Fargate ou build estático
frontend-storefront -> ECS/Fargate
```

## Comunicação com backend

Todos os frontends conversam com:

```text
api.loja.club
```

O dashboard usa autenticação do usuário.

O admin interno usa autenticação de usuários internos da Loja Club e permissões globais da plataforma.

O storefront público usa APIs públicas, identificando a loja pelo domínio da requisição.

## Seleção de loja ativa no dashboard

Um usuário pode fazer parte de várias lojas.

Fluxo:

1. Usuário faz login.
2. Backend retorna as lojas em que ele é membro.
3. Se houver uma loja, o painel entra automaticamente nela.
4. Se houver várias, o painel mostra seletor de loja.
5. A loja ativa define o contexto das chamadas.

Exemplo de seletor:

```text
Loja atual: Brindes Fortaleza ▼
```

## Roteamento por permissão

O menu do painel deve ser dinâmico.

Um módulo só aparece se:

1. o plano da loja permite;
2. o usuário tem permissão para visualizar.

Exemplo:

- usuário sem `payments.view` não vê o módulo Pagamentos;
- usuário sem `layout.update` pode até visualizar layout, mas não salvar alterações;
- usuário sem `reports.view` não vê relatórios.

## Módulos do painel

Menu sugerido:

```text
Dashboard
Produtos
Pedidos
Clientes
Checkout
Pagamentos
Frete
Layout da Loja
Cupons
Relatórios
Domínios
Equipe
Configurações
Plano
```

## Admin e auditoria

Quando um usuário interno da Loja Club acessar dados de uma loja por suporte, isso deve gerar registro de auditoria.

Exemplo:

```text
Admin João acessou a Loja X em modo suporte às 14:32.
```

## Decisão canônica

A V1 terá `frontend-dashboard`, `frontend-admin` e `frontend-storefront` separados. O painel do lojista não deve morar no mesmo projeto frontend do admin da Loja Club.
