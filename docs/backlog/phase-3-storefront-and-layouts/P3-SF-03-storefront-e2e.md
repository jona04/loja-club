---
id: P3-SF-03
title: E2E do storefront (Playwright) + gate de CI de todos os frontends
phase: 3
etapa: "Etapa 1 — Projeto frontend-storefront"
area: SF
status: todo
depends_on: [P3-SF-02]
tests: [e2e]
---

# P3-SF-03 — E2E do `frontend-storefront` (Playwright)

## Contexto
O `frontend-dashboard` tem e2e Playwright e o `frontend-admin` ganhou na `P4-ADMIN-01`. O **`frontend-storefront` ainda NÃO tem** (validou só por "smoke real" do backend). Esta task adiciona o e2e Playwright do storefront **e firma a regra de release**: só sobe pra produção o que passa no e2e de **TODOS** os frontends.

## Docs de referência
- [16 — Testing Strategy](../../16_testing_strategy.md)
- [10 — Storefront and Layouts](../../10_storefront_and_layouts.md)
- [05 — Frontend Architecture](../../05_frontend_architecture.md)
- [12 — AWS Infra & Deployment](../../12_aws_infrastructure_and_deployment.md) (CI/CD)

## Escopo (o que ENTRA)
- `frontend-storefront/playwright.config.ts` + `Dockerfile.playwright` + service `playwright-storefront` no `compose.override.yml` (espelhando dashboard/admin).
- Specs da **navegação real** da vitrine: home → categoria → produto; **host desconhecido → "loja não encontrada"**; resolução por **Host** (`X-Forwarded-Host`).
- **Regra de release (vale p/ TODOS os frontends):** o e2e de **dashboard + admin + storefront** roda no **CI** e **bloqueia o deploy** — nenhuma vitrine/painel sobe com e2e vermelho. (O **wiring** do gate no pipeline é a **[Fase 9](../phase-9-platform-ops-and-production.md)**, Etapa 2 — CI/CD.)

## Fora de escopo (o que NÃO entra)
- Carrinho/checkout reais → Fase 6.
- O **wiring do pipeline CI/CD** em si → Fase 9 (esta task entrega os **testes** + **a regra**).

## Arquivos a criar/alterar
- `frontend-storefront/{playwright.config.ts,Dockerfile.playwright,tests/*}` (criar).
- `compose.override.yml` (alterar) — service `playwright-storefront`.
- README da Fase 3 + Fase 9 (registrar a regra do gate).

## Passos
1. Config + Dockerfile.playwright + service, adaptando pro **Next.js** (o storefront não é Vite; o Playwright sobe o dev server do Next na porta da vitrine).
2. Specs: home/categoria/produto navegam; host desconhecido → not-found.
3. Rodar `docker compose run --rm playwright-storefront bunx playwright test` verde local.

## Testes
- **Níveis:** e2e (Playwright) — navegação real da vitrine, resolvida por Host.
- **Cobrir:** home → categoria → produto; loja inexistente → "loja não encontrada".

## Definition of Done
- [ ] Storefront com Playwright (config + Dockerfile.playwright + compose + specs) **verde local**.
- [ ] **Regra registrada:** "e2e de **todos** os frontends no **CI** bloqueia o deploy" (Fase 9 implementa o gate).
- [ ] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- **Funde** o follow-up "**Lint/test do `frontend-storefront` nos gates**" (`P3-FE-01`) — o storefront passa a ter testes próprios nos gates.
- O storefront é **Next.js** (não Vite); o `webServer` do Playwright sobe o dev do Next — adaptar do padrão dashboard/admin.

## Follow-ups
- [ ] — (preencher ao implementar) → README da fase.
