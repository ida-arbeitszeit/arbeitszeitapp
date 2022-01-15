from dataclasses import dataclass
from typing import Protocol, Union
from uuid import UUID

from injector import inject

from arbeitszeit.use_cases.pay_consumer_product import (
    PayConsumerProductResponse,
    RejectionReason,
)

from .notification import Notifier


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


@inject
@dataclass
class PayConsumerProductViewModel:
    status_code: int


@inject
@dataclass
class PayConsumerProductPresenter:
    user_notifier: Notifier

    def present(
        self, use_case_response: PayConsumerProductResponse
    ) -> PayConsumerProductViewModel:
        if use_case_response.rejection_reason is None:
            self.user_notifier.display_info("Produkt erfolgreich bezahlt.")
            return PayConsumerProductViewModel(status_code=200)
        elif use_case_response.rejection_reason == RejectionReason.plan_inactive:
            self.user_notifier.display_warning(
                "Der angegebene Plan ist nicht aktuell. Bitte wende dich an den Verkäufer, um eine aktuelle Plan-ID zu erhalten."
            )
            return PayConsumerProductViewModel(status_code=410)
        else:
            self.user_notifier.display_warning(
                "Ein Plan mit der angegebene ID existiert nicht im System."
            )
            return PayConsumerProductViewModel(status_code=404)
