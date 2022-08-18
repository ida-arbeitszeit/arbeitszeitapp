from dataclasses import dataclass
from uuid import UUID

from injector import inject

from arbeitszeit.use_cases.pay_consumer_product import (
    PayConsumerProductResponse,
    RejectionReason,
)
from arbeitszeit_web.forms import PayConsumerProductForm
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


@inject
@dataclass
class PayConsumerProductController:
    class FormError(Exception):
        pass

    translator: Translator

    def import_form_data(
        self, current_user: UUID, form: PayConsumerProductForm
    ) -> PayConsumerProductRequestImpl:
        try:
            plan_id = UUID(form.plan_id_field().get_value())
        except ValueError:
            form.plan_id_field().attach_error(
                self.translator.gettext("Plan ID is invalid.")
            )
            raise self.FormError()
        try:
            amount = int(form.amount_field().get_value())
            if amount <= 0:
                form.amount_field().attach_error(
                    self.translator.gettext("Must be a number larger than zero.")
                )
                raise self.FormError()
        except ValueError:
            form.amount_field().attach_error(
                self.translator.gettext("This is not an integer.")
            )
            raise self.FormError()
        return PayConsumerProductRequestImpl(current_user, plan_id, amount)


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
        elif use_case_response.rejection_reason == RejectionReason.insufficient_balance:
            self.user_notifier.display_warning(
                self.translator.gettext("You do not have enough work certificates.")
            )
            return PayConsumerProductViewModel(status_code=406)
        else:
            self.user_notifier.display_warning(
                self.translator.gettext(
                    "There is no plan with the specified ID in the database."
                )
            )
            return PayConsumerProductViewModel(status_code=404)
