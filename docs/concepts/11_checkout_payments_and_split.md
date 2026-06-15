# Checkout, Payments and Split

## Decisão principal

A Kriar não vai reter dinheiro.

A Kriar terá uma camada própria de produto chamada **Kriar Pay**. Essa camada representa a experiência financeira dentro do painel da Kriar, mas não é uma carteira interna nem uma instituição financeira. Por baixo dela existe uma abstração de provedor de pagamento.

O provedor de pagamento será responsável por:

- receber o pagamento;
- processar cartão/Pix/boleto;
- aplicar antifraude, se houver;
- fazer split;
- repassar a parte do lojista;
- repassar a comissão da Kriar;
- lidar com cadastro financeiro do recebedor.

## Kriar Pay e provedores

O frontend e o domínio de produto devem falar em **Kriar Pay** sempre que possível. O backend decide qual provedor atende aquela loja.

Modos previstos:

| Modo | Provider interno | Quando usar | Experiência |
|---|---|---|---|
| Kriar Pay Nativo | `asaas_baas` | Caminho principal da Fase 8 | Lojista opera financeiro dentro da Kriar |
| Conta conectada | `mercado_pago` | Fase 13 | Lojista conecta Mercado Pago via OAuth; algumas ações podem abrir painel externo |
| Provider futuro | `pagarme` ou outro | Futuro/escala | Depende do contrato e das capabilities |

Decisão inicial:

```text
Fase 8: implementar apenas Asaas BaaS como Kriar Pay Nativo.
Fase 13: adicionar Mercado Pago como provider conectado, mantendo a mesma camada Kriar Pay.
```

O objetivo é começar com uma experiência completa e controlada pela Kriar, sem bloquear uma evolução multi-provider. O Asaas BaaS combina melhor com a promessa de painel financeiro nativo; o Mercado Pago entra depois para lojistas que já usam MP ou quando a confiança/conversão da marca MP justificar.

## Abstração multi-provider

O módulo `payments` deve expor uma interface interna de provedor, por exemplo:

```text
PaymentProvider
  create_or_connect_account()
  get_account_status()
  create_payment()
  refund_payment()
  parse_webhook()
  get_capabilities()
```

A aplicação não deve espalhar `if provider == ...` por telas e fluxos. O backend retorna o estado financeiro da loja e uma lista de capabilities que o frontend usa para montar a UX.

Capabilities iniciais:

| Capability | Significado |
|---|---|
| `can_show_balance` | A Kriar consegue exibir saldo/valores disponíveis da conta |
| `can_show_payouts` | A Kriar consegue exibir repasses/saques informados pelo provider |
| `can_manage_pix` | A Kriar consegue configurar/consultar Pix dentro do painel |
| `can_manage_methods` | A Kriar consegue habilitar/desabilitar métodos de pagamento |
| `can_manage_splits` | O provider suporta split automático para comissão da Kriar |
| `can_issue_refunds` | A Kriar consegue solicitar reembolso pela API |
| `can_show_disputes` | A Kriar consegue listar/acompanhar chargebacks/disputas |
| `needs_external_dashboard` | Parte da gestão precisa acontecer no painel externo do provider |
| `requires_oauth_connection` | A conta é conectada por autorização OAuth do lojista |
| `is_native_financial_account` | A conta foi criada/controlada pelo fluxo nativo da Kriar |

Regra de UX:

```text
O painel mostra sempre "Pagamentos / Kriar Pay".
O nome do provedor aparece como detalhe técnico/operacional, não como o produto principal.
```

## Providers candidatos

Providers possíveis:

- Asaas;
- Mercado Pago;
- Pagar.me.

Decisão:

- **Asaas BaaS** será o primeiro provider implementado (Fase 8), como **Kriar Pay Nativo**.
- **Mercado Pago** será implementado depois (Fase 13), como conta conectada via OAuth.
- **Pagar.me** fica como possibilidade futura para escala, negociação ou necessidades específicas de marketplace.

## Modelo de split

Exemplo:

```text
Venda: R$ 100,00
Taxa do provider: R$ 4,00
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
10. Sistema cria transação/cobrança no provider.
11. Provider processa pagamento.
12. Provider aplica split.
13. Provider envia webhook.
14. Backend valida webhook.
15. Backend atualiza transação.
16. Backend atualiza pedido.
17. Cliente e lojista recebem notificação.

## Pedido pendente

Antes de chamar o provider, a Kriar deve criar um pedido com status:

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

Antes de o provider entrar (Fase 8), a V1 **vende sem pagamento online**. O checkout vai até o **pedido pendente** e para — não há chamada de provider, split nem webhook. O pagamento é **combinado fora da plataforma**.

Diferenças em relação ao fluxo com provider:

- o fluxo de checkout termina em **criar pedido `pending_payment`** (passos 1–9); os passos de provider/webhook (10–16) **não rodam**;
- **número do pedido:** todo pedido recebe um identificador **sequencial por loja** (ex.: `#1001`), exibido ao cliente e ao lojista (confirmação, e-mail, painel) — é a referência que ambos usam para combinar entrega/pagamento;
- **baixa de estoque:** ao criar o pedido, o estoque dos itens é **decrementado** em `catalog_inventory_items`; **cancelar** o pedido **devolve** o estoque. Sem reserva intermediária no V1 — valida + decrementa na criação (a unicidade `store_id+product_id+variant_id` evita linha duplicada e corrida de upsert);
- **pagamento combinado fora da plataforma:** a confirmação explica como combinar (Pix/transferência/WhatsApp/entrega combinada). O caminho primário é um **handoff por WhatsApp**: um botão que abre o WhatsApp da loja (`whatsapp_number` de `store_settings`) com mensagem **pré-preenchida** contendo o **número do pedido** e o resumo dos itens, para o cliente combinar o pagamento direto com a loja;
- **marcar pago manualmente:** enquanto não há provider, o lojista marca o pagamento como recebido no painel (`pending_payment → paid`). **Nenhum pedido vira pago sozinho**;
- **políticas da loja:** o checkout exibe/linka as políticas de **troca/devolução/privacidade** da loja (`checkout.policies.*`);
- **ponto de integração do provider:** o módulo de pagamento expõe a **interface** (sem implementar) para a Fase 8 plugar o Kriar Pay Nativo aqui.

### Status do pedido nesta fase

Sem pagamento online, os status que a Fase 6 usa são operacionais:

```text
pending_payment → paid (marcado manualmente) → processing → shipped → delivered
                → canceled (quando permitido; devolve estoque)
```

Os status de provider (`payment_failed`, `refunded`, `chargeback`) entram com o pagamento na **Fase 8**. Todo status precisa ser **lido em código** — a Fase 6 não cria status que ninguém usa.

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
- provider pode demorar;
- Pix/boleto podem ser assíncronos;
- antifraude pode mudar status depois.

## Webhook idempotente

Webhooks podem chegar mais de uma vez.

A tabela `payment_webhooks` deve registrar eventos processados.

Campos sugeridos:

| Campo | Descrição |
|---|---|
| `gateway_event_id` | ID do evento no provider |
| `provider` | `asaas_baas`, `mercado_pago`, etc. |
| `event_type` | Tipo de evento |
| `payload` | Conteúdo bruto ou seguro |
| `processed_at` | Quando foi processado |
| `status` | `received`, `processed`, `failed` |

Regra:

```text
Se `provider + gateway_event_id` já foi processado, não processar novamente.
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

Cada loja precisa ter uma conta/recebedor no provider ativo.

Tabela:

```text
payment_accounts
```

Campos sugeridos:

| Campo | Descrição |
|---|---|
| `store_id` | Loja |
| `provider` | Provider usado (`asaas_baas`, `mercado_pago`, etc.) |
| `mode` | `native` ou `connected` |
| `provider_account_id` | ID da conta/subconta/recebedor no provider |
| `provider_wallet_id` | ID de carteira quando o provider usar esse conceito |
| `status` | `pending`, `active`, `blocked`, `rejected` |
| `kyc_status` | Status do cadastro |
| `capabilities` | JSON/cache das capabilities do provider para aquela conta |
| `external_dashboard_url` | Link opcional para painel externo do provider |
| `metadata` | Dados adicionais |

Credenciais sensíveis, como API key de subconta, access token OAuth ou refresh token, **não devem ficar soltas em `metadata`**. Devem ser armazenadas de forma segura por referência (`provider_credentials_ref`) ou mecanismo equivalente, com criptografia/segredo adequado ao ambiente.

## Configuração do painel

No módulo Pagamentos, o lojista verá:

```text
Status da conta: Ativa / Em análise / Bloqueada
Produto: Kriar Pay Nativo
Provider: Asaas BaaS
Métodos ativos: Pix, Cartão, Boleto
Conta: acc_xxx
```

Quando o provider for externo/conectado:

```text
Produto: Kriar Pay via Mercado Pago
Provider: Mercado Pago
Status: Conectado
Detalhes avançados: Abrir Mercado Pago
```

A tela deve adaptar blocos por capability. Exemplo: se `can_show_balance=false`, não renderizar card de saldo; se `needs_external_dashboard=true`, exibir ação para abrir o painel externo.

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
- chamar provider;
- atualizar transação;
- atualizar pedido;
- notificar cliente/lojista quando necessário.

## Chargeback

Chargeback é risco comercial do lojista.

A Kriar pode:

- registrar o evento;
- exibir alerta;
- permitir resposta, se o provider suportar;
- bloquear loja com chargeback excessivo.

## Segurança de webhook

Todo webhook deve validar:

- assinatura do provider;
- origem esperada;
- idempotência;
- payload mínimo;
- transação pertencente à loja;
- status válido.

## Responsabilidade

| Problema | Responsável principal |
|---|---|
| Cartão recusado | Banco/provider/cliente |
| Pix não pago | Cliente/provider |
| Provider indisponível | Provider |
| Produto não entregue | Lojista |
| Produto com defeito | Lojista |
| Arte personalizada enviada pelo cliente | Cliente/lojista, conforme termos |
| Produção diferente da arte aprovada | Lojista |
| Entrega combinada não realizada | Lojista |
| Checkout da plataforma fora do ar | Kriar |
| Erro técnico no sistema | Kriar |

## Decisão canônica

A V1 usará **Kriar Pay Nativo com Asaas BaaS** como primeiro provider de pagamento com split. A Kriar não reterá valores. O checkout criará pedido pendente, congelará personalizações aprovadas, enviará a cobrança ao provider e só marcará pagamento como confirmado após webhook validado e idempotente. A arquitetura deve continuar multi-provider para permitir Mercado Pago na Fase 13 sem reescrever checkout, pedidos ou painel.
