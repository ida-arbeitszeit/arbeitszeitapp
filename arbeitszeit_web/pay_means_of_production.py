from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from arbeitszeit.use_cases.pay_means_of_production import PayMeansOfProductionResponse
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex

from .notification import Notifier


@dataclass
class PayMeansOfProductionPresenter:
    @dataclass
    class ViewModel:
        redirect_url: Optional[str]

    user_notifier: Notifier
    trans: Translator
    url_index: UrlIndex

    def present(self, use_case_response: PayMeansOfProductionResponse) -> ViewModel:
        redirect_url: Optional[str] = None

        reasons = use_case_response.RejectionReason
        if use_case_response.rejection_reason is None:
            self.user_notifier.display_info(self.trans.gettext("Successfully paid."))
            redirect_url = self.url_index.get_pay_means_of_production_url()
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
        return self.ViewModel(redirect_url=redirect_url)
