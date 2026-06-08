---
id: P2-CUST-03
title: product_customization — rotas (sessão/autosave/upload/aprovar/expirar/merchant)
phase: 2
etapa: "Etapa 6 — Personalização 3D"
area: CUST
status: todo
depends_on: [P2-CUST-02, P2-MEDIA-02]
blocks: [P2-FE-02]
tests: [integration]
---

# P2-CUST-03 — `product_customization`: serviço e rotas

## Contexto
A API das sessões de personalização (doc [22](../../22_product_customization_3d.md)): cliente cria/edita/aprova; lojista visualiza. O **editor 3D (Three.js) é Fase 3** (storefront) — aqui só o backend + a visão do lojista.

## Docs de referência
- [22 — Product Customization 3D](../../22_product_customization_3d.md) (fluxo, aprovação, status de arte)
- [14 — Security](../../14_security_strategy.md) (arte privada, URL assinada, auditoria de acesso)
- [13 — Performance/Cache/CDN](../../13_performance_cache_and_cdn.md) (cache `customization_session:{id}`, expiração por worker)
- [20 — API Contracts](../../20_api_contracts_todo.md)

## Escopo (o que ENTRA)
- **Cliente (sem login; `guest_session_id`):** iniciar sessão; obter sessão; **autosave** do `state_json`; **upload de arte** (validado, **privado** → S3, acesso por URL assinada); registrar `preview_url`; **aprovar** (congela `state_json` + arquivo original + preview + `approved_snapshot_url` + `model_version_id` + `approved_at`; status → `approved`).
- **Lojista (gated `customization.*`):** listar sessões da própria loja; obter sessão; baixar arte (URL assinada); atualizar **status de arte/produção** (`received…production_done`).
- **Expiração:** worker marca sessões > 30 dias sem virar pedido como `expired` + `deleted_at` (sem hard delete).

## Fora de escopo (o que NÃO entra)
- Editor 3D do cliente (Three.js) → Fase 3. Consumo no carrinho/pedido → Fase 4. Identidade do cliente/guest completa → Fase 4 (aqui `guest_session_id` é interface opaca).

## Arquivos a criar/alterar
- `backend/app/modules/product_customization/services.py`/`repositories.py`/`routes.py`/`schemas.py` (preencher).
- Worker de expiração; `api/router.py` (incluir); regenerar client.

## Passos
1. Sessão: criar/obter/autosave; upload privado (storage presigned).
2. Aprovar (congelar snapshot/versão/data).
3. Visão do lojista (listar/baixar/status) + worker de expiração.

## Testes
> Fundações §10. Permissão/arquivo privado/isolamento são fronteiras reais → integração.

- **Cobrir:** ciclo da sessão (criar→autosave→upload→aprovar); aprovar congela o snapshot; lojista só vê sessões da própria loja (isolamento); arte é privada (URL assinada, não pública); expiração → `expired`+`deleted_at`.

## Definition of Done
- [ ] Sessões (criar/autosave/upload/preview/aprovar) + visão do lojista + expiração por worker.
- [ ] Arte privada por URL assinada; isolamento por `store_id`.
- [ ] Client regenerado; lint/tests/cobertura verdes.
- [ ] Itens adiados varridos → Follow-ups + README (ou "nenhum").

## Notas / Reconciliações
- **Guest/customer:** a identidade completa do cliente é Fase 4; aqui `guest_session_id` entra como interface (sem auth de cliente). Registrar.

## Follow-ups
- (preencher)
