# Customer Identity and Guest Checkout

## Objetivo

A Loja Club deve permitir que o cliente final compre sem criar conta.

Isso é importante para conversão. O cliente de uma loja pequena, gráfica ou empresa de brindes não deve ser obrigado a passar por cadastro antes de comprar ou personalizar um produto.

Ao mesmo tempo, o sistema precisa permitir que esse cliente recupere carrinho, continue uma personalização e acompanhe pedidos.

## Três tipos de pessoas no sistema

Existem três grupos diferentes e eles não devem ser misturados.

| Tipo | Onde atua | Exemplo | Tabela principal |
|---|---|---|---|
| Admin Loja Club | Admin interno da plataforma | equipe Loja Club | `account_users` + `platform_admin_roles` |
| Lojista/equipe | Painel da loja | owner, admin, support, catalog | `account_users` + `store_members` |
| Cliente final | Storefront da loja | comprador da loja | `customer_profiles` |

## User da plataforma

`account_users` representa quem acessa sistemas autenticados da Loja Club:

- admin interno;
- dono da loja;
- equipe da loja;
- suporte;
- catálogo;
- marketing.

Esse usuário pode ter acesso a uma ou mais lojas por meio de `store_members`.

## Customer da loja

`customer_profiles` representa o comprador final de uma loja.

Características:

- pertence a uma loja via `store_id`;
- pode existir sem senha;
- pode ser criado durante o checkout;
- pode comprar como convidado;
- pode virar cliente identificado depois;
- não acessa `frontend-dashboard` nem `frontend-admin`.

O mesmo e-mail comprando em duas lojas diferentes deve gerar dois customers diferentes, um por loja.

Exemplo:

```text
store_id: 10, email: ana@email.com -> customer da Loja A
store_id: 20, email: ana@email.com -> customer da Loja B
```

## Compra sem login

Fluxo padrão da V1:

1. Cliente acessa a loja pública.
2. Sistema cria ou reutiliza uma sessão anônima.
3. Cliente navega, personaliza produto e adiciona ao carrinho.
4. Carrinho fica associado à sessão anônima.
5. No checkout, cliente informa nome, e-mail, telefone e endereço.
6. Sistema cria ou atualiza `customer_profiles`.
7. Pedido fica associado ao customer.
8. Cliente recebe confirmação por e-mail e/ou WhatsApp.

O cliente não precisa criar senha.

## Sessão anônima

Antes do checkout, o cliente pode não ter informado e-mail, telefone ou nome.

Mesmo assim, o sistema deve conseguir manter estado usando uma sessão anônima.

Meios recomendados:

- cookie HTTP-only com `guest_session_id`;
- registro em `customer_guest_sessions`;
- carrinho em `cart_carts`;
- personalização em `customization_sessions`.

O cookie identifica o navegador/dispositivo.
Ele não substitui autenticação e não deve dar acesso a dados sensíveis.

## Recuperar carrinho sem login

Existem três níveis de recuperação.

### Mesmo navegador

Se o cliente voltar pelo mesmo navegador antes da expiração:

- cookie identifica `guest_session_id`;
- storefront carrega carrinho ativo;
- personalizações em andamento são restauradas.

Esse é o fluxo mais simples e deve funcionar sem pedir login.

### Link de recuperação

Depois que o cliente informar e-mail ou telefone, o sistema pode gerar um link seguro para continuar.

Exemplo:

```text
https://loja.com.br/continue?token=...
```

Esse token deve:

- ser aleatório;
- expirar;
- pertencer a uma loja;
- dar acesso apenas ao carrinho/sessão relacionados;
- não expor dados sensíveis no próprio token.

### Pós-checkout

Depois do pedido, o cliente acompanha por link seguro enviado por e-mail/WhatsApp.

Na V1, não é necessário criar área logada do cliente.

## Recuperar personalização sem login

Quando o cliente inicia uma personalização 3D, o sistema cria uma sessão.

Essa sessão deve guardar:

- modelo 3D;
- produto;
- variação;
- cor escolhida;
- imagens enviadas;
- posição da imagem;
- escala;
- rotação;
- área usada;
- preview;
- status;
- expiração.

Se o cliente voltar com o mesmo cookie, a personalização deve continuar exatamente onde parou.

Se o cliente já informou e-mail/telefone, a sessão pode ser recuperada também por link seguro.

## Validade das sessões

Sessões anônimas não devem durar para sempre.

Regras da V1:

- carrinho anônimo expira em 30 dias;
- sessão de personalização expira em 30 dias;
- checkout session expira em prazo menor, por exemplo 24 horas;
- pedido criado não expira como sessão;
- personalização congelada no pedido deve ser preservada para auditoria.

Quando uma sessão expirar, ela deve ser marcada como `expired`.
Como regra geral do projeto, isso é soft delete ou mudança de status, não remoção direta do registro.

Arquivos temporários não aprovados podem entrar em política de limpeza depois da expiração, mas o registro de auditoria deve permanecer.

## Cliente identificado opcional

No futuro, o cliente poderá ter uma conta leve.

Para V1, a sugestão é:

- sem senha obrigatória;
- compra como convidado;
- link mágico por e-mail/WhatsApp para continuar carrinho ou ver pedido;
- conta opcional depois da compra.

Isso evita atrito no checkout e mantém espaço para evoluir.

## Diferença entre visitante, customer e user

| Conceito | Login? | Persistido? | Uso |
|---|---|---|---|
| Visitante anônimo | Não | sessão/cookie | carrinho e personalização antes do checkout |
| Customer | Não necessariamente | sim, por loja | comprador final, pedidos, histórico |
| User | Sim | sim, global | lojista, equipe e admin Loja Club |

## Decisão canônica

Cliente final pode comprar e personalizar sem login.
Antes do checkout, o estado é mantido por sessão anônima com validade.
No checkout, o cliente vira `customer_profile` daquela loja.
Usuários da plataforma e clientes finais são modelos diferentes.
