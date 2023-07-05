from dataclasses import dataclass

from arbeitszeit.use_cases.send_work_certificates_to_worker import (
    SendWorkCertificatesToWorkerResponse,
)
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.www.controllers.send_work_certificates_to_worker_controller import (
    ControllerRejection,
)

from ...translator import Translator


@dataclass
class SendWorkCertificatesToWorkerPresenter:
    notifier: Notifier
    translator: Translator

    def present_use_case_response(
        self, response: SendWorkCertificatesToWorkerResponse
    ) -> int:
        if response.is_rejected:
            if (
                response.rejection_reason
                == SendWorkCertificatesToWorkerResponse.RejectionReason.worker_not_at_company
            ):
                self.notifier.display_warning(
                    self.translator.gettext(
                        "This worker does not work in your company."
                    )
                )
            return 404
        else:
            self.notifier.display_info(
                self.translator.gettext("Work certificates successfully transferred.")
            )
            return 200

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
