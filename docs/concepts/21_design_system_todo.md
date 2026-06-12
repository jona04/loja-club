# Design System TODO

<!--
Este documento será usado para definir padrões visuais da Kriar.
A V1 usará Tailwind e shadcn/ui no painel, aproveitando o Full Stack FastAPI Template.
O storefront terá 2 templates iniciais.
-->

## Objetivo

Definir padrões visuais para:

- painel do lojista;
- admin da plataforma;
- storefront público;
- templates das lojas;
- editor de personalização 3D;
- e-mails transacionais.

## Painel do lojista

Itens a definir:

- paleta da Kriar;
- logo;
- sidebar;
- topbar;
- cards;
- tabelas;
- formulários;
- botões;
- estados vazios;
- alertas;
- modais;
- feedback de erro/sucesso;
- componentes de upload;
- componentes de visualização de personalização;
- seletor de loja.

## Admin da plataforma

Terá frontend próprio.

Pode reutilizar padrões visuais e componentes do painel, mas deve ter indicação visual clara de ambiente interno/admin.

## Storefront templates

A V1 terá 2 templates:

### Template Classic

<!--
Detalhar depois:
- layout da home;
- grid de produtos;
- página de produto;
- tipografia;
- estilo de botão;
- rodapé;
- header/menu.
-->

### Template Modern

<!--
Detalhar depois:
- layout da home;
- banner principal;
- cards de produto;
- página de produto;
- tipografia;
- estilo de botão;
- rodapé;
- header/menu.
-->

## Editor de personalização 3D

Itens a definir:

- botão `Personalizar`;
- área do canvas 3D;
- controles de upload de arte;
- seletor de cor;
- controles de posição, escala e rotação;
- estado de salvamento automático;
- botão de aprovação visual;
- preview no carrinho;
- preview no pedido;
- aviso de qualidade/baixa resolução, se possível;
- botão flutuante de WhatsApp.

## Customização da V1

Na V1, a customização visual da loja deve permitir:

- escolher template;
- logo;
- banner principal;
- texto principal;
- produtos em destaque.

A personalização 3D é uma customização do produto, não do layout da loja.
Ela deve ter padrões próprios de interface.

Preparar banco para futuro:

- cor primária;
- cor de fundo;
- fonte;
- blocos customizáveis;
- seções da home.

## E-mails

Templates necessários:

- confirmação de conta;
- recuperação de senha;
- novo pedido para lojista;
- nova personalização aprovada para lojista;
- pedido criado para cliente;
- pagamento aprovado;
- pedido enviado;
- convite de equipe;
- aviso de loja suspensa;
- aviso de plano vencido.

## TODO

- [ ] Definir identidade visual da Kriar.
- [ ] Definir componentes padrão do painel.
- [ ] Criar mockups do painel.
- [ ] Criar mockups dos 2 templates públicos.
- [ ] Criar mockup do editor 3D.
- [ ] Definir estados do editor 3D.
- [ ] Definir padrão de e-mails.
- [ ] Definir estados vazios e mensagens.
