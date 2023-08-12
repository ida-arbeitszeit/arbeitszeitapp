import sqlalchemy as sa
import typing as t
from .extension import SQLAlchemy as SQLAlchemy
from .query import Query as Query

class _QueryProperty:
    @t.overload
    def __get__(self, obj: None, cls: type[Model]) -> Query: ...
    @t.overload
    def __get__(self, obj: Model, cls: type[Model]) -> Query: ...

class Model:
    __fsa__: t.ClassVar[SQLAlchemy]
    query_class: t.ClassVar[type[Query]]
    query: t.ClassVar[Query]

class BindMetaMixin(type):
    __fsa__: SQLAlchemy
    metadata: sa.MetaData
    def __init__(cls, name: str, bases: tuple[type, ...], d: dict[str, t.Any], **kwargs: t.Any) -> None: ...

class NameMetaMixin(type):
    metadata: sa.MetaData
    __tablename__: str
    __table__: sa.Table
    def __init__(cls, name: str, bases: tuple[type, ...], d: dict[str, t.Any], **kwargs: t.Any) -> None: ...
    def __table_cls__(cls, *args: t.Any, **kwargs: t.Any) -> sa.Table | None: ...

def should_set_tablename(cls) -> bool: ...
def camel_to_snake_case(name: str) -> str: ...

class DefaultMeta(BindMetaMixin, NameMetaMixin, sa.orm.DeclarativeMeta): ...
