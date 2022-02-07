from dataclasses import dataclass

from arbeitszeit.use_cases.pay_means_of_production import PayMeansOfProductionResponse
from arbeitszeit_web.controllers.pay_means_of_production_controller import (
    PayMeansOfProductionController,
)

from .notification import Notifier


@dataclass
class PayMeansOfProductionPresenter:
    user_notifier: Notifier

    def present(self, use_case_response: PayMeansOfProductionResponse) -> None:
        reasons = use_case_response.RejectionReason
        if use_case_response.rejection_reason is None:
            self.user_notifier.display_info("Erfolgreich bezahlt.")
        elif use_case_response.rejection_reason == reasons.plan_not_found:
            self.user_notifier.display_warning("Plan existiert nicht.")
        elif use_case_response.rejection_reason == reasons.plan_is_not_active:
            self.user_notifier.display_warning(
                "Der angegebene Plan ist nicht aktuell. Bitte wende dich an den Verkäufer, um eine aktuelle Plan-ID zu erhalten."
            )
        elif use_case_response.rejection_reason == reasons.cannot_buy_public_service:
            self.user_notifier.display_warning(
                "Bezahlung nicht erfolgreich. Betriebe können keine öffentlichen Dienstleistungen oder Produkte erwerben."
            )
        elif use_case_response.rejection_reason == reasons.buyer_is_planner:
            self.user_notifier.display_warning(
                "Bezahlung nicht erfolgreich. Betriebe können keine eigenen Produkte erwerben."
            )
        else:
            self.user_notifier.display_warning(
                "Der angegebene Verwendungszweck is ungültig."
            )

    def present_malformed_data_warnings(
        self, malformed_data: PayMeansOfProductionController.MalformedInputData
    ) -> None:
        fields_and_messages = malformed_data.field_messages
        for field in fields_and_messages:
            for msg in fields_and_messages[field]:
                self.user_notifier.display_warning(msg)
