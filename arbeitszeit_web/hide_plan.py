from dataclasses import dataclass
from typing import List

from injector import inject

from arbeitszeit.use_cases.hide_plan import HidePlanResponse

from .notification import Notifier


@inject
@dataclass
class HidePlanPresenter:
    notifier: Notifier

    def present(self, use_case_response: HidePlanResponse) -> None:
        if use_case_response.is_success:
            self.notifier.display_info(
                f"Abgelaufener Plan {use_case_response.plan_id} wird dir nicht mehr angezeigt."
            )
