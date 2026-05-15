# Merchant Dashboard

## Objetivo

O painel do lojista será o principal ambiente de gestão da loja.

URL:

```text
app.loja.club
```

Ele deve permitir que o lojista configure e opere toda a loja sem precisar de suporte técnico.

## Estrutura geral

Menu recomendado:

```text
Dashboard
Produtos
Pedidos
Personalizações
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

Cada item do menu corresponde a um módulo do sistema e a permissões específicas.

## Dashboard inicial

A primeira tela deve mostrar:

- vendas do dia;
- pedidos recentes;
- pedidos aguardando ação;
- status da loja;
- status do pagamento/gateway;
- produtos ativos;
- personalizações recentes;
- alertas importantes;
- atalhos para cadastrar produto e ver pedidos.

## Seleção de loja ativa

Como um usuário pode ter várias lojas, o painel precisa ter um seletor de loja.

Fluxo:

1. usuário faz login;
2. sistema lista lojas onde ele é membro;
3. se houver uma loja, entra nela;
4. se houver várias, mostra seletor;
5. usuário escolhe loja ativa;
6. todas as telas usam a loja ativa.

Exemplo:

```text
Loja atual: Brindes Fortaleza ▼
```

## Produtos

Funcionalidades:

- listar produtos;
- criar produto;
- editar produto;
- arquivar/desativar produto;
- publicar/despublicar;
- gerenciar imagem;
- gerenciar variações;
- gerenciar estoque;
- definir categoria;
- definir preço;
- definir slug;
- marcar produto como personalizável;
- vincular modelo 3D disponível;
- marcar produto como destaque.

### Produtos personalizáveis

O lojista deve conseguir ativar personalização 3D em produtos compatíveis.

Na V1, os modelos 3D são criados e publicados pela Loja Club.
O lojista escolhe um modelo disponível para o produto, como caneca, squeeze ou camisa.

Funcionalidades:

- habilitar/desabilitar personalização;
- escolher modelo 3D publicado pela Loja Club;
- definir se cor do produto pode ser alterada;
- definir observações de produção;
- ver preview básico do modelo;
- manter imagens tradicionais para listagem e fallback.

## Pedidos

Funcionalidades:

- listar pedidos;
- filtrar por status;
- filtrar por data;
- ver detalhe do pedido;
- ver cliente;
- ver itens comprados;
- ver personalização aprovada, quando houver;
- ver pagamento;
- atualizar status operacional;
- adicionar nota interna;
- cancelar pedido quando permitido;
- solicitar/processar reembolso se permitido;
- ver histórico de status.

## Personalizações

O painel deve ter uma área para acompanhar personalizações de produtos.

Objetivo:

- ver sessões recentes de personalização;
- identificar clientes que enviaram arte;
- abrir preview do produto personalizado;
- verificar arquivo original enviado;
- entender se a arte parece possível de produzir;
- acessar pedido vinculado, quando existir.
- acompanhar a sessão quase em tempo real a partir do autosave do cliente.

Na V1, não haverá chat interno completo.
A loja pode usar o botão de WhatsApp configurado no storefront para conversar com o cliente quando ele pedir ajuda ou quando houver um pedido claro.

O lojista não deve alterar a arte aprovada pelo cliente sem gerar uma nova aprovação.
O pedido precisa preservar o que o cliente confirmou no storefront.

## Clientes

Funcionalidades:

- listar clientes;
- ver histórico de pedidos;
- ver dados de contato;
- ver endereços;
- buscar cliente;
- exportar se permitido pelo plano/permissão.

## Checkout

Funcionalidades:

- configurar dados básicos do checkout;
- configurar política de troca/devolução;
- configurar mensagem pós-compra;
- definir campos obrigatórios;
- visualizar status dos métodos de pagamento;
- orientar conexão com gateway.

## Pagamentos

Funcionalidades:

- conectar conta do lojista ao gateway;
- exibir status da conta;
- exibir métodos ativos;
- ver transações;
- ver problemas de pagamento;
- ver chargebacks/disputas;
- ver informações de repasse fornecidas pelo gateway.

A Loja Club não reterá dinheiro. O painel apenas exibirá informações retornadas pelo gateway.

## Frete

Na V1, o frete será simples.

Funcionalidades:

- frete fixo;
- frete grátis acima de valor mínimo;
- retirada local;
- entrega combinada;
- regiões de entrega;
- prazo estimado manual.

### Entrega combinada

A entrega combinada permite que a loja venda para clientes próximos e combine o envio depois da compra.

Uso esperado:

- cliente está na mesma cidade, região metropolitana ou estado da loja física;
- loja pode entregar por motoboy próprio;
- loja pode combinar envio por aplicativo, como 99, Uber ou similar da região;
- cliente e loja conversam após a venda para fechar prazo, valor e forma de envio.

Na V1, essa opção não precisa integrar diretamente com aplicativos.
Ela deve deixar claro no checkout e no pedido que a entrega será combinada com a loja após a compra.

## Layout da loja

Funcionalidades da V1:

- escolher entre 2 templates prontos;
- visualizar preview;
- aplicar template;
- atualizar logo;
- atualizar banner principal;
- atualizar texto principal;
- escolher produtos em destaque.

Quando salvar, a loja pública deve refletir a alteração.

## Cupons

Funcionalidades:

- criar cupom percentual;
- criar cupom de valor fixo;
- definir validade;
- definir limite de uso;
- definir pedido mínimo;
- ativar/desativar cupom.

## Relatórios

V1 deve ter relatórios simples:

- total vendido;
- pedidos por status;
- produtos mais vendidos;
- ticket médio;
- clientes recentes;
- vendas por período.

Relatórios pesados devem ser calculados de forma assíncrona ou otimizada.

## Domínios

Funcionalidades:

- ver subdomínio atual;
- alterar subdomínio se permitido;
- conectar domínio próprio, se estiver na V1;
- ver status de verificação;
- instruções de DNS.

Uma loja pode ter vários domínios ativos.
Não haverá domínio principal na V1.

## Equipe

Funcionalidades:

- convidar usuário;
- listar membros;
- alterar papel;
- remover membro;
- definir permissões por papel;
- bloquear acesso.

## Configurações

Funcionalidades:

- nome da loja;
- descrição;
- logo;
- e-mail de contato;
- telefone;
- endereço;
- redes sociais;
- políticas básicas;
- status da loja publicada/não publicada.

## Plano

Funcionalidades:

- plano atual;
- comissão do plano;
- mensalidade;
- status da assinatura;
- faturas;
- trocar plano;
- alerta de inadimplência.

## Permissões no painel

O painel deve esconder módulos conforme permissão.

Exemplo:

- usuário sem `payments.view` não vê Pagamentos;
- usuário sem `layout.update` pode ver o layout, mas não salvar;
- usuário sem `team.view` não vê Equipe.

## Estado da loja

A loja pode ter estados:

| Status | Significado |
|---|---|
| `draft` | Loja ainda não publicada |
| `active` | Loja ativa |
| `paused` | Loja pausada pelo lojista |
| `suspended` | Loja suspensa pela plataforma |
| `blocked` | Loja bloqueada por regra crítica |
| `archived` | Loja arquivada por soft delete |

## Onboarding do lojista

A V1 deve ter checklist inicial:

```text
1. Criar loja
2. Escolher layout
3. Cadastrar primeiro produto
4. Vincular modelo 3D, se o produto for personalizável
5. Configurar pagamento
6. Configurar entrega
7. Publicar loja
```

Isso ajuda o lojista a chegar mais rápido na primeira venda.
