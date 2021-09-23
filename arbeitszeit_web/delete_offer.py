from dataclasses import dataclass
from typing import List

from arbeitszeit.use_cases.delete_offer import DeleteOfferResponse


@dataclass
class DeleteOfferViewModel:
    notifications: List[str]


class DeleteOfferPresenter:
    def present(self, use_case_response: DeleteOfferResponse) -> DeleteOfferViewModel:
        notifications: List[str] = []
        if use_case_response.is_success:
            notifications.append(
                f"Löschen des Angebots {use_case_response.offer_id} erfolgreich."
            )
        else:
            notifications.append(
                f"Löschen des Angebots {use_case_response.offer_id} nicht erfolgreich."
            )
        return DeleteOfferViewModel(
            notifications=notifications,
        )
