from dataclasses import dataclass
from typing import List

from arbeitszeit.use_cases.hide_plan import HidePlanResponse


@dataclass
class HidePlanViewModel:
    notifications: List[str]


class HidePlanPresenter:
    def present(self, use_case_response: HidePlanResponse) -> HidePlanViewModel:
        notifications: List[str] = []
        if use_case_response.is_success:
            notifications.append(
                f"Löschen des Plans {use_case_response.plan_id} erfolgreich."
            )
        return HidePlanViewModel(
            notifications=notifications,
        )
