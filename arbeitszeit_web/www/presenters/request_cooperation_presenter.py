from dataclasses import dataclass
from typing import List

from arbeitszeit.interactors.request_cooperation import RequestCooperationResponse
from arbeitszeit_web.translator import Translator


@dataclass
class RequestCooperationViewModel:
    notifications: List[str]
    is_error: bool


@dataclass
class RequestCooperationPresenter:
    translator: Translator

    def present(
        self, interactor_response: RequestCooperationResponse
    ) -> RequestCooperationViewModel:
        view_model = self._create_view_model(interactor_response)
        return view_model

    def _create_view_model(
        self, interactor_response: RequestCooperationResponse
    ) -> RequestCooperationViewModel:
        notifications = []
        if not interactor_response.is_rejected:
            is_error = False
            notifications.append(self.translator.gettext("Request has been sent."))
        else:
            is_error = True
            if (
                interactor_response.rejection_reason
                == RequestCooperationResponse.RejectionReason.plan_not_found
            ):
                notifications.append(self.translator.gettext("Plan not found."))
            elif (
                interactor_response.rejection_reason
                == RequestCooperationResponse.RejectionReason.cooperation_not_found
            ):
                notifications.append(self.translator.gettext("Cooperation not found."))
            elif (
                interactor_response.rejection_reason
                == RequestCooperationResponse.RejectionReason.plan_inactive
            ):
                notifications.append(self.translator.gettext("Plan not active."))
            elif interactor_response.rejection_reason in (
                RequestCooperationResponse.RejectionReason.plan_has_cooperation,
                RequestCooperationResponse.RejectionReason.plan_is_already_requesting_cooperation,
            ):
                notifications.append(
                    self.translator.gettext(
                        "Plan is already cooperating or requested a cooperation."
                    )
                )
            elif (
                interactor_response.rejection_reason
                == RequestCooperationResponse.RejectionReason.plan_is_public_service
            ):
                notifications.append(
                    self.translator.gettext("Public plans cannot cooperate.")
                )
            elif (
                interactor_response.rejection_reason
                == RequestCooperationResponse.RejectionReason.requester_is_not_planner
            ):
                notifications.append(
                    self.translator.gettext(
                        "Only the creator of a plan can request a cooperation."
                    )
                )
        return RequestCooperationViewModel(
            notifications=notifications, is_error=is_error
        )
