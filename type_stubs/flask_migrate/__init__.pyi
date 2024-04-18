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
    def __init__(
        self,
        app: Incomplete | None = None,
        db: Incomplete | None = None,
        directory: str = "migrations",
        command: str = "db",
        compare_type: bool = True,
        render_as_batch: bool = True,
        **kwargs,
    ) -> None: ...
    def init_app(
        self,
        app,
        db: Incomplete | None = None,
        directory: Incomplete | None = None,
        command: Incomplete | None = None,
        compare_type: Incomplete | None = None,
        render_as_batch: Incomplete | None = None,
        **kwargs,
    ) -> None: ...
    def configure(self, f): ...
    def call_configure_callbacks(self, config): ...
    def get_config(
        self,
        directory: Incomplete | None = None,
        x_arg: Incomplete | None = None,
        opts: Incomplete | None = None,
    ): ...

def catch_errors(f): ...
def list_templates() -> None: ...
def init(
    directory: Incomplete | None = None,
    multidb: bool = False,
    template: Incomplete | None = None,
    package: bool = False,
) -> None: ...
def revision(
    directory: Incomplete | None = None,
    message: Incomplete | None = None,
    autogenerate: bool = False,
    sql: bool = False,
    head: str = "head",
    splice: bool = False,
    branch_label: Incomplete | None = None,
    version_path: Incomplete | None = None,
    rev_id: Incomplete | None = None,
) -> None: ...
def migrate(
    directory: Incomplete | None = None,
    message: Incomplete | None = None,
    sql: bool = False,
    head: str = "head",
    splice: bool = False,
    branch_label: Incomplete | None = None,
    version_path: Incomplete | None = None,
    rev_id: Incomplete | None = None,
    x_arg: Incomplete | None = None,
) -> None: ...
def edit(directory: Incomplete | None = None, revision: str = "current") -> None: ...
def merge(
    directory: Incomplete | None = None,
    revisions: str = "",
    message: Incomplete | None = None,
    branch_label: Incomplete | None = None,
    rev_id: Incomplete | None = None,
) -> None: ...
def upgrade(
    directory: Incomplete | None = None,
    revision: str = "head",
    sql: bool = False,
    tag: Incomplete | None = None,
    x_arg: Incomplete | None = None,
) -> None: ...
def downgrade(
    directory: Incomplete | None = None,
    revision: str = "-1",
    sql: bool = False,
    tag: Incomplete | None = None,
    x_arg: Incomplete | None = None,
) -> None: ...
def show(directory: Incomplete | None = None, revision: str = "head") -> None: ...
def history(
    directory: Incomplete | None = None,
    rev_range: Incomplete | None = None,
    verbose: bool = False,
    indicate_current: bool = False,
) -> None: ...
def heads(
    directory: Incomplete | None = None,
    verbose: bool = False,
    resolve_dependencies: bool = False,
) -> None: ...
def branches(directory: Incomplete | None = None, verbose: bool = False) -> None: ...
def current(directory: Incomplete | None = None, verbose: bool = False) -> None: ...
def stamp(
    directory: Incomplete | None = None,
    revision: str = "head",
    sql: bool = False,
    tag: Incomplete | None = None,
    purge: bool = False,
) -> None: ...
def check(directory: Incomplete | None = None) -> None: ...
