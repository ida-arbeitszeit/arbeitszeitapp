from dataclasses import dataclass
from typing import List, Protocol, Union
from uuid import UUID, uuid4

from arbeitszeit.use_cases.pay_consumer_product import (
    PayConsumerProductResponse,
    RejectionReason,
)


@dataclass
class PayConsumerProductRequestImpl:
    user: UUID
    plan: UUID
    amount: int

    def get_buyer_id(self) -> UUID:
        return self.user

    def get_plan_id(self) -> UUID:
        return self.plan

    def get_amount(self) -> int:
        return self.amount


class PayConsumerProductForm(Protocol):
    def get_plan_id_field(self) -> str:
        ...

    def get_amount_field(self) -> str:
        ...


class PayConsumerProductController:
    @dataclass
    class MalformedInputData:
        field: str
        message: str

    def import_form_data(
        self, current_user: UUID, form: PayConsumerProductForm
    ) -> Union[PayConsumerProductRequestImpl, MalformedInputData]:
        try:
            uuid = UUID(form.get_plan_id_field())
        except ValueError:
            return self.MalformedInputData("plan_id", "Plan-ID ist ungültig")
        try:
            amount = int(form.get_amount_field())
        except ValueError:
            return self.MalformedInputData("amount", "Das ist keine ganze Zahl")
        return PayConsumerProductRequestImpl(current_user, uuid, amount)


@dataclass
class PayConsumerProductViewModel:
    notifications: List[str]


class PayConsumerProductPresenter:
    def present(
        self, use_case_response: PayConsumerProductResponse
    ) -> PayConsumerProductViewModel:
        if use_case_response.rejection_reason is None:
            notifications = ["Produkt erfolgreich bezahlt."]
        elif use_case_response.rejection_reason == RejectionReason.plan_inactive:
            notifications = [
                "Der angegebene Plan ist nicht aktuell. Bitte wende dich an den Verkäufer, um eine aktuelle Plan-ID zu erhalten."
            ]
        else:
            notifications = [
                "Ein Plan mit der angegebene ID existiert nicht im System."
            ]
        return PayConsumerProductViewModel(
            notifications=notifications,
        )
