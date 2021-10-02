from dataclasses import dataclass
from typing import List

from arbeitszeit.use_cases.create_offer import CreateOfferResponse, RejectionReason


@dataclass
class CreateOfferViewModel:
    notifications: List[str]


class CreateOfferPresenter:
    def present(self, use_case_response: CreateOfferResponse) -> CreateOfferViewModel:
        if use_case_response.rejection_reason is None:
            notifications = [
                "Dein Angebot wurde erfolgreich in unserem Marketplace veröffentlicht."
            ]
        elif use_case_response.rejection_reason == RejectionReason.plan_inactive:
            notifications = [
                "Angebot wurde nicht veröffentlicht. Der Plan ist nicht aktiv."
            ]

        return CreateOfferViewModel(notifications=notifications)
