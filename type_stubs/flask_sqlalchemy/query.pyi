import typing as t

import sqlalchemy.orm as sa_orm

from .pagination import Pagination as Pagination
from .pagination import QueryPagination as QueryPagination

class Query(sa_orm.Query):
    def get_or_404(self, ident: t.Any, description: str | None = None) -> t.Any: ...
    def first_or_404(self, description: str | None = None) -> t.Any: ...
    def one_or_404(self, description: str | None = None) -> t.Any: ...
    def paginate(
        self,
        *,
        page: int | None = None,
        per_page: int | None = None,
        max_per_page: int | None = None,
        error_out: bool = True,
        count: bool = True,
    ) -> Pagination: ...
