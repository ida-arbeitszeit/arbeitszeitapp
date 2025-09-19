from dataclasses import dataclass

from arbeitszeit.interactors.register_hours_worked import RegisterHoursWorkedResponse
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.www.controllers.register_hours_worked_controller import (
    ControllerRejection,
)

from ...translator import Translator


@dataclass
class RegisterHoursWorkedPresenter:
    notifier: Notifier
    translator: Translator

    def present_interactor_response(self, response: RegisterHoursWorkedResponse) -> int:
        if response.is_rejected:
            if (
                response.rejection_reason
                == RegisterHoursWorkedResponse.RejectionReason.worker_not_at_company
            ):
                self.notifier.display_warning(
                    self.translator.gettext(
                        "This worker does not work in your company."
                    )
                )
            return 404
        else:
            self.notifier.display_info(
                self.translator.gettext("Labour hours successfully registered")
            )
            return 302

    def present_controller_warnings(
        self, controller_rejection: ControllerRejection
    ) -> None:
        if (
            controller_rejection.reason
            == ControllerRejection.RejectionReason.invalid_input
        ):
            self.notifier.display_warning(self.translator.gettext("Invalid input"))
        elif (
            controller_rejection.reason
            == ControllerRejection.RejectionReason.negative_amount
        ):
            self.notifier.display_warning(
                self.translator.gettext("A negative amount is not allowed.")
            )
