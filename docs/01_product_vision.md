# Product Vision

## Visão geral

A **Loja Club** será uma plataforma SaaS multi-tenant de ecommerce, permitindo que várias empresas criem e operem suas próprias lojas virtuais dentro de uma infraestrutura única.

A proposta é entregar uma solução semelhante ao conceito de plataformas como Shopify: o lojista não precisa desenvolver um ecommerce próprio, contratar hospedagem separada, configurar checkout do zero ou montar toda a infraestrutura técnica. Ele entra na Loja Club, cria sua loja, cadastra produtos, configura pagamento/frete/layout e começa a vender.

## Posicionamento

A Loja Club não deve ser apresentada apenas como um “criador de sites”. Ela deve ser posicionada como uma **infraestrutura de comércio online**.

A plataforma deve oferecer:

- loja pública;
- painel administrativo do lojista;
- cadastro de produtos;
- imagens e mídia;
- carrinho;
- checkout;
- pagamento com split;
- pedidos;
- clientes;
- frete simples;
- entrega combinada;
- cupons;
- layouts prontos;
- domínio/subdomínio;
- relatórios básicos;
- equipe e permissões;
- admin interno da plataforma.

## Experiência do lojista

O lojista deve conseguir:

1. Criar sua conta.
2. Criar uma ou mais lojas.
3. Escolher um subdomínio inicial, por exemplo `minhaloja.loja.club`.
4. Configurar identidade básica da loja.
5. Escolher entre dois templates prontos na V1.
6. Cadastrar produtos e imagens.
7. Configurar checkout e pagamento.
8. Definir frete simples, retirada local ou entrega combinada.
9. Publicar a loja.
10. Receber pedidos.
11. Ver clientes.
12. Convidar membros da equipe.
13. Controlar permissões por usuário.
14. Ver relatórios básicos.
15. Conectar domínio próprio, se esta funcionalidade for mantida dentro da V1.

## Experiência do cliente final

O cliente final deve acessar a loja pública do lojista sem necessariamente saber que a Loja Club está por trás.

Exemplos:

- `brindesfortaleza.loja.club`
- `presentescriativos.loja.club`
- `www.minhaloja.com.br`

O cliente final deve conseguir:

1. Navegar pela loja.
2. Ver categorias e produtos.
3. Ver detalhes do produto.
4. Adicionar ao carrinho.
5. Finalizar compra.
6. Escolher forma de entrega.
7. Pagar via gateway.
8. Receber confirmação de pedido.
9. Se escolher entrega combinada, manter contato com a loja para combinar o envio.

## Escopo da V1

A V1 deve ser completa o suficiente para operar lojas reais.

A V1 deve incluir:

- autenticação;
- criação de loja;
- multi-tenancy por loja;
- subdomínio automático;
- catálogo;
- upload de imagens;
- dois templates públicos;
- painel do lojista;
- carrinho;
- checkout;
- gateway com split;
- pedidos;
- clientes;
- frete simples;
- entrega combinada para envio local/particular;
- cupons básicos;
- notificações por e-mail;
- planos da Loja Club;
- permissões por módulo;
- admin interno;
- observabilidade mínima;
- segurança básica forte;
- deploy com Docker;
- infraestrutura AWS barata, mas escalável.

## Fora do escopo inicial

A V1 não deve começar com:

- marketplace com vários vendedores no mesmo carrinho;
- app store;
- editor visual avançado;
- temas infinitos;
- ERP;
- automação de marketing avançada;
- emissão automática de nota fiscal;
- integração profunda com transportadoras;
- Kubernetes;
- microserviços;
- banco separado por loja;
- BI avançado;
- wallet interna;
- retenção de saldo pela Loja Club.

## Princípio do produto

A V1 precisa ser simples para construir, mas real o suficiente para vender.

O foco não é copiar todas as funcionalidades de uma plataforma madura. O foco é construir uma base sólida, multi-tenant, segura, modular e capaz de receber lojistas reais.

Um diferencial importante é permitir que lojas locais vendam online sem depender apenas de transportadora tradicional.
Quando fizer sentido para a região, a loja poderá oferecer entrega combinada, usando contato direto com o cliente e serviços locais como 99, Uber, motoboy próprio ou alternativas semelhantes.
