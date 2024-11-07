from dataclasses import dataclass
from typing import TypeAlias, TypeVar
from uuid import UUID

from arbeitszeit_web.translator import Translator

T = TypeVar("T")
ValidatorResult: TypeAlias = T | list[str]


@dataclass
class RegisterPrivateConsumptionFormValidator:
    translator: Translator

    def validate_plan_id_string(self, text: str) -> ValidatorResult[UUID]:
        if text:
            try:
                return UUID(text)
            except ValueError:
                return [self.translator.gettext("Plan ID is invalid.")]
        else:
            return [self.translator.gettext("Plan ID is invalid.")]

    def validate_amount_string(self, text: str) -> ValidatorResult[int]:
        if text:
            try:
                amount = int(text)
            except ValueError:
                return [self.translator.gettext("This is not an integer.")]
        else:
            return [self.translator.gettext("You must specify an amount.")]
        if amount is not None and amount < 1:
            return [self.translator.gettext("Must be a number larger than zero.")]
        return amount
