from arbeitszeit.injector import AliasProvider, Binder, Injector, Module
from arbeitszeit_web.session import Session
from tests.dependency_injection import TestingModule
from tests.session import FakeSession
from tests.use_cases.dependency_injection import InMemoryModule


class ControllerTestsModule(Module):
    def configure(self, binder: Binder) -> None:
        super().configure(binder)
        binder[Session] = AliasProvider(FakeSession)  # type: ignore


def get_dependency_injector() -> Injector:
    return Injector([TestingModule(), InMemoryModule(), ControllerTestsModule()])
