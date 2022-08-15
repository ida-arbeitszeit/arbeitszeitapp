from __future__ import annotations

from decimal import Decimal
from typing import Generic, List, Optional, TypeVar

T = TypeVar("T")


class LoginForm:
    def __init__(self) -> None:
        self.email_errors: List[str] = []
        self.password_errors: List[str] = []
        self._is_remember: bool = False

    def email_field(self) -> FormFieldImpl[str]:
        return FormFieldImpl(value="test value", errors=self.email_errors)

    def password_field(self) -> FormFieldImpl[str]:
        return FormFieldImpl(value="test password", errors=self.password_errors)

    def remember_field(self) -> FormFieldImpl[bool]:
        return FormFieldImpl(value=self._is_remember, errors=[])

    def has_errors(self) -> bool:
        return bool(self.email_errors or self.password_errors)

    def set_remember_field(self, state: bool) -> None:
        self._is_remember = state


class DraftForm:
    def __init__(
        self,
        prd_name: str,
        description: str,
        timeframe: int,
        prd_unit: str,
        prd_amount: int,
        costs_p: Decimal,
        costs_r: Decimal,
        costs_a: Decimal,
        productive_or_public: str,
    ) -> None:
        self._product_name_field = FormFieldImpl(value=prd_name)
        self._description_field = FormFieldImpl(value=description)
        self._timeframe_field = FormFieldImpl(value=timeframe)
        self._unit_of_distribution_field = FormFieldImpl(value=prd_unit)
        self._amount_field = FormFieldImpl(value=prd_amount)
        self._means_cost_field = FormFieldImpl(value=costs_p)
        self._resource_cost_field = FormFieldImpl(value=costs_r)
        self._labour_cost_field = FormFieldImpl(value=costs_a)
        if productive_or_public == "public":
            self._is_public_service_field = FormFieldImpl(value=True)
        elif productive_or_public == "productive":
            self._is_public_service_field = FormFieldImpl(value=True)
        else:
            raise ValueError("{productive_or_public=} must be 'productive' or 'public'")

    def product_name_field(self) -> FormFieldImpl[str]:
        return self._product_name_field

    def description_field(self) -> FormFieldImpl[str]:
        return self._description_field

    def timeframe_field(self) -> FormFieldImpl[int]:
        return self._timeframe_field

    def unit_of_distribution_field(self) -> FormFieldImpl[str]:
        return self._unit_of_distribution_field

    def amount_field(self) -> FormFieldImpl[int]:
        return self._amount_field

    def means_cost_field(self) -> FormFieldImpl[Decimal]:
        return self._means_cost_field

    def resource_cost_field(self) -> FormFieldImpl[Decimal]:
        return self._resource_cost_field

    def labour_cost_field(self) -> FormFieldImpl[Decimal]:
        return self._labour_cost_field

    def is_public_service_field(self) -> FormFieldImpl[bool]:
        return self._is_public_service_field


class FormFieldImpl(Generic[T]):
    def __init__(self, value: T, errors: Optional[List[str]] = None) -> None:
        if errors is None:
            self.errors = []
        else:
            self.errors = errors
        self.value = value

    def get_value(self) -> T:
        return self.value

    def attach_error(self, message: str) -> None:
        self.errors.append(message)

    def set_value(self, value: T) -> None:
        self.value = value
