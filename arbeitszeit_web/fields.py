from typing import Protocol, TypeVar

T = TypeVar("T")


class FormField(Protocol[T]):
    def get_value(self) -> T:
        ...

    def attach_error(self, message: str) -> None:
        ...

    def set_default_value(self, value: T) -> None:
        ...
