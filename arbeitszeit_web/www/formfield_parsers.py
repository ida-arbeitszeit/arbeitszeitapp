from copy import copy
from typing import Self
from uuid import UUID

from arbeitszeit_web.fields import ParsingFailure, ParsingSuccess
from arbeitszeit_web.translator import Translator


class UuidParser:
    def __init__(self, translator: Translator) -> None:
        self.translator = translator
        self._invalid_uuid_message: str | None = None

    def __call__(self, candidate: str) -> ParsingSuccess[UUID] | ParsingFailure:
        try:
            value = UUID(candidate.strip())
        except ValueError:
            message = self._invalid_uuid_message or self.translator.gettext(
                "Invalid UUID."
            )
            return ParsingFailure([message])
        return ParsingSuccess(value)

    def with_invalid_uuid_message(self, message: str) -> Self:
        new_parser = copy(self)
        new_parser._invalid_uuid_message = message
        return new_parser


class PositiveIntegerParser:
    def __init__(self, translator: Translator) -> None:
        self.translator = translator
        self._not_positive_message: str | None = None
        self._not_an_integer_message: str | None = None

    def __call__(self, value: str) -> ParsingSuccess[int] | ParsingFailure:
        try:
            amount = int(value.strip())
        except ValueError:
            return ParsingFailure(
                [
                    self._not_an_integer_message
                    or self.translator.gettext("This is not an integer.")
                ]
            )
        if amount <= 0:
            return ParsingFailure(
                [
                    self._not_positive_message
                    or self.translator.gettext("Must be a number larger than zero.")
                ]
            )
        return ParsingSuccess(amount)

    def with_not_positive_message(self, message: str) -> Self:
        new_parser = copy(self)
        new_parser._not_positive_message = message
        return new_parser

    def with_not_an_integer_message(self, message: str) -> Self:
        new_parser = copy(self)
        new_parser._not_an_integer_message = message
        return new_parser
