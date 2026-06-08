# Loja Club — instruções do projeto

SaaS de ecommerce multi-tenant. Documentação conceitual em `docs/01..24`; **backlog acionável** em `docs/backlog/`; **invariantes e decisões** em `docs/backlog/_foundations-and-bottlenecks.md`.

## Regra de ouro
O código imita a lógica dos docs — **não inventar lógica de negócio nova**. Se uma limitação técnica impedir seguir o doc, atualizar o `.md` para refletir o código; **nunca** deixar doc e código divergentes.

## Git (importante)
**Nunca** executar operações de git que alterem estado: sem `commit`, `push`, `branch`, `checkout`/`switch`, `merge`, `reset`, `rebase`, `stash`. **O usuário gerencia o git.** Implementar **sempre na branch atual** (a que estiver checada) — não criar nem trocar de branch. Rodar git (mesmo só-leitura, como `git status`/`git diff`) **apenas se o usuário pedir**.

## Como rodar e testar (dev)
Portas do stack são **não-padrão** (db `5442`, redis `6399`, backend `8800`, painel `5180`) — código/testes no host precisam delas. Guias: [`backend/README.md`](backend/README.md) / [`frontend/README.md`](frontend/README.md).

- **Infra:** `docker compose up -d --wait db redis` (antes de rodar testes no host).
- **Lint (backend):** `uv run bash scripts/lint.sh` — sempre via `uv run` (o script chama `mypy`/`ruff` puros; precisa do venv). Gate = mypy + ty + ruff + format.
- **Testes (backend):** `POSTGRES_PORT=5442 REDIS_PORT=6399 uv run coverage run -m pytest tests/` + `… coverage report --fail-under=90`.
- **Migrations:** `… uv run alembic upgrade head`; ao mudar modelos, `alembic revision --autogenerate` → **revisar** (ordem de FK, nomear FKs) e `alembic check` deve voltar **vazio**.
- **Frontend:** bun **não** está instalado localmente → usar os binários da raiz `../node_modules/.bin/{vite,vitest,biome,tsc}` (workspace bun: `node_modules`/lockfile únicos na raiz).

## Roadmap
8 fases sequenciais; **índice, foco atual e status estão em [`docs/backlog/README.md`](docs/backlog/README.md)** — a fonte única (não duplicar aqui). Trilha em `docs/17_v1_roadmap.md`; cada fase vira tasks (template `docs/backlog/_task-template.md`) ao entrar nela.

## Disciplina (sempre)
- **Modos de falha / edge cases viram follow-up na hora** — ao escrever o caminho feliz, registrar o que acontece se falhar / for grande demais / chegar fora de ordem (na task **e** no README da fase). Nunca deixar uma falha sem rastro.
- **Ao concluir uma task:** varrer Notas/Fora-de-escopo por itens adiados → promover a **Follow-ups** (na task e no README da fase) ou confirmar "nenhum".
- **Sem arqueologia ao reestruturar docs:** escrever assumindo o **layout novo**; nada de "ex-", "saiu de", "mudança", "antes era".

## Convenções de código

### Python — docstrings (obrigatório)
- **Toda classe, função e método** (e módulos públicos) tem docstring no **estilo Google**, em **inglês**.
- Conteúdo: 1 linha de resumo + `Args:` + `Returns:` (+ `Raises:` quando aplicável; `Yields:` em generators).
- Documentar **entrada e saída** (significado de cada parâmetro e do retorno) e os **erros levantados**.
- **Type hints em tudo** (mypy strict). O docstring descreve significado/contrato, não repete o óbvio dos tipos.
- **Enforce:** Ruff pydocstyle (`D`, `convention = "google"`) — habilitado em `P0-CI-01`; o CI falha sem docstring.

Exemplo:

```python
def charge(order_id: str, amount: Money) -> Payment:
    """Charge an order through the payment gateway.

    Args:
        order_id: ID of the order to charge.
        amount: Amount (with currency) to charge.

    Returns:
        The created Payment, carrying the gateway status.

    Raises:
        PaymentError: If the gateway declines the charge.
    """
```

### Frontend (TypeScript)
- **TSDoc** em funções, componentes e hooks exportados (parâmetros + retorno), em inglês.

### Idioma
- **Docstrings, comentários e identificadores: inglês.**
- Documentação `.md` em `docs/`: **português** (como hoje).

## Outras convenções (resumo — detalhes nas Fundações)
- **Dados:** PK UUID · soft delete (nunca hard delete) · prefixo de tabela por domínio (`store_`, `catalog_`, `media_`, …) · dinheiro = `(valor em unidades menores + moeda ISO 4217)` · `store_id` (FK via `StoreScopedMixin`) em toda tabela/consulta comercial.
- **Módulo:** `app/modules/<nome>/` — `models.py` (só tabelas + `*Base`) · `schemas.py` (DTOs) · `enums.py` · `services.py`/`repositories.py`/`routes.py`/`permissions.py` (doc 04).
- **Infra/abstrações:** fila/worker (`arq`) via `app.core.queue.enqueue`; **todo e-mail é enfileirado no worker** (nunca inline — INV-F5); storage **S3 + CloudFront reais** desde o dev local (`app.core.storage`, região `us-east-2`).
- **Segurança:** **nunca commitar `.env` nem chaves AWS** (repo público) — `.env` é gitignored, `.env.example` versionado; em deploy, segredos via GitHub Secrets/SSM + IAM role.
- **Testes:** unit/integração/E2E pela regra do §10; serviço externo = mock (`moto`) no CI **+** smoke real env-gated.

Ver `docs/backlog/_foundations-and-bottlenecks.md`.
