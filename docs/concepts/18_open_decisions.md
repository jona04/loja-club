# Open Decisions

Este documento lista decisões que ainda precisam ser fechadas.

## Lib de fila/worker

```text
Decisão fechada: usar arq (async, baseado em Redis).
```

Motivos: async (casa com o backend), Redis já presente, leve e com cron embutido. Ver também `docs/backlog/_foundations-and-bottlenecks.md` (DEC-3).

## API de geração de modelos 3D (Fase 12)

O 3D da **Fase 7** usa o **catálogo da plataforma** (modelos via seed) — não precisa de API de geração. A **geração pelo lojista** (image/text → GLB) é a **Fase 12** e é o que depende desta decisão.

Candidatos a avaliar:

- [Meshy](https://www.meshy.ai/api)
- [Tripo3D](https://www.tripo3d.ai/api)
- [Hyper3D](https://hyper3d.ai/api-dashboard)

Critérios: qualidade do GLB (web-ready), custo por geração, latência, formatos/texturas, limites de uso, licença do output, suporte a image→3D. **Pendente** — fechar ao iniciar a **Fase 12**. Ver [Fase 12](../backlog/phase-12-merchant-3d-generation.md).

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

- **dev**: Fases 0–8 local; **Fase 9** dev online na AWS com **EC2 + Docker Compose + Traefik + RDS**;
- **produção robusta (Fase 11)**: ECS/Fargate + ALB + RDS.

Decisão:

```text
Dev online = EC2 (Fase 9). ECS/Fargate fica para a produção (Fase 11).
```

## Domínio próprio na V1

Subdomínio `*.kriar.shop` será obrigatório na V1.

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
A V1 deve incluir personalização 3D de produtos com Three.js (via react-three-fiber).
```

Escopo definido:

- modelos 3D criados pela Kriar;
- lojista vincula modelo ao produto;
- cliente envia arte e personaliza no storefront;
- sessão fica salva;
- arte aprovada fica congelada no pedido;
- WhatsApp será o canal de conversa da V1.

Decidido (Fase 7 — doc [30](./30_3d_customization_technical_design.md)):

- **Primeiro modelo = caneca branca de cerâmica** (GLB do Tripo3D, preparado no Blender → GLB+Draco no CDN); outros entram pelo mesmo seed.
- Arte do cliente = **só raster (PNG/JPG)** (SVG/PDF = follow-up).
- **Sem troca de cor do produto na V1** (recolor = follow-up).

## Acesso à personalização criada pelo lojista (Fase 7/8)

Contexto: na **personalização assistida pelo lojista** (o lojista monta a arte em nome do cliente, pré-cadastrado por e-mail/telefone — doc [22](22_product_customization_3d.md)), o cliente precisa **ver e aprovar** a personalização antes de comprar.

Decidido (doc [30 §9](./30_3d_customization_technical_design.md)) — **os dois caminhos**:

- **Fase 7:** **link público compartilhável** (read-only) pra ver/compartilhar + **confirmação de contato** (e-mail/telefone) pra aprovar/comprar — **sem conta**.
- **Fase 8:** com **conta do cliente**, ele também vê/aprova **logado** na área do cliente.

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
