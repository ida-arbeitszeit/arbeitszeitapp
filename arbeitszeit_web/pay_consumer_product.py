from dataclasses import dataclass
from typing import List

from arbeitszeit.use_cases.pay_consumer_product import (
    PayConsumerProductResponse,
    RejectionReason,
)


@dataclass
class PayConsumerProductViewModel:
    notifications: List[str]


class PayConsumerProductPresenter:
    def present(
        self, use_case_response: PayConsumerProductResponse
    ) -> PayConsumerProductViewModel:
        if use_case_response.rejection_reason is None:
            notifications = ["Produkt erfolgreich bezahlt."]
        elif use_case_response.rejection_reason == RejectionReason.plan_inactive:
            notifications = [
                "Der angegebene Plan ist nicht aktuell. Bitte wende dich an den Verkäufer, um eine aktuelle Plan-ID zu erhalten."
            ]
        else:
            notifications = [
                "Ein Plan mit der angegebene ID existiert nicht im System."
            ]
        return PayConsumerProductViewModel(
            notifications=notifications,
        )
