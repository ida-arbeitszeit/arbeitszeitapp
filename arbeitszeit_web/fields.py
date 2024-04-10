from dataclasses import dataclass
from typing import Generic, Optional, Protocol, TypeVar

T = TypeVar("T")


class FormField(Protocol[T]):
    def get_value(self) -> T: ...

    def attach_error(self, message: str) -> None: ...

    def set_value(self, value: T) -> None: ...


@dataclass
class ParsingSuccess(Generic[T]):
    value: T


@dataclass
class ParsingFailure:
    errors: list[str]


class FieldParser(Protocol[T]):
    def __call__(self, value: str, /) -> ParsingSuccess[T] | ParsingFailure: ...


def parse_formfield(
    field: FormField[str], parser: FieldParser[T]
) -> Optional[ParsingSuccess[T]]:
    match parser(field.get_value()):
        case ParsingFailure(errors):
            for error in errors:
                field.attach_error(error)
        case ParsingSuccess() as result:
            return result
    return None
