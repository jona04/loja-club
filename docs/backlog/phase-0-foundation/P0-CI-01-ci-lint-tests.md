---
id: P0-CI-01
title: CI, lint, testes e client OpenAPI
phase: 0
etapa: "Etapa 2 — Refatoração modular"
area: CI
status: todo
depends_on: [P0-MOD-03, P0-MOD-04]
blocks: []
---

# P0-CI-01 — CI, lint, testes e client OpenAPI

## Contexto
Depois do refactor modular (módulos, remoção de `items`, `account_users`), o CI, os scripts e o client OpenAPI do frontend precisam refletir a nova estrutura e continuar verdes.

## Docs de referência
- [16 — Testing Strategy](../../16_testing_strategy.md)

## Escopo (o que ENTRA)
- Ajustar GitHub Actions (`.github/workflows/`) e `.pre-commit-config.yaml` para os novos paths de `app/modules/*`.
- Garantir `backend/scripts/lint.sh`, `format.sh`, `test.sh` rodando na estrutura nova.
- Ajustar/limpar testes do template que referenciam `items`/`user` antigos.
- Regenerar o client OpenAPI do frontend (`npm run generate-client`) após mudanças de rota.

## Fora de escopo (o que NÃO entra)
- Build de imagens + deploy automatizado (CD) → Fase 6 (`P6-CICD-*`).
- Novos testes de domínio (multi-tenant, catálogo, etc.) → fases respectivas.

## Arquivos a criar/alterar
- `.github/workflows/*` (alterar) — paths/jobs.
- `.pre-commit-config.yaml` (alterar).
- `backend/tests/*` (alterar) — remover/ajustar testes de item/user antigos.
- `frontend/src/client/*` (regenerar).

## Passos
1. Rodar lint/format/test localmente e corrigir o que o refactor quebrou.
2. Atualizar workflows e pre-commit.
3. Regenerar o client OpenAPI e ajustar imports no frontend.
4. Conferir o CI no push.

## Definition of Done
- [ ] `lint` + type check + testes do backend passam localmente.
- [ ] Client OpenAPI regenerado, sem referências a endpoints removidos.
- [ ] CI verde no GitHub Actions.

## Notas / Reconciliações
- Esta é a parte de **CI** (Etapa 1 do roadmap). O **CD** (deploy automatizado) é a Etapa 21, na Fase 6.
