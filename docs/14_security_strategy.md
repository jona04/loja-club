# Security Strategy

## Objetivo

A Loja Club será uma plataforma multi-tenant de ecommerce. Segurança é crítica porque o sistema lidará com:

- dados de lojistas;
- dados de clientes finais;
- pedidos;
- endereços;
- transações;
- permissões;
- domínios;
- webhooks de pagamento.

## Princípios de segurança

1. Isolamento entre lojas é obrigatório.
2. Toda consulta comercial deve filtrar por `store_id`.
3. Frontend esconder botão não é segurança.
4. Backend deve validar permissão em toda ação crítica.
5. Webhooks devem ser validados e idempotentes.
6. A Loja Club não deve armazenar cartão.
7. Segredos não devem ficar no código.
8. Uploads devem ser validados.
9. Ações sensíveis devem gerar auditoria.
10. Admins internos devem ter acesso controlado.

## Autenticação

A V1 usará autenticação baseada no template FastAPI.

Deve suportar:

- login;
- logout;
- recuperação de senha;
- confirmação de e-mail, se possível;
- tokens seguros;
- expiração de sessão;
- proteção contra brute force.

## Autorização por loja

Toda rota de loja deve validar:

1. usuário autenticado;
2. usuário pertence à loja;
3. usuário tem permissão;
4. recurso pertence à loja.

Exemplo:

```text
PUT /stores/{store_id}/products/{product_id}
```

Valida:

```text
StoreMember existe?
Permissão catalog.product.update existe?
Product.store_id == store_id?
```

## Multi-tenant isolation

Erro grave a evitar:

```text
buscar recurso apenas por id
```

Sempre usar:

```text
store_id + resource_id
```

Ou:

```text
store_id + slug
```

## Permissões

Permissões devem ser verificadas no backend.

Frontend apenas melhora UX.

## Admin da plataforma

Admins internos da Loja Club precisam de permissões globais.

Ações sensíveis devem gerar auditoria:

- acessar loja em modo suporte;
- bloquear loja;
- desbloquear loja;
- alterar plano;
- alterar status de pagamento;
- alterar domínio;
- acessar dados sensíveis.

## Upload de arquivos

Uploads devem validar:

- tipo de arquivo;
- tamanho máximo;
- extensão;
- MIME type;
- conteúdo suspeito;
- limite por plano;
- quantidade por produto.

Imagens devem ir para S3.

Não salvar arquivos no backend.

## Pagamentos

A Loja Club não deve armazenar cartão.

Dados sensíveis de pagamento devem ficar no gateway.

Backend deve armazenar apenas:

- ID da transação no gateway;
- status;
- valores;
- método;
- recebedor;
- metadados mínimos;
- eventos de webhook.

## Webhooks

Webhooks devem validar:

- assinatura;
- origem;
- evento duplicado;
- transação existente;
- pertencimento à loja;
- status esperado;
- ordem de eventos quando necessário.

## Rate limit

Adicionar rate limit para:

- login;
- recuperação de senha;
- checkout;
- criação de conta;
- APIs públicas sensíveis;
- webhooks, quando fizer sentido sem bloquear gateway.

## Segredos

Segredos devem ficar em:

- AWS Secrets Manager;
- SSM Parameter Store;
- variáveis de ambiente seguras no ambiente local.

Não commitar:

- chaves do gateway;
- secrets JWT;
- senhas do banco;
- tokens AWS;
- SMTP credentials;
- Sentry DSN privado, se sensível.

## LGPD

A Loja Club lidará com dados pessoais.

Dados típicos:

- nome;
- e-mail;
- telefone;
- endereço;
- histórico de pedidos;
- dados de entrega.

Medidas necessárias:

- política de privacidade;
- base legal definida;
- controle de acesso;
- logs de ações sensíveis;
- exclusão/anonymização quando aplicável;
- consentimentos quando necessários;
- minimização de dados.

## Auditoria

Registrar:

- login;
- falhas de login;
- alterações de produto;
- alteração de preço;
- alteração de conta de pagamento;
- alteração de domínio;
- convite/remoção de usuário;
- alteração de permissão;
- cancelamento de pedido;
- reembolso;
- acesso de suporte.

## Backups

Banco deve ter backup automático.

Também deve haver plano de restauração testado.

## Headers e HTTPS

Produção deve exigir HTTPS.

Adicionar headers de segurança quando aplicável:

- HSTS;
- X-Frame-Options ou CSP adequada;
- X-Content-Type-Options;
- política de CORS restrita;
- cookies seguros, se usados.

## CORS

Permitir apenas origens esperadas:

```text
app.loja.club
admin.loja.club
*.loja.club
loja.club
```

Cuidado com wildcard amplo em APIs autenticadas.

## Decisão canônica

A segurança da Loja Club depende principalmente de isolamento por `store_id`, permissões fortes no backend, validação de webhooks, não armazenar dados sensíveis de pagamento, auditoria e gestão segura de segredos.
