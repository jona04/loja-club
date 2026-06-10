---
id: P4-ADMIN-03
title: Telas de templates no admin — CRUD + thumbnail + schema
phase: 4
etapa: "Etapa 3 — Cadastro/gestão de templates"
area: ADMIN
status: todo
depends_on: [P4-ADMIN-01, P4-TPL-01, P4-TPL-02]
tests: [e2e]
---

# P4-ADMIN-03 — Telas de gestão de templates (frontend-admin)

## Contexto
As telas do `frontend-admin` que consomem o registro de templates: a equipe cria/edita um template (metadados/status), **sobe o thumbnail pro CDN** e **vê o schema** (read-only). Alimenta a Fase 5 (onde entram o import de imagens, a loja-demo por template e o preview navegável).

## Docs de referência
- [26 — Template System](../../26_template_system.md)
- [27 — Guia de autoria de template](../../27_template_authoring_guide.md)
- [25 — Platform Admin](../../25_platform_admin.md)
- [05 — Frontend Architecture](../../05_frontend_architecture.md)

## Escopo (o que ENTRA)
- Lista + CRUD de templates (metadados/status) — consome `P4-TPL-01`.
- **Upload de thumbnail** (→ `P4-TPL-02`), mostrando a URL de CDN resultante.
- Visualização (read-only) do `settings_schema` do template (vem do código).

## Fora de escopo (o que NÃO entra)
- Backend (registro/thumbnail) → `P4-TPL-01`/`02`.
- **Edição** do schema (é do código, não editável no admin) — só leitura.
- **Import de imagens (chrome/demo), loja-demo por template e preview navegável** → **Fase 5** (o botão "abrir preview" entra quando a Fase 5 entregar o preview).
- Form do lojista (consumo do schema) → **Fase 5**.

## Arquivos a criar/alterar
- `frontend-admin/src/routes/...` (criar) — telas de templates.
- `frontend-admin/src/components/...` (criar) — upload de thumbnail + visual do schema (read-only).

## Passos
1. Lista + CRUD de templates.
2. Upload de thumbnail com preview da URL de CDN.
3. Schema read-only; validar via Traefik (`admin.localhost`).

## Testes
> Regra em [`_foundations-and-bottlenecks.md`](../_foundations-and-bottlenecks.md) §10.
- **Níveis:** e2e (smoke) + `tsc`/`biome`.
- **Cobrir:** criar/ativar template; upload de thumbnail reflete a URL de CDN; schema só leitura.

## Definition of Done
- [ ] Telas de CRUD de template + upload de thumbnail (CDN) + schema read-only.
- [ ] Gates (`tsc`/`biome`) + smoke.
- [ ] **Modos de falha / edge cases mapeados** → tratados ou Follow-ups.
- [ ] **Itens adiados varridos** → Follow-ups + README.

## Notas / Reconciliações
- Fecha o follow-up `P3-TPL-03` ("Admin pra cadastrar templates") — marcar `[x]` na origem (README da Fase 3) ao concluir.
- **Preview navegável** saiu pra **Fase 5** (depende da loja-demo por template + import de imagens + a vitrine lendo `theme.settings`) — aqui o admin só **registra + thumbnail + schema**.

## Follow-ups
- [ ] — (preencher ao implementar) → README da fase.
