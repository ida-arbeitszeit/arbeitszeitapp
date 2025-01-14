from __future__ import annotations

from dataclasses import dataclass
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
