from dataclasses import dataclass
from typing import Protocol, Union
from uuid import UUID

from injector import inject

from arbeitszeit.use_cases.pay_consumer_product import (
    PayConsumerProductResponse,
    RejectionReason,
)
from arbeitszeit_web.translator import Translator

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


@inject
@dataclass
class PayConsumerProductController:
    @dataclass
    class MalformedInputData:
        field: str
        message: str

    translator: Translator

    def import_form_data(
        self, current_user: UUID, form: PayConsumerProductForm
    ) -> Union[PayConsumerProductRequestImpl, MalformedInputData]:
        try:
            uuid = UUID(form.get_plan_id_field())
        except ValueError:
            return self.MalformedInputData(
                "plan_id", self.translator.gettext("Plan ID is invalid.")
            )
        try:
            amount = int(form.get_amount_field())
        except ValueError:
            return self.MalformedInputData(
                "amount", self.translator.gettext("This is not an integer.")
            )
        if amount < 0:
            return self.MalformedInputData(
                "amount", self.translator.gettext("Negative numbers are not allowed.")
            )
        return PayConsumerProductRequestImpl(current_user, uuid, amount)


@inject
@dataclass
class PayConsumerProductViewModel:
    status_code: int


@inject
@dataclass
class PayConsumerProductPresenter:
    user_notifier: Notifier
    translator: Translator

    def present(
        self, use_case_response: PayConsumerProductResponse
    ) -> PayConsumerProductViewModel:
        if use_case_response.rejection_reason is None:
            self.user_notifier.display_info(
                self.translator.gettext("Product successfully paid.")
            )
            return PayConsumerProductViewModel(status_code=200)
        elif use_case_response.rejection_reason == RejectionReason.plan_inactive:
            self.user_notifier.display_warning(
                self.translator.gettext(
                    "The specified plan has been expired. Please contact the selling company to provide you with an up-to-date plan ID."
                )
            )
            return PayConsumerProductViewModel(status_code=410)
        else:
            self.user_notifier.display_warning(
                self.translator.gettext(
                    "There is no plan with the specified ID in the database."
                )
            )
            return PayConsumerProductViewModel(status_code=404)
