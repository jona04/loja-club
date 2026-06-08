---
id: P0-CFG-04
title: Fila/worker (base)
phase: 0
etapa: "Etapa 1 — Fundação do projeto"
area: CFG
status: done
depends_on: [P0-CFG-03]
blocks: []
tests: [integration]
---

# P0-CFG-04 — Fila/worker (base)

## Contexto
Tarefas pesadas (thumbnails, e-mails, expiração de sessões, webhooks) devem rodar fora da requisição. Esta task fecha a **decisão da lib de fila** e cria a **interface mínima**, sem implementar tasks reais ainda.

## Docs de referência
- [03 — System Architecture](../../03_system_architecture.md)
- [13 — Performance, Cache and CDN](../../13_performance_cache_and_cdn.md)
- [12 — AWS Infrastructure and Deployment](../../12_aws_infrastructure_and_deployment.md)

## Escopo (o que ENTRA)
- Decidir a lib de fila e registrar em [18_open_decisions.md](../../18_open_decisions.md). **Recomendado: `arq`** (async, baseado em Redis, leve, casa com FastAPI async).
- `backend/pyproject.toml`: dependência da lib escolhida.
- `backend/app/core/queue.py`: interface mínima `enqueue(task_name, *args, **kwargs)` que isola o resto do código da lib.
- `compose.yml`: serviço `worker` (e `scheduler` se a lib exigir) consumindo a fila do Redis.
- Uma task de exemplo (no-op/log) para validar o caminho ponta a ponta.

## Fora de escopo (o que NÃO entra)
- Geração de thumbnails → Fase 2 (`P2-MEDIA-*`).
- E-mails de pedido → Fase 4 (`P4-NOTIF-*`).
- Limpeza de sessões expiradas e processamento de webhook → fases respectivas.

## Arquivos a criar/alterar
- `docs/18_open_decisions.md` (alterar) — registrar a lib escolhida.
- `backend/pyproject.toml` (alterar) — dep da fila.
- `backend/app/core/queue.py` (criar) — `enqueue()` + bootstrap do worker.
- `compose.yml` (alterar) — serviço `worker`.

## Passos
1. Escolher a lib (arq) e registrar a decisão.
2. Adicionar a dependência.
3. `queue.py` com `enqueue()` e a função worker.
4. Serviço `worker` no compose apontando para o Redis.
5. Enfileirar uma task dummy e ver o worker processar.

## Testes
> Fundações §10.

- **Níveis:** integração (+ unit se houver serialização pura).
- **Quando:** depois (worker no compose).
- **Cobrir:**
  - integração — `enqueue()` de uma task dummy e o worker processá-la.

## Definition of Done
- [x] Decisão da lib registrada em `18_open_decisions.md`. *(arq)*
- [x] `worker` processa uma task dummy enfileirada via `enqueue()`. *(verificado local com `arq --burst`; o serviço `worker` no compose usa o mesmo command)*
- [x] O resto do código usa só `app.core.queue.enqueue` (sem acoplar à lib).

## Notas / Reconciliações
- **Implementado (arq 0.25):** `enqueue()` (interface), `dummy_task` e `WorkerSettings`; serviço `worker` no compose (`command: arq app.core.queue.WorkerSettings`). arq tem cron embutido → sem serviço `scheduler` separado.
- **Verificado** ponta a ponta local: `enqueue('dummy_task','hello')` → `arq … --burst` processou → marcador `done` no Redis; gate `app` verde. (O container `worker` usa o mesmo command; build da imagem deferido.)
- **Teste automatizado** (criado em `P0-CI-01`): `tests/integration/test_queue_sample.py` enfileira `dummy_task` e roda um `Worker(..., burst=True)` que processa e grava o marcador no Redis.

## Follow-ups
- [ ] **Task `send_email` no worker** (INV-F5): renderiza o MJML e envia (SMTP/SES), com retry; chamada via `enqueue("send_email", ...)`. **Todo** e-mail passa por ela — inclusive o de **recuperação de senha** do template (hoje inline em `app/utils.py`), que deve ser **roteado pelo worker**. Origem: P0-CFG-04. *Quando:* ao construir as notificações (Fase 4) — ou antes, se algum e-mail transacional (recuperação/convite) for disparado antes.
