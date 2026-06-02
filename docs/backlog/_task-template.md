---
id: PX-AREA-NN          # ex.: P0-MOD-04 — estável; não muda mesmo que o título mude
title: Título curto da task
phase: 0                # número da fase
etapa: "Etapa N — Nome da etapa do roadmap"
area: AREA              # sigla curta do domínio (CFG, MOD, CI, STORE, CATALOG, ...)
status: todo            # todo | doing | blocked | done
depends_on: []          # ex.: [P0-MOD-02] — precisa estar done antes
blocks: []              # ex.: [P1-STORE-02] — o que esta task destrava (opcional)
tests: tbd              # [unit] | [integration] | [unit, integration] | [e2e] | none | tbd
---

# PX-AREA-NN — Título da task

## Contexto
Por que esta task existe, em 1–3 linhas. Liga ao objetivo da etapa/fase.

## Docs de referência
- [NN — Título do doc](../../NN_arquivo.md)

## Escopo (o que ENTRA)
- item objetivo e testável
- ...

## Fora de escopo (o que NÃO entra)
- o que pertence a outra task (citar o ID): pertence a `PX-AAA-NN`
- ...

## Arquivos a criar/alterar
- `caminho/arquivo` (criar | alterar | remover) — o quê

## Passos
1. passo concreto
2. ...

## Testes
> Regra em [`_foundations-and-bottlenecks.md`](./_foundations-and-bottlenecks.md) §10. Preencha os níveis; use `a decidir` só se realmente não der pra saber agora.

- **Níveis:** unit · integração · E2E — (ou `nenhum automatizado` p/ config/manual, ou `a decidir`)
- **Quando escrever:** antes (lógica/contrato claros, estilo TDD) · durante · depois
- **Cobrir:**
  - unit — …
  - integração — …
  - e2e — …

## Definition of Done
- [ ] critério testável 1
- [ ] critério testável 2
- [ ] código novo segue as convenções do `CLAUDE.md` (docstrings Google completas, type hints)

## Notas / Reconciliações
- divergências código ↔ doc resolvidas aqui (citar o doc afetado)
