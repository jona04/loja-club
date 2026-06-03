# Open Decisions

Este documento lista decisões que ainda precisam ser fechadas.

## Lib de fila/worker

```text
Decisão fechada: usar arq (async, baseado em Redis).
```

Motivos: async (casa com o backend), Redis já presente, leve e com cron embutido. Ver também `docs/backlog/_foundations-and-bottlenecks.md` (DEC-3).

## Gateway principal

Opções:

- Pagar.me;
- Mercado Pago;
- Asaas.

Critérios:

- qualidade do split;
- facilidade de integração;
- taxas;
- confiança do consumidor;
- suporte a Pix/cartão/boleto;
- onboarding de recebedores;
- webhooks;
- documentação;
- ambiente sandbox.

Decisão pendente:

```text
Escolher gateway principal da V1.
```

## Storefront Next.js

```text
Decisão fechada: usar Next.js no frontend-storefront desde a V1.
```

Motivos:

- SEO;
- cache/CDN;
- renderização server-side;
- metadata dinâmica;
- evitar refatoração futura de loja pública.

## Infra inicial

Opções:

1. EC2 + Docker Compose + Traefik + RDS.
2. ECS/Fargate + ALB + RDS.

Recomendação (decidido):

- **toda a V1 é dev**: Fases 0–4 local; Fases 5–6 online na AWS com **EC2 + Docker Compose + Traefik + RDS**;
- **produção robusta (pós-V1)**: ECS/Fargate + ALB + RDS.

Decisão:

```text
V1 = dev em EC2 (Fases 5–6). ECS/Fargate fica para a produção pós-V1.
```

## Domínio próprio na V1

Subdomínio `*.loja.club` será obrigatório na V1.

Domínio próprio pode ser:

- incluído na V1;
- lançado manualmente/controlado;
- deixado para depois.

Decisão pendente:

```text
Confirmar se domínio próprio entra automatizado na V1.
```

## Cobrança de mensalidade

A comissão via split é clara.

A mensalidade pode ser:

- cobrada desde a V1;
- cobrada depois;
- simulada/manual no começo;
- integrada ao gateway.

Decisão pendente:

```text
Definir como a mensalidade será cobrada na V1.
```

## Planos iniciais

Sugestão atual:

```text
Starter: R$ 49,90 + 3%
Pro: R$ 99,90 + 1,5%
Business: R$ 199,90 + 0,5%
```

Decisão pendente:

```text
Validar valores comerciais finais.
```

## Dois templates iniciais

Nomes sugeridos:

```text
classic
modern
```

Decisão pendente:

```text
Definir visual exato dos 2 templates.
```

## Personalização 3D na V1

Decisão assumida:

```text
A V1 deve incluir personalização 3D de produtos com Three.js.
```

Escopo definido:

- modelos 3D criados pela Loja Club;
- lojista vincula modelo ao produto;
- cliente envia arte e personaliza no storefront;
- sessão fica salva;
- arte aprovada fica congelada no pedido;
- WhatsApp será o canal de conversa da V1.

Decisões pendentes:

```text
Definir lista exata dos primeiros modelos 3D e formatos finais dos assets.
```

## Frete na V1

Sugestão:

- frete fixo;
- frete grátis por valor mínimo;
- retirada local;
- entrega combinada.

Decisão pendente:

```text
Confirmar se haverá integração com Correios/transportadora na V1 ou não.
```

Decisão já assumida:

```text
A V1 deve permitir entrega combinada sem integração automática com apps.
```

## Nota fiscal

Sugestão:

```text
Fora da V1. Responsabilidade do lojista.
```

Decisão pendente:

```text
Confirmar se a V1 apenas informa que nota fiscal é responsabilidade do lojista.
```

## Editor visual

Sugestão:

```text
Editor visual de layout da loja fica fora da V1.
Personalização 3D de produto entra na V1.
```

Decisão pendente:

```text
Confirmar limite exato de customização visual na V1.
```
