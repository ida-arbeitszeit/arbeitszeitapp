from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Optional, TypeAlias, TypeVar, Union

from arbeitszeit_web.forms import DraftForm
from arbeitszeit_web.request import Request as WebRequest
from arbeitszeit_web.translator import Translator

T = TypeVar("T")
ValidatorResult: TypeAlias = Union[T, list[str]]


@dataclass
class ValidatedFormFields:
    product_name: str
    description: str
    timeframe: int
    production_unit: str
    amount: int
    means_cost: Decimal
    resource_cost: Decimal
    labour_cost: Decimal
    is_public_plan: bool


@dataclass
class DraftFormValidator:
    translator: Translator

    def validate(self, request: WebRequest) -> Union[DraftForm, ValidatedFormFields]:
        fields = {
            "product_name": self._validate_text_field(request, "prd_name", 100),
            "description": self._validate_text_field(request, "description"),
            "timeframe": self._validate_integer_field(request, "timeframe", 1, 365),
            "production_unit": self._validate_text_field(request, "prd_unit"),
            "amount": self._validate_integer_field(request, "prd_amount", 1),
            "means_cost": self._validate_decimal_field(request, "costs_p"),
            "resource_cost": self._validate_decimal_field(request, "costs_r"),
            "labour_cost": self._validate_decimal_field(request, "costs_a"),
            "is_public_plan": self._validate_boolean_field(request, "is_public_plan"),
        }

        errors = {
            key: value for key, value in fields.items() if isinstance(value, list)
        }
        if not self._is_at_least_one_cost_field_positive(fields):
            errors["general"] = [
                self.translator.gettext(
                    "At least one of the costs fields must be a positive number of hours."
                )
            ]

        if errors:
            return self._create_draft_form(request, errors)
        return self._create_validated_form_fields(fields)

    def _create_draft_form(self, request: WebRequest, errors: dict) -> DraftForm:
        return DraftForm(
            product_name_value=request.get_form("prd_name") or "",
            product_name_errors=errors.get("product_name", []),
            description_value=request.get_form("description") or "",
            description_errors=errors.get("description", []),
            timeframe_value=request.get_form("timeframe") or "",
            timeframe_errors=errors.get("timeframe", []),
            unit_of_distribution_value=request.get_form("prd_unit") or "",
            unit_of_distribution_errors=errors.get("production_unit", []),
            amount_value=request.get_form("prd_amount") or "",
            amount_errors=errors.get("amount", []),
            means_cost_value=request.get_form("costs_p") or "",
            means_cost_errors=errors.get("means_cost", []),
            resource_cost_value=request.get_form("costs_r") or "",
            resource_cost_errors=errors.get("resource_cost", []),
            labour_cost_value=request.get_form("costs_a") or "",
            labour_cost_errors=errors.get("labour_cost", []),
            is_public_plan_value=request.get_form("is_public_plan") or "",
            is_public_plan_errors=errors.get("is_public_plan", []),
            general_errors=errors.get("general", []),
        )

    def _create_validated_form_fields(self, fields: dict) -> ValidatedFormFields:
        return ValidatedFormFields(
            product_name=(
                fields["product_name"]
                if isinstance(fields["product_name"], str)
                else ""
            ),
            description=(
                fields["description"] if isinstance(fields["description"], str) else ""
            ),
            timeframe=(
                fields["timeframe"] if isinstance(fields["timeframe"], int) else 0
            ),
            production_unit=(
                fields["production_unit"]
                if isinstance(fields["production_unit"], str)
                else ""
            ),
            amount=fields["amount"] if isinstance(fields["amount"], int) else 0,
            means_cost=(
                fields["means_cost"]
                if isinstance(fields["means_cost"], Decimal)
                else Decimal(0)
            ),
            resource_cost=(
                fields["resource_cost"]
                if isinstance(fields["resource_cost"], Decimal)
                else Decimal(0)
            ),
            labour_cost=(
                fields["labour_cost"]
                if isinstance(fields["labour_cost"], Decimal)
                else Decimal(0)
            ),
            is_public_plan=(
                fields["is_public_plan"]
                if isinstance(fields["is_public_plan"], bool)
                else False
            ),
        )

    def _validate_text_field(
        self, request: WebRequest, field_name: str, max_length: Optional[int] = None
    ) -> ValidatorResult[str]:
        text = request.get_form(field_name)
        if self._is_form_field_missing(text):
            return [self.translator.gettext("This field is required.")]
        assert text is not None
        if max_length and len(text) > max_length:
            return [
                self.translator.gettext(
                    f"This field must be at most {max_length} characters long."
                )
            ]
        return text.strip()

    def _validate_integer_field(
        self,
        request: WebRequest,
        field_name: str,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
    ) -> ValidatorResult[int]:
        text = request.get_form(field_name)
        if self._is_form_field_missing(text):
            return [self.translator.gettext("This field is required.")]
        assert text is not None
        try:
            integer = int(text)
        except ValueError:
            return [self.translator.gettext("This field must be an integer.")]
        if (min_value is not None and integer < min_value) or (
            max_value is not None and integer > max_value
        ):
            if min_value is not None and max_value is not None:
                return [
                    self.translator.gettext(
                        f"This field must be an integer between {min_value} and {max_value}."
                    )
                ]
            elif min_value is not None:
                return [
                    self.translator.gettext(
                        f"This field must be an integer greater than or equal to {min_value}."
                    )
                ]
            elif max_value is not None:
                return [
                    self.translator.gettext(
                        f"This field must be an integer less than or equal to {max_value}."
                    )
                ]
        return integer

    def _validate_decimal_field(
        self, request: WebRequest, field_name: str
    ) -> ValidatorResult[Decimal]:
        text = request.get_form(field_name)
        if self._is_form_field_missing(text):
            return [self.translator.gettext("This field is required.")]
        assert text is not None
        try:
            decimal_number = Decimal(text)
        except InvalidOperation:
            return [
                self.translator.gettext("This field must be zero or a positive number.")
            ]
        if decimal_number < 0:
            return [
                self.translator.gettext("This field must be zero or a positive number.")
            ]
        return decimal_number

    def _validate_boolean_field(
        self, request: WebRequest, field_name: str
    ) -> ValidatorResult[bool]:
        text = request.get_form(field_name)
        return bool(text and text.strip())

    def _is_form_field_missing(self, value: Optional[str]) -> bool:
        return value is None or not value.strip()

    def _is_at_least_one_cost_field_positive(self, fields: dict) -> bool:
        return any(
            fields[key] > 0
            for key in ["means_cost", "resource_cost", "labour_cost"]
            if isinstance(fields[key], Decimal)
        )
