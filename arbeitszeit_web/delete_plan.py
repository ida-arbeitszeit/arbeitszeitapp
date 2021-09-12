from dataclasses import dataclass
from typing import List

from arbeitszeit.use_cases.delete_plan import DeletePlanResponse


@dataclass
class DeletePlanViewModel:
    notifications: List[str]


class DeletePlanPresenter:
    def present(self, use_case_response: DeletePlanResponse) -> DeletePlanViewModel:
        notifications: List[str] = []
        if use_case_response.is_success:
            notifications.append(
                f"Löschen des Plans {use_case_response.plan_id} erfolgreich."
            )
        return DeletePlanViewModel(
            notifications=notifications,
        )
