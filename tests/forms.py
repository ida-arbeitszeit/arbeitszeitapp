from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Generic, List, Optional, Self, TypeVar

T = TypeVar("T")


class LoginForm:
    def __init__(
        self,
        *,
        remember_value: bool = False,
        email_value: str = "test@email.ad",
        password_value: str = "testpassword",
    ) -> None:
        self._email_field = FormFieldImpl(value=email_value)
        self._remember_field = FormFieldImpl(value=remember_value)
        self._password_field = FormFieldImpl(value=password_value)

    def email_field(self) -> FormFieldImpl[str]:
        return self._email_field

    def password_field(self) -> FormFieldImpl[str]:
        return self._password_field

    def remember_field(self) -> FormFieldImpl[bool]:
        return self._remember_field

    def has_errors(self) -> bool:
        return bool(
            self._email_field.errors
            or self._password_field.errors
            or self._remember_field.errors
        )


class DraftForm:
    def __init__(
        self,
        prd_name: str = "product name",
        description: str = "product description",
        timeframe: int = 1,
        prd_unit: str = "unit",
        prd_amount: int = 1,
        costs_p: Decimal = Decimal("1"),
        costs_r: Decimal = Decimal("1"),
        costs_a: Decimal = Decimal("1"),
        is_public_service: bool = False,
    ) -> None:
        self._product_name_field = FormFieldImpl(value=prd_name)
        self._description_field = FormFieldImpl(value=description)
        self._timeframe_field = FormFieldImpl(value=timeframe)
        self._unit_of_distribution_field = FormFieldImpl(value=prd_unit)
        self._amount_field = FormFieldImpl(value=prd_amount)
        self._means_cost_field = FormFieldImpl(value=costs_p)
        self._resource_cost_field = FormFieldImpl(value=costs_r)
        self._labour_cost_field = FormFieldImpl(value=costs_a)
        self._is_public_service_field = FormFieldImpl(value=is_public_service)

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


class RegisterProductiveConsumptionFakeForm:
    def __init__(self, amount: str, plan_id: str, type_of_consumption: str) -> None:
        self._amount_field = FormFieldImpl(value=amount)
        self._plan_id_field = FormFieldImpl(value=plan_id)
        self._type_of_consumption_field = FormFieldImpl(value=type_of_consumption)

    def amount_field(self) -> FormFieldImpl[str]:
        return self._amount_field

    def plan_id_field(self) -> FormFieldImpl[str]:
        return self._plan_id_field

    def type_of_consumption_field(self) -> FormFieldImpl[str]:
        return self._type_of_consumption_field


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


@dataclass
class RegisterFormImpl:
    email_field: FormFieldImpl[str]
    password_field: FormFieldImpl[str]
    name_field: FormFieldImpl[str]

    @classmethod
    def create(
        cls,
        email: str = "test@test.test",
        password: str = "testpassword",
        name: str = "testname",
    ) -> RegisterFormImpl:
        return cls(
            email_field=FormFieldImpl(value=email),
            password_field=FormFieldImpl(value=password),
            name_field=FormFieldImpl(value=name),
        )

    def errors(self) -> List[str]:
        """Contains all errors of all fields of the form"""
        return (
            self.email_field.errors
            + self.password_field.errors
            + self.name_field.errors
        )


@dataclass
class RequestEmailAddressChangeFormImpl:
    new_email_field: FormFieldImpl[str]
    current_password_field: FormFieldImpl[str]

    @classmethod
    def from_values(cls, new_email_address: str, current_password: str) -> Self:
        return cls(
            new_email_field=FormFieldImpl(value=new_email_address),
            current_password_field=FormFieldImpl(value=current_password),
        )


class RequestCoordinationTransferFormImpl:
    def __init__(self, candidate: str, cooperation: str) -> None:
        self._candidate_field = FormFieldImpl(value=candidate)
        self._cooperation_field = FormFieldImpl(value=cooperation)

    def candidate_field(self) -> FormFieldImpl[str]:
        return self._candidate_field

    def cooperation_field(self) -> FormFieldImpl[str]:
        return self._cooperation_field


class ConfirmEmailAddressChangeFormImpl:
    def __init__(self, is_accepted: bool) -> None:
        self._is_accepted_field = FormFieldImpl(value=is_accepted)

    def is_accepted_field(self) -> FormFieldImpl[bool]:
        return self._is_accepted_field
