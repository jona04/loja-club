# Security Strategy

## Objetivo

A Loja Club será uma plataforma multi-tenant de ecommerce. Segurança é crítica porque o sistema lidará com:

- dados de lojistas;
- dados de clientes finais;
- pedidos;
- endereços;
- transações;
- arquivos de personalização enviados por clientes;
- modelos 3D;
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
11. Arte enviada por cliente deve ser privada por padrão.
12. Registros de negócio devem usar soft delete.

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

Imagens, artes de personalização e modelos 3D devem ir para S3.

Não salvar arquivos no backend.

## Personalização 3D

Arquivos de personalização são sensíveis porque podem conter marcas, imagens pessoais, logos de clientes ou material comercial.

Regras:

- validar upload do cliente;
- separar arquivos por `store_id`;
- usar URLs assinadas para arquivos privados;
- não expor arquivo original em URL pública permanente;
- limitar tamanho e quantidade por sessão;
- registrar acesso do lojista a arquivos enviados pelo cliente;
- congelar a personalização aprovada no pedido;
- impedir que sessão editável altere pedido já criado.

Modelos 3D do lojista (por loja) podem ser públicos via CDN quando não contiverem dados sensíveis.
Arquivos enviados pelo cliente não devem seguir a mesma regra dos assets públicos.

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

**Como aplicamos (decidido):** o `.env` é **gitignored**; um `.env.example` (só placeholders, sem segredos) fica versionado como template. O CI roda `cp .env.example .env` (valores de dev/throwaway). No **deploy (Fase 7)** os segredos vêm de **GitHub Actions Secrets** → env vars e/ou **SSM/Secrets Manager**; em produção a credencial AWS é **IAM role** (sem chave longa). Realização do INV-S3.

## LGPD

A Loja Club lidará com dados pessoais.

Dados típicos:

- nome;
- e-mail;
- telefone;
- endereço;
- histórico de pedidos;
- dados de entrega.
- arquivos enviados em personalização.

Medidas necessárias:

- política de privacidade;
- base legal definida;
- controle de acesso;
- logs de ações sensíveis;
- anonimização quando aplicável;
- consentimentos quando necessários;
- minimização de dados.

## Auditoria

Registrar:

- login;
- falhas de login;
- alterações de produto;
- alteração de configuração de personalização;
- acesso a arte enviada pelo cliente;
- alteração de preço;
- alteração de conta de pagamento;
- alteração de domínio;
- convite/remoção de usuário;
- alteração de permissão;
- cancelamento de pedido;
- reembolso;
- acesso de suporte.

## Soft delete

Não usar hard delete para registros de negócio.

Exemplos:

- produto arquivado;
- loja arquivada;
- domínio arquivado;
- cupom arquivado;
- customer arquivado;
- sessão expirada.

Isso permite auditoria, investigação de suporte e recuperação quando necessário.

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

A segurança da Loja Club depende principalmente de isolamento por `store_id`, permissões fortes no backend, validação de webhooks, não armazenar dados sensíveis de pagamento, auditoria, gestão segura de segredos e tratamento privado dos arquivos de personalização.
