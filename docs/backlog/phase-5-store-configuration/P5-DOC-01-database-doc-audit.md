---
id: P5-DOC-01
title: Auditoria do doc de banco (tabelas + índices vs código)
phase: 5
etapa: "Etapa 1 — Groundwork (e2e + doc de banco)"
area: DOC
status: todo
depends_on: []
blocks: []
tests: none
---

# P5-DOC-01 — Auditoria do doc de banco

## Contexto
Conforme as tabelas foram criadas (Fases 0–4), o doc [07](../../concepts/07_database_strategy.md) pode ter ficado para trás (tabela/índice no código sem estar no doc, ou nome divergente). A **fonte de verdade é a doc** — esta task garante que **toda** tabela e índice já criados estão no doc 07, atualizando-o onde faltar.

## Docs de referência
- [07 — Database Strategy](../../concepts/07_database_strategy.md)

## Escopo (o que ENTRA)
- **Inventário do real:** listar todas as tabelas (`__tablename__` em `app/modules/*/models.py`) e índices/uniques (migrations / `Index(...)`) efetivamente criados.
- **Conferir contra o doc 07:** tabela presente? na lista certa (global vs por-loja)? índice documentado? `store_id` correto?
- **Atualizar o doc 07** com o que faltar/divergir (nomes, colunas-chave, índices) — sem inventar; só **refletir o código**.

## Fora de escopo (o que NÃO entra)
- Mudar o schema do banco (esta task ajusta só **doc**).
- `content_store_template_settings` (criada na `P5-CFG-01`, que já documenta) — esta auditoria cobre o que **já existe**.

## Arquivos a criar/alterar
- `docs/concepts/07_database_strategy.md` (alterar) — tabelas/índices faltantes ou divergentes.

## Passos
1. Extrair `__tablename__` de todos os módulos + os `Index`/`unique` das migrations.
2. Diff contra as tabelas/índices do doc 07.
3. Adicionar/corrigir no doc 07 (listas "Tabelas globais"/"por loja" + "Índices completos iniciais").

## Testes
- **Níveis:** nenhum automatizado (auditoria de doc).
- **Cobrir:** revisão — `alembic check` vazio confirma models ↔ migrations; a auditoria confirma migrations ↔ doc.

## Definition of Done
- [ ] Toda tabela criada (Fases 0–4) está no doc 07, na lista certa (global/por-loja).
- [ ] Todo índice/unique relevante está na seção "Índices completos iniciais".
- [ ] Divergências de nome/coluna corrigidas no doc.
- [ ] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- Divergências encontradas listadas aqui (citar a tabela).

## Follow-ups
- [ ] — nenhum (preencher ao implementar).
