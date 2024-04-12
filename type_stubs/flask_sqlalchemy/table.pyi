import typing as t

import sqlalchemy as sa
import sqlalchemy.sql.schema as sa_sql_schema

class _Table(sa.Table):
    @t.overload
    def __init__(
        self,
        name: str,
        *args: sa_sql_schema.SchemaItem,
        bind_key: str | None = None,
        **kwargs: t.Any,
    ) -> None: ...
    @t.overload
    def __init__(
        self,
        name: str,
        metadata: sa.MetaData,
        *args: sa_sql_schema.SchemaItem,
        **kwargs: t.Any,
    ) -> None: ...
    @t.overload
    def __init__(
        self, name: str, *args: sa_sql_schema.SchemaItem, **kwargs: t.Any
    ) -> None: ...
