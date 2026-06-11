---
id: P5-DEMO-02
title: Loja-demo por template (<id>-demo do demo.json)
phase: 5
etapa: "Etapa 4 — Loja-demo + import de assets"
area: DEMO
status: todo
depends_on: [P5-DEMO-01]
blocks: [P5-PREV-01]
tests: [integration]
---

# P5-DEMO-02 — Loja-demo por template

## Contexto
Cada template tem uma **loja-demo própria** (`aurora-demo`/`bazar-demo`/`studio-demo`): uma `store` real, com o template aplicado + catálogo/imagens/textos do `demo.json` (= o design). É o **preview navegável** e o **modelo** que o lojista copia.

## Docs de referência
- [26 — Sistema de templates](../../concepts/26_template_system.md) (§"A loja-demo (por template)")
- [27 — Guia de autoria](../../concepts/27_template_authoring_guide.md) (Passo 6)

## Escopo (o que ENTRA)
- **Monta a loja-demo** de cada template (`<id>-demo`): `store` real com `active_template_id = <id>` + catálogo do `demo.json` (imagens **já no CDN** via `P5-DEMO-01`). **Idempotente**.
- **Reusa tudo** (store/catalog/storefront/settings) — zero render especial; a loja-demo é servida como qualquer vitrine.
- **Aurora/Bazar/Studio** ganham sua loja-demo (carga do `docs/design/`, pelo **mesmo caminho** de um template futuro).

## Fora de escopo (o que NÃO entra)
- O `import_assets` em si: `P5-DEMO-01`.
- O painel abrir o preview navegável: `P5-PREV-01`.

## Arquivos a criar/alterar
- `backend/app/modules/.../seed_template_demo_store` (criar) — cria/atualiza a loja-demo a partir do `demo.json`.

## Passos
1. A partir do `demo.json` (+ imagens no CDN), cria/atualiza a `store` `<id>-demo` (categorias/produtos publicados), `active_template_id = <id>`.
2. Idempotente (re-rodar não duplica).
3. Roda pros 3 templates.

## Testes
- **Níveis:** integração.
- **Quando escrever:** durante.
- **Cobrir:** integração — monta a loja-demo (catálogo do demo, template ativo), idempotente; a vitrine serve a loja-demo como qualquer loja.

## Definition of Done
- [ ] `<id>-demo` montada pros 3 templates (catálogo do demo, imgs no CDN, template ativo).
- [ ] Idempotente.
- [ ] Servida pela vitrine como loja normal (smoke).
- [ ] **Modos de falha mapeados** (`demo.json` inválido, slug colidindo, re-seed) → tratados ou Follow-ups.
- [ ] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- —

## Follow-ups
- [ ] — nenhum (preencher ao implementar).
