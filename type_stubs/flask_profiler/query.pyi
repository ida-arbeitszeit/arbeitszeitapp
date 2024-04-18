import enum
from dataclasses import dataclass
from typing import Any, List, Protocol, Tuple

from _typeshed import Incomplete

class Expression(Protocol):
    def as_expression(self) -> str: ...

class FromClause(Protocol):
    def as_from_clause(self) -> str: ...

class SelectorClause(Protocol):
    def as_selector_clause(self) -> str: ...

class Query(Protocol):
    def as_query(self) -> str: ...

class Vector(Protocol):
    def as_vector(self) -> str: ...

class Selector(Protocol):
    def as_selector(self) -> str: ...

class Statement(Protocol):
    def as_statement(self) -> str: ...

class PragmaValue(Protocol):
    def as_pragma_value(self) -> str: ...

class ColumnConstraint(Protocol):
    def as_column_constraint(self) -> str: ...

class JoinConstraint(Protocol):
    def as_join_constraint(self) -> str: ...

class Ordering(Expression, Protocol):
    def is_ascending(self) -> bool: ...

@dataclass
class Select:
    selector: SelectorClause
    from_clause: FromClause
    where_clause: Expression | None = ...
    group_by: Expression | None = ...
    order_by: List[Ordering] = ...
    limit_clause: int = ...
    offset_clause: int = ...
    def as_query(self) -> str: ...
    def as_vector(self) -> str: ...
    def and_where(self, expression: Expression) -> Select: ...
    def as_statement(self) -> str: ...
    def as_expression(self) -> str: ...
    def as_from_clause(self) -> str: ...
    def __init__(
        self,
        selector,
        from_clause,
        where_clause,
        group_by,
        order_by,
        limit_clause,
        offset_clause,
    ) -> None: ...

@dataclass(frozen=True)
class Insert:
    into: Identifier
    rows: List[List[Expression]]
    columns: List[Identifier] | None = ...
    alias: Identifier | None = ...
    returning: All | None = ...
    def as_statement(self) -> str: ...
    def __init__(self, into, rows, columns, alias, returning) -> None: ...

@dataclass
class Pragma:
    name: str
    schema: str | None = ...
    value: PragmaValue | None = ...
    def as_statement(self) -> str: ...
    def __init__(self, name, schema, value) -> None: ...

@dataclass
class CreateTable:
    name: Identifier
    columns: List[ColumnDefinition]
    if_not_exists: bool = ...
    def as_statement(self) -> str: ...
    def __init__(self, name, columns, if_not_exists) -> None: ...

@dataclass
class CreateIndex:
    name: Identifier
    on: Identifier
    indices: List[IndexDefinition]
    if_not_exists: bool = ...
    def as_statement(self) -> str: ...
    def __init__(self, name, on, indices, if_not_exists) -> None: ...

@dataclass
class Delete:
    table: Identifier
    where: Expression | None = ...
    def as_statement(self) -> str: ...
    def __init__(self, table, where) -> None: ...

@dataclass
class IndexDefinition:
    column: Expression
    descending: bool = ...
    def __init__(self, column, descending) -> None: ...

@dataclass
class ColumnDefinition:
    name: Identifier
    column_type: ColumnType
    constraints: List[ColumnConstraint] | None = ...
    def __init__(self, name, column_type, constraints) -> None: ...

class ColumnType(enum.Enum):
    NULL: str
    INTEGER: str
    REAL: str
    TEXT: str
    BLOB: str
    def as_type_def(self) -> str: ...

@dataclass
class PrimaryKey:
    autoincrement: bool = ...
    def as_column_constraint(self) -> str: ...
    def __init__(self, autoincrement) -> None: ...

@dataclass
class Function:
    name: str
    operands: List[Expression] = ...
    def as_expression(self) -> str: ...
    def __init__(self, name, operands) -> None: ...

@dataclass
class BinaryOp:
    operator: str
    x: Expression
    y: Expression
    def as_expression(self) -> str: ...
    def as_selector(self) -> str: ...
    def __init__(self, operator, x, y) -> None: ...

@dataclass
class Literal:
    value: Any
    def as_expression(self) -> str: ...
    def as_selector(self) -> str: ...
    def as_pragma_value(self) -> str: ...
    def __init__(self, value) -> None: ...

@dataclass
class Identifier:
    names: str | List[str]
    def as_expression(self) -> str: ...
    def as_from_clause(self) -> str: ...
    def as_selector(self) -> str: ...
    @staticmethod
    def escape(value: str) -> str: ...
    def __init__(self, names) -> None: ...

@dataclass
class ExpressionList:
    expressions: List[Expression]
    def as_expression(self) -> str: ...
    def __init__(self, expressions) -> None: ...

class Null:
    def as_expression(self) -> str: ...
    def as_pragma_value(self) -> str: ...

null: Incomplete

@dataclass
class Alias:
    expression: Expression
    name: Identifier
    def as_from_clause(self) -> str: ...
    def as_selector(self) -> str: ...
    def as_selector_clause(self) -> str: ...
    def __init__(self, expression, name) -> None: ...

@dataclass
class SelectorList:
    selectors: List[Selector]
    def as_selector_clause(self) -> str: ...
    def __init__(self, selectors) -> None: ...

class All:
    def as_selector(self) -> str: ...
    def as_selector_clause(self) -> str: ...

@dataclass
class Aggregate:
    name: str
    expression: Expression | All
    is_distinct: bool = ...
    def as_selector(self) -> str: ...
    def as_expression(self) -> str: ...
    def __init__(self, name, expression, is_distinct) -> None: ...

@dataclass
class JoinSpec:
    operator: str
    table: Identifier
    constraint: JoinConstraint
    def __init__(self, operator, table, constraint) -> None: ...

def left(table: Identifier, constraint: JoinConstraint) -> JoinSpec: ...
def inner(table: Identifier, constraint: JoinConstraint) -> JoinSpec: ...
def right(table: Identifier, constraint: JoinConstraint) -> JoinSpec: ...
@dataclass
class On:
    expression: Expression
    def as_join_constraint(self) -> str: ...
    def __init__(self, expression) -> None: ...

@dataclass
class Join:
    table: Identifier
    spec: List[JoinSpec]
    def as_from_clause(self) -> str: ...
    def __init__(self, table, spec) -> None: ...

@dataclass
class If:
    condition: Expression
    consequence: Expression
    alternative: Expression
    def as_expression(self) -> str: ...
    def __init__(self, condition, consequence, alternative) -> None: ...

@dataclass
class Case:
    cases: List[Tuple[Expression, Expression]]
    alternative: Expression | None = ...
    def as_expression(self) -> str: ...
    def __init__(self, cases, alternative) -> None: ...

@dataclass
class Asc:
    expression: Expression
    def as_expression(self) -> str: ...
    def is_ascending(self) -> bool: ...
    def __init__(self, expression) -> None: ...

@dataclass
class Desc:
    expression: Expression
    def as_expression(self) -> str: ...
    def is_ascending(self) -> bool: ...
    def __init__(self, expression) -> None: ...
