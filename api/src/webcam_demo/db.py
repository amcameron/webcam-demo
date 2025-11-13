"""database management for webcam demo backend"""

from sqlalchemy.dialects.sqlite import insert as _insert
from sqlmodel import create_engine

_SQLITE_DB_FILENAME = "webcam_demo.db"
_SQL_URL = f"sqlite:///{_SQLITE_DB_FILENAME}"
engine = create_engine(_SQL_URL, echo=True)

# Without doing this insert -> _insert -> insert trick, it would look like an unused import.
# This makes clear that we mean to export this name from this module.
insert = _insert
