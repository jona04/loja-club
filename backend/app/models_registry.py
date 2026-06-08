"""Central import of all SQLModel models so the metadata is fully populated.

Importing this module registers every table on ``SQLModel.metadata`` (used by
Alembic autogenerate, ``init_db`` and the test harness). Domain module models are
imported here as they are created.
"""

from sqlmodel import SQLModel

import app.models  # noqa: F401
import app.modules.accounts.models  # noqa: F401
import app.modules.domains.models  # noqa: F401
import app.modules.stores.models  # noqa: F401

__all__ = ["SQLModel"]
