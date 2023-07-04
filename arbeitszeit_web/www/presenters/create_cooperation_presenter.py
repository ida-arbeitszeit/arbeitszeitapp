from dataclasses import dataclass

from arbeitszeit.use_cases.create_cooperation import CreateCooperationResponse

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
        self, use_case_response: CreateCooperationResponse
    ) -> CreateCooperationViewModel:
        if not use_case_response.is_rejected:
            self.user_notifier.display_info(
                self.translator.gettext("Successfully created cooperation.")
            )
        elif (
            use_case_response.rejection_reason
            == CreateCooperationResponse.RejectionReason.cooperation_with_name_exists
        ):
            self.user_notifier.display_warning(
                self.translator.gettext(
                    "There is already a cooperation with the same name."
                )
            )
        elif (
            use_case_response.rejection_reason
            == CreateCooperationResponse.RejectionReason.coordinator_not_found
        ):
            self.user_notifier.display_warning(
                self.translator.gettext("Internal error: Coordinator not found.")
            )
        return CreateCooperationViewModel()
