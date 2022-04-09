from dataclasses import dataclass

from arbeitszeit.use_cases.pay_means_of_production import PayMeansOfProductionResponse
from arbeitszeit_web.controllers.pay_means_of_production_controller import (
    PayMeansOfProductionController,
)
from arbeitszeit_web.translator import Translator

from .notification import Notifier


@dataclass
class PayMeansOfProductionPresenter:
    user_notifier: Notifier
    trans: Translator

    def present(self, use_case_response: PayMeansOfProductionResponse) -> None:
        reasons = use_case_response.RejectionReason
        if use_case_response.rejection_reason is None:
            self.user_notifier.display_info(self.trans.gettext("Successfully paid."))
        elif use_case_response.rejection_reason == reasons.plan_not_found:
            self.user_notifier.display_warning(
                self.trans.gettext("Plan does not exist.")
            )
        elif use_case_response.rejection_reason == reasons.plan_is_not_active:
            self.user_notifier.display_warning(
                self.trans.gettext(
                    "The specified plan has expired. Please contact the provider to obtain a current plan ID."
                )
            )
        elif use_case_response.rejection_reason == reasons.cannot_buy_public_service:
            self.user_notifier.display_warning(
                self.trans.gettext(
                    "Payment failed. Companies cannot acquire public products."
                )
            )
        elif use_case_response.rejection_reason == reasons.buyer_is_planner:
            self.user_notifier.display_warning(
                self.trans.gettext(
                    "Payment failed. Companies cannot acquire their own products."
                )
            )
        else:
            self.user_notifier.display_warning(
                self.trans.gettext("The specified purpose is invalid.")
            )

    def present_malformed_data_warnings(
        self, malformed_data: PayMeansOfProductionController.MalformedInputData
    ) -> None:
        fields_and_messages = malformed_data.field_messages
        for field in fields_and_messages:
            for msg in fields_and_messages[field]:
                self.user_notifier.display_warning(msg)
