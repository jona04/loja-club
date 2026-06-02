---
id: P0-CFG-01
title: Branding Loja Club
phase: 0
etapa: "Etapa 1 — Fundação do projeto"
area: CFG
status: todo
depends_on: []
blocks: []
tests: none
---

# P0-CFG-01 — Branding Loja Club

## Contexto
O projeto foi gerado do Full Stack FastAPI Template e ainda está com a identidade do template: `PROJECT_NAME="Full Stack FastAPI Project"`, título do template no frontend, nomes de stack genéricos. Esta task dá a cara da Loja Club.

## Docs de referência
- [04 — FastAPI Template Adaptation](../../04_fastapi_template_adaptation.md)

## Escopo (o que ENTRA)
- `.env`: `PROJECT_NAME="Loja Club"`, `STACK_NAME=loja-club`, `DOCKER_IMAGE_BACKEND=loja-club-backend`, `DOCKER_IMAGE_FRONTEND=loja-club-frontend`.
- `frontend/index.html`: `<title>` e favicon da Loja Club.
- `README.md` (raiz) e `copier.yml`: nome do projeto Loja Club.
- Confirmar que `EMAILS_FROM_NAME` herda de `PROJECT_NAME` (já há `_set_default_emails_from` em `config.py`).

## Fora de escopo (o que NÃO entra)
- Paleta, logo final, design system completo → doc [21](../../21_design_system_todo.md), fases de frontend.
- Domínio, CORS e secrets → `P0-CFG-02`.

## Arquivos a criar/alterar
- `.env` (alterar) — `PROJECT_NAME`, `STACK_NAME`, `DOCKER_IMAGE_*`.
- `frontend/index.html` (alterar) — título.
- `frontend/public/` (alterar) — favicon placeholder Loja Club.
- `README.md` (alterar) — nome/descrição.
- `copier.yml` (alterar) — nome do projeto.

## Passos
1. Editar `.env` com os valores acima.
2. Trocar título em `frontend/index.html` e o favicon em `frontend/public/`.
3. Ajustar `README.md` e `copier.yml`.
4. Subir local e conferir título + nome nos e-mails (Mailcatcher).

## Testes
> Fundações §10. Branding/config visual — sem teste automatizado.

- **Níveis:** nenhum automatizado (verificação manual está no DoD).
- **Quando:** —

## Definition of Done
- [ ] Painel abre com título "Loja Club".
- [ ] E-mails de teste usam o nome "Loja Club" como remetente.
- [ ] Containers locais usam o prefixo `loja-club-*` (via `STACK_NAME`/`DOCKER_IMAGE_*`).

## Notas / Reconciliações
- Sem divergência com docs: é só configuração/branding do template.
