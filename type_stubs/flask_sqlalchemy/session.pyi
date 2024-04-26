import typing as t

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from .extension import SQLAlchemy as SQLAlchemy

class Session(sa_orm.Session):
    def __init__(self, db: SQLAlchemy, **kwargs: t.Any) -> None: ...
    def get_bind(
        self,
        mapper: t.Any | None = None,
        clause: t.Any | None = None,
        bind: sa.engine.Engine | sa.engine.Connection | None = None,
        **kwargs: t.Any,
    ) -> sa.engine.Engine | sa.engine.Connection: ...
