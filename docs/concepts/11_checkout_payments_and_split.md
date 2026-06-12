# Checkout, Payments and Split

## Decisão principal

A Kriar não vai reter dinheiro.

O gateway de pagamento será responsável por:

- receber o pagamento;
- processar cartão/Pix/boleto;
- aplicar antifraude, se houver;
- fazer split;
- repassar a parte do lojista;
- repassar a comissão da Kriar;
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
Comissão Kriar: R$ 3,00
Lojista: R$ 93,00
```

A comissão da Kriar será definida pelo plano da loja.

## Fluxo de checkout

1. Cliente adiciona produtos ao carrinho.
2. Se houver produto personalizável, cliente aprova a personalização antes do checkout.
3. Cliente inicia checkout.
4. Sistema valida estoque, valores e personalizações aprovadas.
5. Cliente escolhe forma de entrega.
6. Cliente informa contato e endereço sem criar senha.
7. Sistema cria ou atualiza customer da loja.
8. Sistema cria pedido pendente.
9. Sistema congela a personalização nos itens do pedido.
10. Sistema cria transação/cobrança no gateway.
11. Gateway processa pagamento.
12. Gateway aplica split.
13. Gateway envia webhook.
14. Backend valida webhook.
15. Backend atualiza transação.
16. Backend atualiza pedido.
17. Cliente e lojista recebem notificação.

## Pedido pendente

Antes de chamar o gateway, a Kriar deve criar um pedido com status:

```text
pending_payment
```

Esse pedido precisa registrar:

- loja;
- cliente;
- guest session, se a compra começou anônima;
- endereço;
- itens;
- preços no momento da compra;
- personalizações aprovadas;
- frete;
- método de entrega;
- desconto;
- total;
- status.

## Venda sem gateway (MVP local — Fase 6)

Antes de o gateway entrar (Fase 8), a V1 **vende sem pagamento online**. O checkout vai até o **pedido pendente** e para — não há chamada de gateway, split nem webhook. O pagamento é **combinado fora da plataforma**.

Diferenças em relação ao fluxo com gateway:

- o fluxo de checkout termina em **criar pedido `pending_payment`** (passos 1–9); os passos de gateway/webhook (10–16) **não rodam**;
- **número do pedido:** todo pedido recebe um identificador **sequencial por loja** (ex.: `#1001`), exibido ao cliente e ao lojista (confirmação, e-mail, painel) — é a referência que ambos usam para combinar entrega/pagamento;
- **baixa de estoque:** ao criar o pedido, o estoque dos itens é **decrementado** em `catalog_inventory_items`; **cancelar** o pedido **devolve** o estoque. Sem reserva intermediária no V1 — valida + decrementa na criação (a unicidade `store_id+product_id+variant_id` evita linha duplicada e corrida de upsert);
- **pagamento combinado fora da plataforma:** a confirmação explica como combinar (Pix/transferência/WhatsApp/entrega combinada). O caminho primário é um **handoff por WhatsApp**: um botão que abre o WhatsApp da loja (`whatsapp_number` de `store_settings`) com mensagem **pré-preenchida** contendo o **número do pedido** e o resumo dos itens, para o cliente combinar o pagamento direto com a loja;
- **marcar pago manualmente:** enquanto não há gateway, o lojista marca o pagamento como recebido no painel (`pending_payment → paid`). **Nenhum pedido vira pago sozinho**;
- **políticas da loja:** o checkout exibe/linka as políticas de **troca/devolução/privacidade** da loja (`checkout.policies.*`);
- **ponto de integração do gateway:** o módulo de pagamento expõe a **interface** (sem implementar) para a Fase 8 plugar o gateway aqui.

### Status do pedido nesta fase

Sem pagamento online, os status que a Fase 6 usa são operacionais:

```text
pending_payment → paid (marcado manualmente) → processing → shipped → delivered
                → canceled (quando permitido; devolve estoque)
```

Os status de gateway (`payment_failed`, `refunded`, `chargeback`) entram com o pagamento na **Fase 8**. Todo status precisa ser **lido em código** — a Fase 6 não cria status que ninguém usa.

## Produtos personalizáveis no checkout

Produtos personalizáveis em 3D só podem avançar para checkout quando a personalização estiver aprovada.

Regra:

```text
cart_item de produto image_3d_customizable exige customization_session status approved
```

Ao criar o pedido, o sistema deve copiar a personalização para o item do pedido.

Dados que devem ser congelados:

- modelo 3D usado;
- versão do modelo;
- JSON de parâmetros;
- imagem original enviada pelo cliente;
- preview renderizado;
- snapshot aprovado;
- data da aprovação.

Depois que o pedido for criado, alterações na sessão original não podem mudar o pedido.
Se o cliente quiser alterar a arte, deve gerar nova personalização ou novo item.

## Entrega combinada

A V1 deve suportar uma opção de entrega combinada.

Nome sugerido:

```text
private_delivery
```

Essa modalidade representa envio particular negociado entre cliente e loja depois da compra.

Exemplos:

- motoboy próprio;
- 99;
- Uber;
- aplicativo local de entrega;
- entrega manual combinada por telefone ou WhatsApp.

Regras:

- a loja decide se essa opção fica disponível;
- pode ser limitada por cidade, região ou estado;
- o checkout deve informar que a entrega será combinada após a compra;
- o pedido deve registrar que a entrega depende de contato com a loja;
- a Kriar não calcula automaticamente preço, prazo ou disponibilidade de aplicativos;
- a responsabilidade pela entrega continua sendo do lojista.

Essa opção permite vendas locais com mais flexibilidade, especialmente para lojas físicas que atendem clientes próximos.

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

## Comissão da Kriar

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

A Kriar pode:

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
| Arte personalizada enviada pelo cliente | Cliente/lojista, conforme termos |
| Produção diferente da arte aprovada | Lojista |
| Entrega combinada não realizada | Lojista |
| Checkout da plataforma fora do ar | Kriar |
| Erro técnico no sistema | Kriar |

## Decisão canônica

A V1 usará gateway com split. A Kriar não reterá valores. O checkout criará pedido pendente, congelará personalizações aprovadas, enviará a cobrança ao gateway e só marcará pagamento como confirmado após webhook validado e idempotente.
