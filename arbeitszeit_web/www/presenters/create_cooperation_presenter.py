from dataclasses import dataclass

from arbeitszeit.interactors.create_cooperation import CreateCooperationResponse

from ...notification import Notifier
from ...translator import Translator


@dataclass
class CreateCooperationViewModel:
    pass


@dataclass(frozen=True)
class CreateCooperationPresenter:
    user_notifier: Notifier
    translator: Translator

    def present(
        self, interactor_response: CreateCooperationResponse
    ) -> CreateCooperationViewModel:
        if not interactor_response.is_rejected:
            self.user_notifier.display_info(
                self.translator.gettext("Successfully created cooperation.")
            )
        elif (
            interactor_response.rejection_reason
            == CreateCooperationResponse.RejectionReason.cooperation_with_name_exists
        ):
            self.user_notifier.display_warning(
                self.translator.gettext(
                    "There is already a cooperation with the same name."
                )
            )
        elif (
            interactor_response.rejection_reason
            == CreateCooperationResponse.RejectionReason.coordinator_not_found
        ):
            self.user_notifier.display_warning(
                self.translator.gettext("Internal error: Coordinator not found.")
            )
        return CreateCooperationViewModel()
