# Business Model and Rules

## Modelo de negócio

A Kriar será um SaaS de ecommerce com possibilidade de comissão por venda.

O foco comercial inicial será em lojas de brindes, gráficas e comunicação visual, porque a personalização 3D é um diferencial forte para esse público.

O modelo recomendado para a V1 é:

- mensalidade fixa por loja;
- comissão percentual por venda via split de pagamento;
- gateway responsável por receber, descontar taxa e repassar valores.

A Kriar não deve reter valores dos lojistas.

## Planos iniciais sugeridos

| Plano | Mensalidade | Comissão por venda | Observação |
|---|---:|---:|---|
| Starter | R$ 49,90/mês | 3% | Entrada para lojistas pequenos |
| Pro | R$ 99,90/mês | 1,5% | Plano principal |
| Business | R$ 199,90/mês | 0,5% | Para lojistas com maior volume |

Também pode existir um plano inicial sem mensalidade:

| Plano | Mensalidade | Comissão por venda | Observação |
|---|---:|---:|---|
| Free | R$ 0/mês | 5% | Bom para aquisição inicial |

## Taxa do gateway

A taxa do gateway é separada da comissão da Kriar.

Exemplo:

Venda de R$ 100,00.

- Gateway cobra R$ 4,00.
- Kriar cobra R$ 3,00.
- Lojista recebe R$ 93,00.

O valor exato dependerá do gateway, método de pagamento, parcelamento e prazo de recebimento.

## Regras de responsabilidade

A Kriar fornece tecnologia. O lojista vende o produto.

| Área | Responsável |
|---|---|
| Produto | Lojista |
| Estoque | Lojista |
| Preço | Lojista |
| Qualidade da arte enviada pelo cliente | Cliente/lojista, conforme termos |
| Produção do item personalizado | Lojista |
| Entrega | Lojista |
| Entrega combinada | Lojista |
| Troca/devolução | Lojista |
| Nota fiscal | Lojista |
| Atendimento ao consumidor | Lojista |
| Processamento do pagamento | Gateway |
| Split de pagamento | Gateway |
| Infraestrutura da loja | Kriar |
| Modelos 3D publicados pela plataforma | Kriar |
| Painel administrativo | Kriar |
| Segurança da plataforma | Kriar |
| Disponibilidade técnica | Kriar |

## Regra sobre retenção de dinheiro

A Kriar não deve:

- receber 100% do valor da venda na conta própria;
- guardar saldo do lojista;
- operar carteira interna;
- liberar saque manual;
- antecipar recebíveis com recurso próprio;
- agir como banco ou instituição financeira;
- ser a vendedora oficial dos produtos.

O gateway deve:

- processar o pagamento;
- fazer KYC/cadastro do recebedor;
- aplicar split;
- repassar ao lojista;
- repassar comissão para a Kriar;
- lidar com regras do arranjo de pagamento.

## Regra sobre vendedor oficial

O vendedor oficial é sempre o lojista.

A Kriar deve aparecer nos termos como:

- plataforma tecnológica;
- fornecedora de software;
- infraestrutura de ecommerce;
- intermediadora técnica do fluxo de checkout;
- não vendedora dos produtos.

## Regras de bloqueio da loja

A Kriar deve poder suspender loja em casos como:

- fraude;
- produto proibido;
- denúncia grave;
- chargeback excessivo;
- inadimplência da mensalidade;
- violação dos termos;
- uso indevido da plataforma;
- tentativa de burlar comissão;
- dados falsos no cadastro.

## Planos e permissões comerciais

Além das permissões de usuário, a loja terá permissões por plano.

Exemplo:

| Recurso | Starter | Pro | Business |
|---|---|---|---|
| Produtos | até limite inicial | maior limite | limite alto/ilimitado |
| Usuários da equipe | 1 ou 2 | até 5 | mais usuários |
| Templates | 1 ou 2 | 2 | 2 |
| Personalização 3D | limitada | incluída | maior limite |
| Modelos 3D disponíveis | básicos | principais | mais modelos |
| Relatórios | básico | básico+ | mais completo |
| Comissão | maior | média | menor |

## Regra entre plano e permissão

Para um usuário acessar uma funcionalidade, duas condições precisam ser verdadeiras:

1. O plano da loja permite o recurso.
2. O usuário tem permissão para usar o recurso dentro daquela loja.

Exemplo:

- Plano permite módulo de layout.
- Usuário não tem `layout.update`.
- Resultado: usuário não pode alterar layout.

## Regras de cobrança

A V1 deve suportar:

- plano ativo;
- plano suspenso;
- plano cancelado;
- loja bloqueada por inadimplência;
- comissão por venda definida pelo plano;
- registro de cobrança mensal;
- registro de comissão recebida via split.

## Pontos jurídicos a detalhar depois

Ver também: [Legal and Compliance TODO](./19_legal_and_compliance_todo.md)

Ainda precisam ser detalhados:

- termos de uso da plataforma;
- termos para lojista;
- política de privacidade;
- política de produtos proibidos;
- política de chargeback;
- política de arte enviada pelo cliente;
- responsabilidade por produção personalizada;
- política de suspensão de loja;
- responsabilidade em caso de falha do gateway;
- responsabilidade em caso de falha de entrega;
- LGPD;
- tratamento de dados pessoais de clientes finais.
