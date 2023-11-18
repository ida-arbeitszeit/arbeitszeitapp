from arbeitszeit.injector import Injector
from tests.dependency_injection import TestingModule
from tests.use_cases.dependency_injection import InMemoryModule

def get_dependency_injector() -> Injector:
    return Injector([TestingModule(), InMemoryModule()])

injector = get_dependency_injector()