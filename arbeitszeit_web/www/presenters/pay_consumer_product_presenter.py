from dataclasses import dataclass

from arbeitszeit.use_cases.pay_consumer_product import (
    PayConsumerProductResponse,
    RejectionReason,
)
from arbeitszeit_web.translator import Translator

from ...notification import Notifier


@dataclass
class PayConsumerProductViewModel:
    status_code: int


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
        elif use_case_response.rejection_reason == RejectionReason.buyer_does_not_exist:
            self.user_notifier.display_warning(
                self.translator.gettext(
                    "Failed to pay for consumer product. Are you logged in as a member?"
                )
            )
            return PayConsumerProductViewModel(status_code=404)
        else:
            self.user_notifier.display_warning(
                self.translator.gettext(
                    "There is no plan with the specified ID in the database."
                )
            )
            return PayConsumerProductViewModel(status_code=404)
