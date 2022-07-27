from typing import Protocol, TypeVar

T = TypeVar("T", covariant=True)


class FormField(Protocol[T]):
    def get_value(self) -> T:
        ...

    def attach_error(self, message: str) -> None:
        ...
