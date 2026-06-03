# Loja Club — instruções do projeto

SaaS de ecommerce multi-tenant. Documentação conceitual em `docs/01..24`; **backlog acionável** em `docs/backlog/`; **invariantes e decisões** em `docs/backlog/_foundations-and-bottlenecks.md`.

## Regra de ouro
O código imita a lógica dos docs — **não inventar lógica de negócio nova**. Se uma limitação técnica impedir seguir o doc, atualizar o `.md` para refletir o código; **nunca** deixar doc e código divergentes.

## Git (importante)
**Nunca** executar operações de git que alterem estado: sem `commit`, `push`, `branch`, `checkout`/`switch`, `merge`, `reset`, `rebase`, `stash`. **O usuário gerencia o git.** Implementar **sempre na branch atual** (a que estiver checada) — não criar nem trocar de branch. Rodar git (mesmo só-leitura, como `git status`/`git diff`) **apenas se o usuário pedir**.

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
PK UUID · soft delete · prefixo de tabela por domínio · dinheiro = `(valor em unidades menores + moeda ISO 4217)` · `store_id` em toda query comercial · testes unit/integração/E2E pela regra do §10. Ver `docs/backlog/_foundations-and-bottlenecks.md`.
