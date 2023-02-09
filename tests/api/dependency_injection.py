from arbeitszeit.injector import Injector, Module


class ApiModule(Module):
    ...


def get_dependency_injector() -> Injector:
    return Injector(modules=[ApiModule()])
