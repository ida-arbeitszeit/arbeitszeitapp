from arbeitszeit.injector import AliasProvider, Binder, Module
from arbeitszeit_web.session import Session
from tests.session import FakeSession


class ApiModule(Module):
    def configure(self, binder: Binder) -> None:
        super().configure(binder)
        binder[Session] = AliasProvider(FakeSession)
