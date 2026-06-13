# Observability and Operations

## Objetivo

A Kriar precisa ter visibilidade operacional desde a V1.

Não basta o sistema funcionar localmente. É necessário saber quando:

- checkout falhou;
- webhook não processou;
- API está lenta;
- banco está sobrecarregado;
- worker parou;
- e-mail não foi enviado;
- loja está com erro;
- pagamento está inconsistente.
- personalização 3D está falhando.

## Ferramentas sugeridas

| Necessidade | Ferramenta |
|---|---|
| Logs de infraestrutura | CloudWatch |
| Erros da aplicação | Sentry |
| Métricas AWS | CloudWatch Metrics |
| Alertas | CloudWatch Alarms |
| Uptime | Health checks externos |
| Auditoria de negócio | Tabela `audit_logs` |

## Logs

Logs devem ser estruturados quando possível.

Campos úteis:

- request id;
- user id;
- store id;
- endpoint;
- status code;
- latency;
- error type;
- provider de pagamento;
- order id;
- payment transaction id.
- customization session id.

## Health checks

Criar endpoints:

```text
/health
/health/db
/health/redis
```

O health check público pode ser simples. Health checks internos podem validar dependências.

## Métricas críticas

### API

- taxa de erro 500;
- latência média;
- p95/p99 de latência;
- requisições por minuto;
- endpoints mais lentos.

### Checkout

- pedidos criados;
- pedidos pendentes;
- pagamentos aprovados;
- pagamentos recusados;
- falhas ao chamar provider de pagamento;
- tempo entre pedido e confirmação.

### Personalização 3D

- sessões iniciadas;
- sessões aprovadas;
- sessões abandonadas;
- uploads com erro;
- tempo médio até aprovação;
- falhas ao carregar modelo 3D;
- falhas ao salvar sessão;
- pedidos com produto personalizado.

### Webhooks

- eventos recebidos;
- eventos processados;
- eventos duplicados;
- eventos com falha;
- eventos pendentes há muito tempo.

### Banco

- conexões ativas;
- CPU;
- storage;
- queries lentas;
- locks;
- crescimento das tabelas.

### Worker

- tamanho da fila;
- jobs processados;
- jobs falhos;
- tempo médio de execução;
- e-mails enfileirados / enviados / falhos (todo e-mail é disparado pelo worker — INV-F5).

> Inspeção da fila no dev (Redis Insight / `redis-cli`, chaves `arq:*`, `arq:queue:health-check`): ver [`backend/README.md`](../backend/README.md).

### CDN/S3

- tráfego;
- erros 4xx/5xx;
- cache hit ratio;
- volume de storage.

## Alertas iniciais

Alertas recomendados:

- API com erro 5xx acima de limite;
- latência alta no checkout;
- fila acumulando;
- webhooks falhando;
- RDS com CPU alta;
- RDS com pouco storage;
- backend reiniciando frequentemente;
- worker indisponível;
- certificado perto de expirar;
- taxa de pagamento com erro incomum.
- falhas de upload de personalização acima de limite;
- falhas de carregamento de modelos 3D acima de limite.

## Auditoria operacional

A tabela `audit_logs` deve registrar ações importantes de negócio.

Exemplos:

- alteração de preço;
- alteração de modelo 3D vinculado ao produto;
- acesso a arquivo de personalização;
- alteração de provider de pagamento;
- reembolso;
- cancelamento de pedido;
- bloqueio de loja;
- admin acessando loja em suporte;
- alteração de permissão.

## Suporte ao lojista

O admin interno deve permitir investigar:

- status da loja;
- status do domínio;
- últimos pedidos;
- últimas personalizações;
- últimos webhooks;
- status do provider de pagamento;
- logs de erro relevantes;
- ações recentes da equipe.

## Retenção de logs

Definir retenção para evitar custo excessivo.

Exemplo inicial:

- logs de aplicação: 14 a 30 dias;
- auditoria de negócio: manter por mais tempo;
- webhooks: manter histórico suficiente para suporte;
- payloads sensíveis devem ser minimizados.

## Operações manuais permitidas

Na V1, algumas operações podem ser manuais pelo admin:

- bloquear loja;
- desbloquear loja;
- reenviar notificação;
- reprocessar webhook;
- marcar domínio para reverificação;
- suspender loja por risco;
- ajustar plano em casos especiais.

Todas devem gerar auditoria.

## Decisão canônica

A V1 precisa ter logs, Sentry, CloudWatch, health checks, auditoria de negócio e visibilidade específica para checkout, personalização 3D, pagamentos e webhooks.
