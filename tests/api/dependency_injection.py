from injector import Injector, Module, inject, provider

from arbeitszeit_web.api_presenters.fields import Fields
from arbeitszeit_web.api_presenters.namespace import Namespace
from tests.api.fields import (
    BooleanFieldImpl,
    DateTimeFieldImpl,
    DecimalFieldImpl,
    NestedListFieldImpl,
    StringFieldImpl,
)
from tests.api.namespace import NamespaceImpl


class ApiModule(Module):
    @provider
    def provide_namespace(self) -> Namespace:
        return NamespaceImpl()

    @provider
    def provide_fields(self) -> Fields:
        return Fields(
            nested_list_field=NestedListFieldImpl,
            string_field=StringFieldImpl,
            datetime_field=DateTimeFieldImpl,
            decimal_field=DecimalFieldImpl,
            boolean_field=BooleanFieldImpl,
        )


def get_dependency_injector() -> Injector:
    return Injector(modules=[ApiModule()])


def injection_test(original_test):
    injector = get_dependency_injector()

    def wrapper(*args, **kwargs):
        return injector.call_with_injection(
            inject(original_test), args=args, kwargs=kwargs
        )

    return wrapper
