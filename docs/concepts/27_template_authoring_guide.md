# 27 — Guia: criar um template (do design ao ar)

> **Passo-a-passo** pra um template sair do uxpilot e ficar **no ar**, **escolhível** pelo lojista, com **preview navegável bonito** e servindo de **modelo**. Decisões em [26](./26_template_system.md); admin em [25](./25_platform_admin.md). Este guia é a **referência operacional** de quem cria templates.

## Quem faz o quê (e o que precisa de deploy)

| Etapa | Quem | Precisa deploy? |
|---|---|---|
| 1. Design no uxpilot | **Designer** | — |
| 2. Portar pra React (data-driven) | **Dev** | **Sim** (código) |
| 3. Escrever os manifestos | **Dev** | **Sim** (junto do código) |
| 4. Deploy do `frontend-storefront` | **Dev** | **Sim** |
| 5. Registrar + thumbnail | **Admin** | Não (dinâmico) |
| 6. Importar assets + montar a loja-demo | **Admin** | Não (dinâmico, Fase 5) |
| 7. Ativar | **Admin** | Não |
| 8. Escolher + personalizar + preview | **Lojista** | Não |

> **Regra de ouro:** a **cara** do template é **código React** — um template novo **sempre** exige um dev portar o design + deploy. O que é **dinâmico** (admin, sem deploy): registrar, importar imagens pro CDN, montar o demo, ativar. (Um "motor genérico de HTML" deixaria tudo dinâmico, mas joga fora o port fiel — fora de escopo na V1.)

---

## Passo 1 — Designer: criar no uxpilot

1. Desenha as páginas do template no uxpilot: **home**, **categoria**, **produto** (e o que mais o template tiver).
2. Exporta os **`.html`** de cada página. As imagens ficam com **URL do uxpilot** (ex.: `https://...uxpilot.../hero.png`) — **guarde essas URLs**, elas serão importadas pro CDN.
3. Salva tudo em **`docs/design/templates/<id>/`** (`.html` por página + um `_preview.png`).
4. Define o **`<id>`** do template: slug curto, minúsculo, sem espaço (ex.: `aurora`, `bazar`, `studio`).

**Saída:** `docs/design/templates/<id>/` com os `.html` e as URLs das imagens.

---

## Passo 2 — Dev: portar pra React (data-driven)

1. Cria **`frontend-storefront/templates/<id>/`** com os componentes: `Shell`, `Home`, `Category`, `Product` (+ o card de produto).
2. **Data-driven, sempre:** nada de produto/categoria/texto **hardcoded**. Os componentes recebem os **dados reais** (props vindas da API da vitrine) e leem o chrome de **`theme.settings[key] ?? default`**.
3. Respeita o **contrato** (doc [26](./26_template_system.md) — *composição ≠ contrato*): mesmos dados e mesma navegação (home → categoria → produto → carrinho) de todo template; muda só a **apresentação**.
4. Registra o template no resolver (`frontend-storefront/lib/templates.ts`) — `<id>` → seus componentes.

**Saída:** o template **renderiza** qualquer loja que o selecione.

---

## Passo 3 — Dev: escrever os manifestos

Dois arquivos em **`frontend-storefront/templates/<id>/`** (**fonte única**: o template React importa e o backend lê):

**`settings-schema.json`** — os campos **editáveis** do chrome. Lista de `{ key, type, label, group, default, max_length? }` (`type` ∈ `text|textarea|image|boolean|select`). Campo `image` tem `default` = a **URL do uxpilot** da imagem original:

```json
[
  { "key": "announcement_text", "type": "text", "label": "Barra de anúncio", "group": "Topo", "default": "", "max_length": 120 },
  { "key": "hero_subtitle", "type": "textarea", "label": "Subtítulo do hero", "group": "Home", "default": "" },
  { "key": "hero_image", "type": "image", "label": "Imagem do hero", "group": "Home", "default": "https://uxpilot.../hero.png" }
]
```

**`demo.json`** — o **conteúdo demo** (o que faz a vitrine-demo ficar **igual ao design**): categorias + produtos (nome/preço/categoria) com a **URL de imagem** (uxpilot) de cada um. Preço em **unidades menores** (centavos, BRL):

```json
{
  "categories": [
    { "name": "Camisetas", "slug": "camisetas" },
    { "name": "Canecas",   "slug": "canecas" }
  ],
  "products": [
    { "name": "Camiseta Premium", "slug": "camiseta-premium", "price": 7900, "category": "camisetas", "image": "https://uxpilot.../camiseta.png" },
    { "name": "Caneca Térmica",   "slug": "caneca-termica",   "price": 5900, "category": "canecas",   "image": "https://uxpilot.../caneca.png" }
  ]
}
```

> Para **Aurora/Bazar/Studio**, esses `demo.json` são **transcritos do `docs/design/`** agora (carga "artificial") — mas pelo **mesmo formato** de um template futuro, então **não é descartável**.

**Saída:** o template declara seu chrome editável **e** seu conteúdo demo.

---

## Passo 4 — Dev: deploy do `frontend-storefront`

1. Faz o **deploy** — código + manifestos vão pro ar. **Sem deploy o template não renderiza** (a vitrine é React).
2. No deploy/prestart, o **backend seeda** o `content_theme_templates.settings_schema` a partir do `settings-schema.json`. A `frontend-storefront` é deployada separada, então **a imagem do backend embarca os manifestos**: o `backend/Dockerfile` copia `frontend-storefront/templates/` pra dentro da imagem, pro seed conseguir lê-los. As imagens ainda apontam pro uxpilot — o passo 6 as move pro CDN.

**Saída:** o código do template está no ar; o schema, no banco.

---

## Passo 5 — Admin: registrar o template

No **`frontend-admin`** (`admin.${DOMAIN}`):

1. **Cria o template** (id/nome/descrição) → `POST /platform/templates` (gated `platform.templates.manage`).
2. Sobe o **thumbnail** → CDN → `POST /platform/templates/{id}/thumbnail`.
3. O `settings_schema` já está seedado (passo 4).

**Saída:** o template existe no admin, com thumbnail no CDN.

---

## Passo 6 — Admin: importar os assets + montar a loja-demo *(Fase 5)*

1. **Importar assets** (`import_assets`): a plataforma lê os manifestos, **baixa cada URL do uxpilot → S3/CloudFront** e **reescreve** as referências pra **URL do CDN** (nos defaults `image` do schema **e** no catálogo do demo). Acaba a dependência do uxpilot.
2. **Montar a loja-demo:** a plataforma cria/atualiza a **loja-demo do template** (`<id>-demo`) a partir do `demo.json` (categorias/produtos), com as imagens **já no CDN** e `active_template_id = <id>`.
3. **Mesmo caminho** pra Aurora/Bazar/Studio (carga agora) **e** pra qualquer template futuro.

**Saída:** a loja-demo do template existe, bonita, com imagens no CDN — pronta pra preview.

---

## Passo 7 — Admin: ativar

- `is_active = true` (`PATCH /platform/templates/{id}`) → o template passa a aparecer no **picker** do lojista.

---

## Passo 8 — Lojista *(Fase 5)*: escolher + personalizar + ver o preview

1. **Escolhe** o template no picker (vê o thumbnail).
2. **Personaliza** pelo **form gerado do schema** (textos/imagens do chrome) — valores por **loja × template**.
3. Abre o **preview navegável**: o storefront servindo a **loja-demo** do template — cada clique navega (home → categoria → produto → carrinho). É o **modelo bonito** que ele copia pra própria loja.

---

## Checklist

- [ ] **Designer:** `.html` + imagens em `docs/design/templates/<id>/`.
- [ ] **Dev:** componentes React **data-driven** em `frontend-storefront/templates/<id>/` + registro no resolver.
- [ ] **Dev:** `settings-schema.json` + `demo.json` (com as URLs do uxpilot).
- [ ] **Dev:** deploy do `frontend-storefront` (schema seedado).
- [ ] **Admin:** registrar template + thumbnail no CDN.
- [ ] **Admin (Fase 5):** `import_assets` (imagens → CDN) + montar a loja-demo.
- [ ] **Admin:** ativar.
- [ ] **Lojista (Fase 5):** escolhe + personaliza + abre o preview navegável.
