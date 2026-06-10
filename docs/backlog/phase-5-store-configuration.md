# Fase 5 — Configuração da loja pelo lojista

> Objetivo: com os templates **cadastrados pela plataforma** (admin, [Fase 4](./phase-4-platform-admin.md)), o lojista **escolhe e personaliza** o template da loja dele — a **personalização schema-driven** (`P3-TPL-04`) + o **preview navegável completo**. É o "cadastrar/configurar a loja" pelo lojista, no painel (`app.${DOMAIN}`).

> **Depende da Fase 4:** o **settings schema** e os **assets no CDN** (imagens-default) de cada template são cadastrados no admin; aqui o lojista **consome** isso. O picker de template + upload de banner + preview por imagem já existem desde a **[Fase 3](./phase-3-storefront-and-layouts.md)** (`P3-TPL-03`).

Docs de referência: [26](../26_template_system.md) (sistema de templates), [09](../09_merchant_dashboard.md) (painel), [10](../10_storefront_and_layouts.md) (storefront), [25](../25_platform_admin.md) (de onde vêm os templates/schema/CDN).

## Definition of Done da fase
- O lojista **personaliza o template** por um **form gerado do schema** (campos do template ativo), com valores por **loja × template** (não perde ao trocar) e **reset** (excluir → volta aos defaults).
- A **vitrine reflete** os settings (defaults quando vazio); **campos de imagem** têm default = a imagem original do template **no CDN**.
- O painel abre o **preview navegável completo** do template (outra aba).

## Escopo

### Personalização schema-driven (`P3-TPL-04`)
- [ ] `settings_schema` por template (vem da [Fase 4](./phase-4-platform-admin.md)) → **form genérico** no painel (`TemplateSettingsForm`, render por tipo: `text/textarea/image/boolean/select`). Doc [26](../26_template_system.md).
- [ ] Valores por **loja × template** (`content_store_template_settings`, soft delete; **resetar = excluir** → re-selecionar zera). **"Meus templates"** lista os já editados.
- [ ] API pública: `theme.settings` (defaults do schema **mesclados** com overrides) do template **ativo**; a vitrine (Aurora/Bazar/Studio) lê `theme.settings[key] ?? default`.
- [ ] **Campos de imagem com default no CDN** — a imagem original do template (cadastrada na Fase 4) preenche o default; nunca fundo vazio.

### Preview navegável completo
- [ ] Botão **"ver preview completo"** no painel → abre, em **outra aba**, o **template navegável** (storefront renderizando a **loja-demo** com o template) — cada clique funciona. Doc [26](../26_template_system.md).

## Fora de escopo
- **Cores do tema por loja** (acento aplicado a cada template) → task à parte (cada template usa as cores originais por ora).
- **Editor visual drag-drop / reordenar blocos livres** → V1 = campos declarados no schema.
- **Cadastro de template novo** (admin) → [Fase 4](./phase-4-platform-admin.md).

## Reconciliações
- A **personalização do lojista** (`P3-TPL-04`) é desta fase — **depende** do admin (Fase 4) cadastrar templates/schema/CDN. A Fase 3 entrega os 3 templates + picker + banner + preview por imagem. Decisões no doc [26](../26_template_system.md).
