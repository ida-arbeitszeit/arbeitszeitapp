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
        notifications = (
            ["Erfolgreich bezahlt."]
            if use_case_response.rejection_reason is None
            else ["Plan existiert nicht."]
        )
        return PayMeansOfProductionViewModel(
            notifications=notifications,
        )
