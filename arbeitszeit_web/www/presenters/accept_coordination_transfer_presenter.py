from dataclasses import dataclass
from typing import Optional

from typing_extensions import assert_never

from arbeitszeit.use_cases.accept_coordination_transfer import (
    AcceptCoordinationTransferUseCase,
)
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex


@dataclass
class ViewModel:
    status_code: int
    redirect_url: Optional[str]


@dataclass
class AcceptCoordinationTransferPresenter:
    translator: Translator
    notifier: Notifier
    url_index: UrlIndex

    def present(
        self, use_case_response: AcceptCoordinationTransferUseCase.Response
    ) -> ViewModel:
        if use_case_response.is_rejected:
            assert use_case_response.rejection_reason
            warning, status_code = self._evaluate_rejection_reason(
                use_case_response.rejection_reason
            )
            self.notifier.display_warning(warning)
            return ViewModel(
                status_code=status_code,
                redirect_url=None,
            )
        else:
            assert use_case_response.cooperation_id
            self.notifier.display_info(
                self.translator.gettext(
                    "Successfully accepted the request. You are now coordinator of the cooperation."
                )
            )
            return ViewModel(
                status_code=302,
                redirect_url=self.url_index.get_show_coordination_transfer_request_url(
                    transfer_request=use_case_response.transfer_request_id,
                ),
            )

    def _evaluate_rejection_reason(
        self,
        rejection_reason: AcceptCoordinationTransferUseCase.Response.RejectionReason,
    ) -> tuple[str, int]:
        if (
            rejection_reason
            is AcceptCoordinationTransferUseCase.Response.RejectionReason.transfer_request_not_found
        ):
            warning = self.translator.gettext("Transfer request not found.")
            status_code = 404
            return warning, status_code
        elif (
            rejection_reason
            is AcceptCoordinationTransferUseCase.Response.RejectionReason.transfer_request_closed
        ):
            warning = self.translator.gettext("This request is not valid anymore.")
            status_code = 409
            return warning, status_code
        elif (
            rejection_reason
            is AcceptCoordinationTransferUseCase.Response.RejectionReason.accepting_company_is_not_candidate
        ):
            warning = self.translator.gettext(
                "You are not the candidate of this request."
            )
            status_code = 403
            return warning, status_code
        assert_never(rejection_reason)
