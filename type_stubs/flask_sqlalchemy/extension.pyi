import typing as t

import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from _typeshed import Incomplete
from flask import Flask as Flask

from .model import BindMixin as BindMixin
from .model import DefaultMeta as DefaultMeta
from .model import DefaultMetaNoName as DefaultMetaNoName
from .model import Model as Model
from .model import NameMixin as NameMixin
from .pagination import Pagination as Pagination
from .pagination import SelectPagination as SelectPagination
from .query import Query as Query
from .session import Session as Session

class _FSAModel(Model):
    metadata: sa.MetaData

class SQLAlchemy:
    Query: Incomplete
    session: Incomplete
    metadatas: Incomplete
    Table: Incomplete
    Model: Incomplete
    def __init__(
        self,
        app: Flask | None = None,
        *,
        metadata: sa.MetaData | None = None,
        session_options: dict[str, t.Any] | None = None,
        query_class: type[Query] = ...,
        model_class: _FSA_MCT = ...,
        engine_options: dict[str, t.Any] | None = None,
        add_models_to_shell: bool = True,
        disable_autonaming: bool = False,
    ) -> None: ...
    def init_app(self, app: Flask) -> None: ...
    @property
    def metadata(self) -> sa.MetaData: ...
    @property
    def engines(self) -> t.Mapping[str | None, sa.engine.Engine]: ...
    @property
    def engine(self) -> sa.engine.Engine: ...
    def get_engine(
        self, bind_key: str | None = None, **kwargs: t.Any
    ) -> sa.engine.Engine: ...
    def get_or_404(
        self,
        entity: type[_O],
        ident: t.Any,
        *,
        description: str | None = None,
        **kwargs: t.Any,
    ) -> _O: ...
    def first_or_404(
        self, statement: sa.sql.Select[t.Any], *, description: str | None = None
    ) -> t.Any: ...
    def one_or_404(
        self, statement: sa.sql.Select[t.Any], *, description: str | None = None
    ) -> t.Any: ...
    def paginate(
        self,
        select: sa.sql.Select[t.Any],
        *,
        page: int | None = None,
        per_page: int | None = None,
        max_per_page: int | None = None,
        error_out: bool = True,
        count: bool = True,
    ) -> Pagination: ...
    def create_all(
        self, bind_key: str | None | list[str | None] = "__all__"
    ) -> None: ...
    def drop_all(self, bind_key: str | None | list[str | None] = "__all__") -> None: ...
    def reflect(self, bind_key: str | None | list[str | None] = "__all__") -> None: ...
    def relationship(
        self, *args: t.Any, **kwargs: t.Any
    ) -> sa_orm.RelationshipProperty[t.Any]: ...
    def dynamic_loader(
        self, argument: t.Any, **kwargs: t.Any
    ) -> sa_orm.RelationshipProperty[t.Any]: ...
    def __getattr__(self, name: str) -> t.Any: ...
