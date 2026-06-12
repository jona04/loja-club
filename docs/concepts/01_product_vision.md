# Product Vision

## Visão geral

A **Kriar** será uma plataforma SaaS multi-tenant de ecommerce, permitindo que várias empresas criem e operem suas próprias lojas virtuais dentro de uma infraestrutura única.

A proposta é entregar uma solução com a base operacional de uma plataforma como Shopify, mas com um diferencial inicial claro: atender primeiro empresas de brindes, gráficas, comunicação visual e produtos personalizados.

O lojista não precisa desenvolver um ecommerce próprio, contratar hospedagem separada, configurar checkout do zero ou montar toda a infraestrutura técnica. Ele entra na Kriar, cria sua loja, cadastra produtos, configura pagamento/frete/layout e começa a vender.

Além do ecommerce comum, a Kriar permitirá produtos personalizáveis em 3D **(Fase 7 — ver [Produtos 3D](../backlog/phase-7-3d-products.md); a Fase 2 de catálogo entrega só imagem)**. O cliente escolhe um produto, abre uma experiência de personalização, envia uma imagem, ajusta a arte no modelo 3D, aprova o resultado visual e adiciona ao carrinho. **Os modelos 3D vêm do catálogo da plataforma** (Fase 7, via seed) ou são **gerados pelo lojista** via API de terceiros (Fase 12).

## Posicionamento

A Kriar não deve ser apresentada apenas como um “criador de sites”. Ela deve ser posicionada como uma **infraestrutura de comércio online**.

A plataforma deve oferecer:

- loja pública;
- painel administrativo do lojista;
- cadastro de produtos;
- imagens e mídia;
- modelos 3D do **catálogo da plataforma** (Fase 7) + **gerados pelo lojista** via API (Fase 12);
- produtos personalizáveis;
- sessão de personalização salva;
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
3. Escolher um subdomínio inicial, por exemplo `minhaloja.kriar.shop`.
4. Configurar identidade básica da loja.
5. Escolher entre dois templates prontos na V1.
6. Cadastrar produtos e imagens.
7. Marcar produtos como personalizáveis quando fizer sentido.
8. Gerar modelos 3D via API e vinculá-los aos produtos (Fase 7).
9. Configurar checkout e pagamento.
10. Definir frete simples, retirada local ou entrega combinada.
11. Publicar a loja.
12. Receber pedidos.
13. Ver personalizações aprovadas pelo cliente.
14. Ver clientes.
15. Convidar membros da equipe.
16. Controlar permissões por usuário.
17. Ver relatórios básicos.
18. Conectar domínio próprio, se esta funcionalidade for mantida dentro da V1.

## Experiência do cliente final

O cliente final deve acessar a loja pública do lojista sem necessariamente saber que a Kriar está por trás.

Exemplos:

- `brindesfortaleza.kriar.shop`
- `presentescriativos.kriar.shop`
- `www.minhaloja.com.br`

O cliente final deve conseguir:

1. Navegar pela loja.
2. Ver categorias e produtos.
3. Ver detalhes do produto.
4. Personalizar produtos 3D quando disponível.
5. Salvar e continuar uma personalização depois.
6. Aprovar visualmente a arte antes de adicionar ao carrinho.
7. Adicionar ao carrinho.
8. Finalizar compra.
9. Escolher forma de entrega.
10. Pagar via gateway.
11. Receber confirmação de pedido.
12. Se escolher entrega combinada, manter contato com a loja para combinar o envio.
13. Usar WhatsApp da loja para tirar dúvidas quando disponível.

O cliente final não precisa criar conta nem fazer login para comprar.
Antes do checkout, carrinho e personalização serão mantidos por sessão anônima.
No checkout, ao informar nome, e-mail e telefone, o sistema cria ou atualiza o customer daquela loja.

## Escopo da V1

A V1 deve ser completa o suficiente para operar lojas reais.

A V1 deve incluir:

- autenticação;
- criação de loja;
- multi-tenancy por loja;
- subdomínio automático;
- catálogo;
- upload de imagens;
- modelos 3D do catálogo da plataforma (Fase 7) e gerados pelo lojista, por loja (Fase 12);
- produtos personalizáveis em 3D;
- upload de arte pelo cliente final;
- sessão de personalização persistida;
- preview aprovado anexado ao pedido;
- dois templates públicos;
- painel do lojista;
- carrinho;
- checkout;
- gateway com split;
- pedidos;
- clientes;
- compra sem login obrigatório;
- carrinho anônimo recuperável por sessão;
- frete simples;
- entrega combinada para envio local/particular;
- cupons básicos;
- notificações por e-mail;
- planos da Kriar;
- permissões por módulo;
- admin interno;
- observabilidade mínima;
- segurança básica forte;
- soft delete para registros de negócio;
- deploy com Docker;
- infraestrutura AWS barata, mas escalável.

## Fora do escopo inicial

A V1 não deve começar com:

- marketplace com vários vendedores no mesmo carrinho;
- app store;
- editor visual avançado de layout da loja;
- chat interno completo;
- upload de modelo 3D pelo lojista;
- marketplace de modelos 3D de terceiros;
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
- retenção de saldo pela Kriar.

## Princípio do produto

A V1 precisa ser simples para construir, mas real o suficiente para vender.

O foco não é copiar todas as funcionalidades de uma plataforma madura. O foco é construir uma base sólida, multi-tenant, segura, modular e capaz de receber lojistas reais.

Um diferencial importante é permitir que lojas locais vendam online sem depender apenas de transportadora tradicional.
Quando fizer sentido para a região, a loja poderá oferecer entrega combinada, usando contato direto com o cliente e serviços locais como 99, Uber, motoboy próprio ou alternativas semelhantes.

Outro diferencial central é a personalização 3D.
A Kriar começa nichada para um público que sente essa dor todos os dias: brindes, gráficas e comunicação visual.
Ao mesmo tempo, a plataforma continua atendendo lojistas de ecommerce comum que só precisam cadastrar fotos, variações, preço e estoque.
