# Customer Identity and Guest Checkout

## Objetivo

A Loja Club deve permitir que o cliente final compre sem criar conta.

Isso é importante para conversão. O cliente de uma loja pequena, gráfica ou empresa de brindes não deve ser obrigado a passar por cadastro antes de comprar ou personalizar um produto.

Ao mesmo tempo, o sistema precisa:

- saber **quem é quem** mesmo sem cadastro, identificando o cliente por **e-mail e telefone**;
- permitir que esse cliente recupere carrinho, continue uma personalização e acompanhe pedidos;
- permitir, de forma opcional, que ele entre numa área do cliente para ver histórico e editar o perfil.

A meta é uma experiência agradável e fácil de navegar: comprar é livre; identificar e logar é simples e sem atrito.

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
- é identificado por **e-mail e telefone normalizados** (ver abaixo);
- pode existir sem senha;
- pode ser criado durante o checkout;
- pode comprar como convidado;
- pode virar cliente identificado/logado depois;
- não acessa `frontend-dashboard` nem `frontend-admin`.

O mesmo e-mail comprando em duas lojas diferentes deve gerar dois customers diferentes, um por loja.

```text
store_id: 10, email: ana@email.com -> customer da Loja A
store_id: 20, email: ana@email.com -> customer da Loja B
```

## Chave de identidade do customer

Dentro de uma loja, o customer é identificado por dois campos **únicos**:

- **e-mail normalizado**;
- **telefone normalizado em formato E.164** (`phone_e164`).

Regras:

- `(store_id, email)` é único;
- `(store_id, phone_e164)` é único;
- a **prioridade de match é o e-mail** e, na ausência/divergência, o telefone;
- e-mail e telefone são, portanto, a forma de o lojista saber quem é quem mesmo sem cadastro.

## Normalização de e-mail e telefone

A deduplicação só funciona se os valores forem normalizados de forma consistente. Guardar o valor normalizado (chave de dedup) e, se quiser, também o valor original digitado para exibição.

### E-mail

1. remover espaços nas pontas (`trim`);
2. converter tudo para minúsculas;
3. **não** remover pontos nem sufixos `+tag` (isso uniria e-mails distintos por engano e causaria problemas);
4. usar o resultado como chave de deduplicação.

### Telefone

O país **não é digitado**: vem do **seletor de país** do checkout (ISO 3166-1), que define a região. O cliente digita só o número local.

A normalização usa uma **biblioteca de telefones** (libphonenumber, ex.: `phonenumbers`) — **não normalizar à mão**, para cobrir as regras de cada país (tronco, quantidade de dígitos, validação):

1. obter a **região** a partir do seletor de país (ex.: `BR`, `US`, `PT`);
2. passar o número digitado + a região para a lib;
3. a lib **valida** e devolve o número em **E.164** (`+<código do país><número nacional>`), tratando tronco e formatos locais;
4. guardar o E.164 em `phone_e164` (chave de dedup);
5. número inválido para a região → mensagem amigável, sem travar a experiência.

Exemplos (apenas ilustrativos — a regra vale para qualquer país):

```text
BR  (86) 99999-0000   → +5586999990000
US  (415) 555-0132    → +14155550132
PT  912 345 678       → +351912345678
```

Nenhuma regra de país é fixada no código; a lib cuida disso. O resultado é sempre E.164.

## Identificação no checkout (criar ou atualizar)

Ao finalizar o checkout, com nome, e-mail, telefone e endereço informados:

1. normaliza o e-mail e o telefone;
2. procura customer por **e-mail normalizado** naquela loja → se achar, é esse;
3. senão, procura por **`phone_e164`** naquela loja → se achar, é esse;
4. senão, **cria** um novo customer;
5. vincula o pedido ao customer.

Regras de atualização:

- **Nome:** vale o **primeiro nome** já cadastrado para aquele e-mail/telefone. O sistema **não sobrescreve** o nome em compras seguintes. Para alterar o nome, o cliente precisa **fazer login** e editar o perfil.
- **Campos faltando:** se o customer ainda não tem telefone (ou e-mail) e o checkout trouxe um que **não pertence a outro customer**, o sistema preenche.
- **Endereço:** todo endereço novo informado é cadastrado como **mais um** `customer_addresses` daquele customer (vários endereços por customer). Endereços idênticos não são duplicados.
- **Conflito raro:** se o e-mail bate com um customer e o telefone com outro (diferente), **vence o e-mail** (prioridade). O sistema não "rouba" um e-mail/telefone que já pertence a outro customer, para preservar a unicidade. Esses casos podem ser sinalizados para o lojista revisar.

## Recuperação e login por código

O cliente pode recuperar carrinho/pedido e entrar na área do cliente **sem senha**, usando um código de uso único:

1. informa **e-mail ou telefone**;
2. recebe um **código** por **e-mail, SMS ou WhatsApp**;
3. digita o código → acessa o carrinho/pedido/sessão e, se quiser, fica logado.

O código deve ser:

- aleatório e curto;
- com expiração rápida (ex.: 10 minutos);
- de uso único;
- escopado à loja + customer;
- protegido contra força bruta (tentativas limitadas e rate limit).

## Login da área do cliente

A loja pode permitir que o cliente entre na sua área. Há três formas, e **todas levam ao mesmo customer** (resolvido por e-mail/telefone normalizado):

1. **Código** (sem senha) por e-mail/SMS/WhatsApp;
2. **Cadastro tradicional** com e-mail + senha (o cliente pode definir uma senha);
3. **Login com Google** (OAuth).

Na área do cliente ele pode:

- ver histórico de pedidos;
- acompanhar personalizações;
- gerenciar endereços;
- **editar o perfil, inclusive o nome**.

Editar dados do perfil exige estar autenticado (código, senha ou Google).

## Sincronização guest ↔ conta

Guest e conta são **o mesmo customer** quando o e-mail/telefone batem. Os meios de login são apenas credenciais ligadas a um único `customer_profiles`.

Casos que devem sincronizar:

- comprou como convidado primeiro e depois entrou com Google/senha usando o mesmo e-mail → cai no mesmo customer e enxerga o histórico;
- criou conta primeiro e depois comprou como convidado com o mesmo e-mail/telefone → o pedido cai na conta existente;
- **nunca** criar customer duplicado quando e-mail/telefone já existem na loja.

As identidades de login (senha, `sub` do Google) ficam guardadas como vínculos do customer (`customer_auth_identities`), todos apontando para o mesmo registro.

## Sessão anônima

Antes do checkout, o cliente pode não ter informado e-mail, telefone ou nome.

Mesmo assim, o sistema mantém estado usando uma sessão anônima:

- cookie HTTP-only com `guest_session_id`;
- registro em `customer_guest_sessions`;
- carrinho em `cart_carts`;
- personalização em `customization_sessions`.

O cookie identifica o navegador/dispositivo. Ele não substitui autenticação e não dá acesso a dados sensíveis.

## Recuperar carrinho sem login

Existem três níveis de recuperação.

### Mesmo navegador

Se o cliente voltar pelo mesmo navegador antes da expiração:

- o cookie identifica o `guest_session_id`;
- o storefront carrega o carrinho ativo;
- as personalizações em andamento são restauradas.

Esse é o fluxo mais simples e funciona sem pedir login.

### Por código (e-mail ou telefone)

Depois que o cliente informar e-mail ou telefone, ele pode recuperar o carrinho em qualquer dispositivo pelo **código de uso único** enviado por e-mail, SMS ou WhatsApp (ver "Recuperação e login por código"). É o mesmo mecanismo usado para login.

### Pós-checkout

Depois do pedido, o cliente acompanha por link/código seguro enviado por e-mail/WhatsApp.

## Recuperar personalização sem login

Quando o cliente inicia uma personalização 3D, o sistema cria uma sessão que guarda:

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

Se o cliente voltar com o mesmo cookie, a personalização continua exatamente onde parou. Se já informou e-mail/telefone, a sessão pode ser recuperada por código seguro.

## Validade das sessões

- carrinho anônimo expira em 30 dias;
- sessão de personalização expira em 30 dias;
- checkout session expira em prazo menor, por exemplo 24 horas;
- código de verificação expira em minutos (ex.: 10);
- pedido criado não expira como sessão;
- personalização congelada no pedido deve ser preservada para auditoria.

Quando uma sessão expirar, ela deve ser marcada como `expired` (soft delete/status, não remoção direta). Arquivos temporários não aprovados podem entrar em política de limpeza depois da expiração, mas o registro de auditoria permanece.

## Diferença entre visitante, customer e user

| Conceito | Login? | Persistido? | Uso |
|---|---|---|---|
| Visitante anônimo | Não | sessão/cookie | carrinho e personalização antes do checkout |
| Customer | Opcional (código, senha ou Google) | sim, por loja | comprador final, pedidos, histórico, perfil |
| User | Sim | sim, global | lojista, equipe e admin Loja Club |

## O que é necessário para o MVP (dev local)

Respeitando a prioridade de ter o MVP rodando local o quanto antes (ver `17_v1_roadmap.md`):

Necessário no MVP (dev local):

- guest checkout com identificação por **e-mail e telefone normalizados** + deduplicação;
- regra de **primeiro-nome-vence**;
- vários endereços por customer;
- recuperação de carrinho no mesmo navegador.

Pode vir logo depois (como o pagamento, fica após o MVP — Fase 6):

- recuperação/login por **código** (e-mail/SMS/WhatsApp);
- **área do cliente** (histórico, editar perfil, endereços);
- login com **senha** e com **Google**;
- sincronização completa **guest ↔ conta**.

## Decisão canônica

- O cliente final compra e personaliza **sem login**.
- O customer é **único por loja** por **e-mail e telefone normalizados** (E.164), com o match priorizando o e-mail.
- O **primeiro nome** cadastrado para aquele e-mail/telefone prevalece; alterá-lo exige login.
- Um customer pode ter **vários endereços**; endereço novo no checkout vira mais um endereço.
- A **conta do cliente é opcional**, com login por **código, senha ou Google**, todos sincronizando no mesmo customer.
- Usuários da plataforma (`account_users`) e clientes finais (`customer_profiles`) são modelos diferentes.
