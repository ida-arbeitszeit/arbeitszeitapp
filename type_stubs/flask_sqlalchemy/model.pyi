import typing as t

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm

from .extension import SQLAlchemy as SQLAlchemy
from .query import Query as Query

class _QueryProperty:
    def __get__(self, obj: Model | None, cls: type[Model]) -> Query: ...

class Model:
    __fsa__: t.ClassVar[SQLAlchemy]
    query_class: t.ClassVar[type[Query]]
    query: t.ClassVar[Query]

class BindMetaMixin(type):
    __fsa__: SQLAlchemy
    metadata: sa.MetaData
    def __init__(
        cls, name: str, bases: tuple[type, ...], d: dict[str, t.Any], **kwargs: t.Any
    ) -> None: ...

class BindMixin:
    __fsa__: SQLAlchemy
    metadata: sa.MetaData
    @classmethod
    def __init_subclass__(cls, **kwargs: t.Dict[str, t.Any]) -> None: ...

class NameMetaMixin(type):
    metadata: sa.MetaData
    __tablename__: str
    __table__: sa.Table
    def __init__(
        cls, name: str, bases: tuple[type, ...], d: dict[str, t.Any], **kwargs: t.Any
    ) -> None: ...
    def __table_cls__(cls, *args: t.Any, **kwargs: t.Any) -> sa.Table | None: ...

class NameMixin:
    metadata: sa.MetaData
    __tablename__: str
    __table__: sa.Table
    @classmethod
    def __init_subclass__(cls, **kwargs: t.Dict[str, t.Any]) -> None: ...
    @classmethod
    def __table_cls__(cls, *args: t.Any, **kwargs: t.Any) -> sa.Table | None: ...

def should_set_tablename(cls) -> bool: ...
def camel_to_snake_case(name: str) -> str: ...

class DefaultMeta(BindMetaMixin, NameMetaMixin, sa_orm.DeclarativeMeta): ...
class DefaultMetaNoName(BindMetaMixin, sa_orm.DeclarativeMeta): ...
