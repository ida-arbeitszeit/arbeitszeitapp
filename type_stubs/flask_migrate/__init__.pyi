from _typeshed import Incomplete
from alembic.config import Config as AlembicConfig

alembic_version: Incomplete
log: Incomplete

class _MigrateConfig:
    migrate: Incomplete
    db: Incomplete
    directory: Incomplete
    configure_args: Incomplete
    def __init__(self, migrate, db, **kwargs) -> None: ...
    @property
    def metadata(self): ...

class Config(AlembicConfig):
    template_directory: Incomplete
    def __init__(self, *args, **kwargs) -> None: ...
    def get_template_directory(self): ...

class Migrate:
    configure_callbacks: Incomplete
    db: Incomplete
    command: Incomplete
    directory: Incomplete
    alembic_ctx_kwargs: Incomplete
    def __init__(self, app: Incomplete | None = ..., db: Incomplete | None = ..., directory: str = ..., command: str = ..., compare_type: bool = ..., render_as_batch: bool = ..., **kwargs) -> None: ...
    def init_app(self, app, db: Incomplete | None = ..., directory: Incomplete | None = ..., command: Incomplete | None = ..., compare_type: Incomplete | None = ..., render_as_batch: Incomplete | None = ..., **kwargs) -> None: ...
    def configure(self, f): ...
    def call_configure_callbacks(self, config): ...
    def get_config(self, directory: Incomplete | None = ..., x_arg: Incomplete | None = ..., opts: Incomplete | None = ...): ...

def catch_errors(f): ...
def list_templates() -> None: ...
def init(directory: Incomplete | None = ..., multidb: bool = ..., template: Incomplete | None = ..., package: bool = ...) -> None: ...
def revision(directory: Incomplete | None = ..., message: Incomplete | None = ..., autogenerate: bool = ..., sql: bool = ..., head: str = ..., splice: bool = ..., branch_label: Incomplete | None = ..., version_path: Incomplete | None = ..., rev_id: Incomplete | None = ...) -> None: ...
def migrate(directory: Incomplete | None = ..., message: Incomplete | None = ..., sql: bool = ..., head: str = ..., splice: bool = ..., branch_label: Incomplete | None = ..., version_path: Incomplete | None = ..., rev_id: Incomplete | None = ..., x_arg: Incomplete | None = ...) -> None: ...
def edit(directory: Incomplete | None = ..., revision: str = ...) -> None: ...
def merge(directory: Incomplete | None = ..., revisions: str = ..., message: Incomplete | None = ..., branch_label: Incomplete | None = ..., rev_id: Incomplete | None = ...) -> None: ...
def upgrade(directory: Incomplete | None = ..., revision: str = ..., sql: bool = ..., tag: Incomplete | None = ..., x_arg: Incomplete | None = ...) -> None: ...
def downgrade(directory: Incomplete | None = ..., revision: str = ..., sql: bool = ..., tag: Incomplete | None = ..., x_arg: Incomplete | None = ...) -> None: ...
def show(directory: Incomplete | None = ..., revision: str = ...) -> None: ...
def history(directory: Incomplete | None = ..., rev_range: Incomplete | None = ..., verbose: bool = ..., indicate_current: bool = ...) -> None: ...
def heads(directory: Incomplete | None = ..., verbose: bool = ..., resolve_dependencies: bool = ...) -> None: ...
def branches(directory: Incomplete | None = ..., verbose: bool = ...) -> None: ...
def current(directory: Incomplete | None = ..., verbose: bool = ...) -> None: ...
def stamp(directory: Incomplete | None = ..., revision: str = ..., sql: bool = ..., tag: Incomplete | None = ...) -> None: ...
def check(directory: Incomplete | None = ...) -> None: ...