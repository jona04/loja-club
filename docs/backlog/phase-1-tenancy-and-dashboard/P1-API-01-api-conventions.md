---
id: P1-API-01
title: Padrão de API (response/erro/paginação/tenant)
phase: 1
etapa: "Etapa 1 — Padrão de API"
area: API
status: done
depends_on: []
blocks: [P1-STORE-02, P1-DOM-01]
tests: [unit, integration]
---

# P1-API-01 — Padrão de API (response/erro/paginação/headers de tenant)

## Contexto
As Fundações mandam **travar o padrão de API na primeira API real (Fase 1)** para não retrabalhar depois de dezenas de endpoints (INV-A1/A2, GARGALO §5; DEC-5 paginação pendente). O doc [20](../../concepts/20_api_contracts_todo.md) ainda é um TODO. Esta task fixa as convenções que todos os endpoints da loja reusarão.

## Docs de referência
- [20 — API Contracts TODO](../../concepts/20_api_contracts_todo.md)
- [Fundações §5 (API) + DEC-5](../_foundations-and-bottlenecks.md)
- [06 — Multitenancy and Domains](../../concepts/06_multitenancy_and_domains.md)
- [14 — Security Strategy](../../concepts/14_security_strategy.md)

## Escopo (o que ENTRA)
- **URL/versão:** `/api/v1`; painel sob `/api/v1/stores/{store_id}/...`; APIs públicas do storefront resolvem a loja pelo `Host` (consumo na Fase 3, só a convenção aqui). INV-A1.
- **Paginação (resolver DEC-5):** decidir **offset (`skip`/`limit`)** — já usado no template (`UsersPublic` = `{data, count}`) — vs cursor; documentar a escolha e padronizar o envelope de lista (`{data: [...], count: <total>}`).
- **Response:** recurso único = objeto direto; lista = envelope de paginação acima. Tipo genérico reutilizável de paginação.
- **Erro:** formato unificado para erros de negócio/validação (manter `{detail}` do FastAPI e/ou padronizar `code`/`message`); decidir e documentar (sem vazar dado interno — doc [06](../../concepts/06_multitenancy_and_domains.md) "loja não encontrada").
- **Headers/identificação de tenant:** painel → `store_id` no path (não header); storefront → `Host`. Documentar.
- **Idempotency-Key:** reservar a convenção para operações sensíveis (criar pedido/pagamento) — implementação Fase 6/7 (INV-A3); só documentar aqui.

## Fora de escopo (o que NÃO entra)
- Contratos detalhados por módulo (cada fase define os seus).
- Contratos públicos do storefront e webhooks → Fase 3 / Fase 8.
- Rate limit → baseline Fase 6 (INV-S5).

## Arquivos a criar/alterar
- `backend/app/core/api.py` (criar) — tipo genérico de paginação (`Page[T]`/envelope `{data, count}`) e params de paginação reutilizáveis; helper de erro se necessário.
- `docs/concepts/20_api_contracts_todo.md` (alterar) — preencher os TODOs decididos (URL, response, erro, paginação, headers de tenant).
- `docs/backlog/_foundations-and-bottlenecks.md` (alterar) — marcar **DEC-5** como decidido.

## Passos
1. Decidir paginação (recomendado: offset `skip`/`limit` + `{data, count}`, alinhado ao template) e formato de erro.
2. Criar os tipos/params reutilizáveis em `app/core/api.py`.
3. Atualizar o doc 20 e o status de DEC-5 nas Fundações.
4. Validar o padrão em um endpoint real quando `P1-STORE-02` existir (lista de lojas).

## Testes
> Fundações §10.

- **Níveis:** unit (serialização do envelope/paginação, params) · integração (um endpoint real seguindo o padrão — feito junto de `P1-STORE-02`).
- **Quando escrever:** antes (contrato claro, estilo TDD para o tipo de paginação).
- **Cobrir:**
  - unit — envelope `{data, count}` serializa; `skip`/`limit` com limites/validação.
  - integração — `GET /api/v1/stores` (em `P1-STORE-02`) responde no padrão.

## Definition of Done
- [x] Convenções (URL, response, erro, paginação, tenant) **documentadas** no doc [20](../../concepts/20_api_contracts_todo.md).
- [x] Tipos/params de paginação reutilizáveis em `app/core/api.py`, com unit verde *(73 testes; cobertura 91%)*.
- [x] **DEC-5** marcada como decidida nas Fundações.

## Notas / Reconciliações
- **Decisões travadas:** paginação **offset** (`skip`/`limit`) + envelope `{data, count}` (DEC-5); erro **estruturado** `{error: {code, message, details?}}`.
- **Implementado:** `app/core/api.py` com `Page[T]`, `pagination_params`, `ErrorResponse`/`ErrorDetail`, `AppError` e `register_exception_handlers` (registrado no `main.py`). Handlers convertem `HTTPException` (status→`code`) e `RequestValidationError` (`validation_error` + `details`) para o envelope — **não foi preciso reescrever** as 27 `HTTPException(detail=...)` existentes.
- **Migração do `{detail}`:** o template usava `{detail}`. Ajustados os testes da Fase 0 (`test_login`/`test_users`) e o `frontend-dashboard/src/utils.ts` (`extractErrorMessage` lê `error.message`, com fallback para `detail`). `EditUser.tsx` só tinha "detail" como texto de UI.
- **OpenAPI:** o schema de erro não foi declarado por rota (o front lê `err.body` de forma defensiva); declarar `responses=` por endpoint fica como melhoria futura se precisarmos do tipo no client gerado.
- **`details` sempre presente** (`null` quando ausente) para schema consistente.
- **Erros inesperados (500):** handler de `Exception` genérica responde no **mesmo envelope** (`{error:{code:"internal_error", ...}}`, **sem vazar traceback**) e **loga** o traceback server-side (`logger`, `exc_info`); 5xx de `AppError`/`HTTPException` também logados (4xx não, pra não poluir). Fecha o padrão de erro. **Observabilidade completa** (structured logging, request-id, log de auditoria, ativar Sentry, rate limit) é **Fase 9** (Fundações: observabilidade → Fase 9).

## Follow-ups
- [ ] **Tipar o schema de erro no OpenAPI** (`responses=` com `ErrorResponse` por endpoint) para o client gerado carregar o tipo do erro. *Quando:* se/quando o frontend precisar do tipo (hoje lê `err.body` defensivamente). → README da fase.
