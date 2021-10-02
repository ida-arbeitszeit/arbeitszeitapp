from dataclasses import dataclass
from typing import List

from arbeitszeit.use_cases.pay_means_of_production import PayMeansOfProductionResponse


@dataclass
class PayMeansOfProductionViewModel:
    notifications: List[str]


class PayMeansOfProductionPresenter:
    def present(
        self, use_case_response: PayMeansOfProductionResponse
    ) -> PayMeansOfProductionViewModel:
        reasons = use_case_response.RejectionReason
        if use_case_response.rejection_reason is None:
            notifications = ["Erfolgreich bezahlt."]
        elif use_case_response.rejection_reason == reasons.plan_not_found:
            notifications = ["Plan existiert nicht."]
        else:
            notifications = ["Der angegebene Verwendungszweck is ungültig."]
        return PayMeansOfProductionViewModel(
            notifications=notifications,
        )
