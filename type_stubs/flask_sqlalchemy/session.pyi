import sqlalchemy as sa
import typing as t
from .extension import SQLAlchemy as SQLAlchemy

class Session(sa.orm.Session):
    def __init__(self, db: SQLAlchemy, **kwargs: t.Any) -> None: ...
    def get_bind(self, mapper: t.Any | None = ..., clause: t.Any | None = ..., bind: sa.engine.Engine | sa.engine.Connection | None = ..., **kwargs: t.Any) -> sa.engine.Engine | sa.engine.Connection: ...
