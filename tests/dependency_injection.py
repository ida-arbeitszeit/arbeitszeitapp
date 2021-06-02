from injector import Binder, ClassProvider, Injector, inject

import arbeitszeit.repositories as interfaces
from tests import repositories


def configure_injector(binder: Binder) -> None:
    binder.bind(
        interfaces.PurchaseRepository, ClassProvider(repositories.PurchaseRepository)
    )


injector = Injector(configure_injector)


def injection_test(original_test):
    def wrapper(*args, **kwargs):
        return injector.call_with_injection(
            inject(original_test), args=args, kwargs=kwargs
        )

    return wrapper
