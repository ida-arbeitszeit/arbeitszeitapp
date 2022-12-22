from injector import Injector, Module, inject


class ApiModule(Module):
    ...


def get_dependency_injector() -> Injector:
    return Injector(modules=[ApiModule()])


def injection_test(original_test):
    injector = get_dependency_injector()

    def wrapper(*args, **kwargs):
        return injector.call_with_injection(
            inject(original_test), args=args, kwargs=kwargs
        )

    return wrapper
