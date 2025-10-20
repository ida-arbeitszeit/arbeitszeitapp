import os

from arbeitszeit.injector import (
    AliasProvider,
    Binder,
    CallableProvider,
    Module,
)
from arbeitszeit.records import SocialAccounting
from arbeitszeit.repositories import DatabaseGateway
from arbeitszeit_db import get_social_accounting
from arbeitszeit_db.db import Database
from arbeitszeit_db.repositories import DatabaseGatewayImpl


def provide_test_database_uri() -> str:
    return os.environ["ARBEITSZEITAPP_TEST_DB"]


def provide_database() -> Database:
    Database().configure(uri=provide_test_database_uri())
    return Database()


class DatabaseModule(Module):
    def configure(self, binder: Binder) -> None:
        super().configure(binder)
        binder[Database] = CallableProvider(provide_database, is_singleton=True)
        binder[DatabaseGateway] = AliasProvider(DatabaseGatewayImpl)
        binder[SocialAccounting] = CallableProvider(get_social_accounting)
