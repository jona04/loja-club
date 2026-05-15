# Checkout, Payments and Split

## Decisão principal

A Loja Club não vai reter dinheiro.

O gateway de pagamento será responsável por:

- receber o pagamento;
- processar cartão/Pix/boleto;
- aplicar antifraude, se houver;
- fazer split;
- repassar a parte do lojista;
- repassar a comissão da Loja Club;
- lidar com cadastro financeiro do recebedor.

## Gateways candidatos

Gateways possíveis para a V1:

- Pagar.me;
- Mercado Pago;
- Asaas.

Sugestão inicial:

- Pagar.me se o foco for split/marketplace mais flexível;
- Mercado Pago se o foco for confiança popular e conversão no Brasil.

## Modelo de split

Exemplo:

```text
Venda: R$ 100,00
Taxa do gateway: R$ 4,00
Comissão Loja Club: R$ 3,00
Lojista: R$ 93,00
```

A comissão da Loja Club será definida pelo plano da loja.

## Fluxo de checkout

1. Cliente adiciona produtos ao carrinho.
2. Cliente inicia checkout.
3. Sistema valida estoque e valores.
4. Sistema cria pedido pendente.
5. Sistema cria transação/cobrança no gateway.
6. Gateway processa pagamento.
7. Gateway aplica split.
8. Gateway envia webhook.
9. Backend valida webhook.
10. Backend atualiza transação.
11. Backend atualiza pedido.
12. Cliente e lojista recebem notificação.

## Pedido pendente

Antes de chamar o gateway, a Loja Club deve criar um pedido com status:

```text
pending_payment
```

Esse pedido precisa registrar:

- loja;
- cliente;
- endereço;
- itens;
- preços no momento da compra;
- frete;
- desconto;
- total;
- status.

## Confirmação por webhook

A confirmação real do pagamento deve vir do webhook.

Não confiar apenas no retorno do navegador do cliente.

Motivo:

- cliente pode fechar a aba;
- redirect pode falhar;
- gateway pode demorar;
- Pix/boleto podem ser assíncronos;
- antifraude pode mudar status depois.

## Webhook idempotente

Webhooks podem chegar mais de uma vez.

A tabela `payment_webhooks` deve registrar eventos processados.

Campos sugeridos:

| Campo | Descrição |
|---|---|
| `gateway_event_id` | ID único do evento |
| `gateway` | Pagar.me/Mercado Pago/etc. |
| `event_type` | Tipo de evento |
| `payload` | Conteúdo bruto ou seguro |
| `processed_at` | Quando foi processado |
| `status` | `received`, `processed`, `failed` |

Regra:

```text
Se gateway_event_id já foi processado, não processar novamente.
```

## Status de pagamento

| Status | Significado |
|---|---|
| `created` | Criado |
| `pending` | Aguardando |
| `authorized` | Autorizado |
| `paid` | Pago |
| `refused` | Recusado |
| `canceled` | Cancelado |
| `refunded` | Reembolsado |
| `chargeback` | Contestação |

## Status do pedido

Pedido e pagamento são coisas separadas.

| Pedido | Pagamento |
|---|---|
| `pending_payment` | `pending` |
| `paid` | `paid` |
| `payment_failed` | `refused` |
| `processing` | `paid` |
| `shipped` | `paid` |
| `refunded` | `refunded` |
| `chargeback` | `chargeback` |

## Conta de pagamento do lojista

Cada loja precisa ter uma conta/recebedor no gateway.

Tabela:

```text
payment_accounts
```

Campos sugeridos:

| Campo | Descrição |
|---|---|
| `store_id` | Loja |
| `gateway` | Gateway usado |
| `gateway_recipient_id` | ID do recebedor |
| `status` | `pending`, `active`, `blocked`, `rejected` |
| `kyc_status` | Status do cadastro |
| `metadata` | Dados adicionais |

## Configuração do painel

No módulo Pagamentos, o lojista verá:

```text
Status da conta: Ativa / Em análise / Bloqueada
Gateway: Pagar.me
Métodos ativos: Pix, Cartão, Boleto
Recebedor: rec_xxx
```

## Métodos de pagamento

A V1 deve tentar suportar:

- Pix;
- cartão de crédito;
- boleto, se fizer sentido para o público.

Cartão parcelado pode ser suportado, mas deve ser configurado com cuidado por causa das taxas.

## Comissão da Loja Club

A comissão deve vir do plano.

Exemplo:

```text
Starter: 3%
Pro: 1,5%
Business: 0,5%
```

O lojista não deve configurar essa comissão.

## Reembolso

Na V1, o reembolso deve ser tratado com cuidado.

Regras:

- só usuário com permissão pode reembolsar;
- registrar auditoria;
- chamar gateway;
- atualizar transação;
- atualizar pedido;
- notificar cliente/lojista quando necessário.

## Chargeback

Chargeback é risco comercial do lojista.

A Loja Club pode:

- registrar o evento;
- exibir alerta;
- permitir resposta, se o gateway suportar;
- bloquear loja com chargeback excessivo.

## Segurança de webhook

Todo webhook deve validar:

- assinatura do gateway;
- origem esperada;
- idempotência;
- payload mínimo;
- transação pertencente à loja;
- status válido.

## Responsabilidade

| Problema | Responsável principal |
|---|---|
| Cartão recusado | Banco/gateway/cliente |
| Pix não pago | Cliente/gateway |
| Gateway indisponível | Gateway |
| Produto não entregue | Lojista |
| Produto com defeito | Lojista |
| Checkout da plataforma fora do ar | Loja Club |
| Erro técnico no sistema | Loja Club |

## Decisão canônica

A V1 usará gateway com split. A Loja Club não reterá valores. O checkout criará pedido pendente, enviará a cobrança ao gateway e só marcará pagamento como confirmado após webhook validado e idempotente.
