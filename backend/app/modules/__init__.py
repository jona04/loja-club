"""Domain modules (modular monolith).

One package per domain. Each module uses the 7-file convention as needed
(``models``, ``schemas``, ``routes``, ``services``, ``repositories``,
``permissions``, ``exceptions``). Every table sets an explicit ``__tablename__``
with a domain prefix (e.g. ``account_users``, ``catalog_products``).
"""
