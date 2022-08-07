from __future__ import annotations

from typing import Generic, List, TypeVar
from uuid import uuid4

T = TypeVar("T")


class PayConsumerProductFakeForm:
    def __init__(self) -> None:
        self._amount: str = "1"
        self._plan_id: str = str(uuid4())
        self.amount_errors: List[str] = []
        self.plan_id_errors: List[str] = []

    def amount_field(self) -> FormFieldImpl[str]:
        return FormFieldImpl(value=self._amount, errors=self.amount_errors)

    def plan_id_field(self) -> FormFieldImpl[str]:
        return FormFieldImpl(value=self._plan_id, errors=self.plan_id_errors)

    def has_errors(self) -> bool:
        return bool(self.amount_errors or self.plan_id_errors)

    def set_amount(self, amount: str):
        self._amount = amount

    def set_plan_id(self, plan_id: str):
        self._plan_id = plan_id


class FormFieldImpl(Generic[T]):
    def __init__(self, value: T, errors: List[str]) -> None:
        self.errors = errors
        self.value = value

    def get_value(self) -> T:
        return self.value

    def attach_error(self, message: str) -> None:
        self.errors.append(message)

    def set_default_value(self, value: T) -> None:
        self.value = value
