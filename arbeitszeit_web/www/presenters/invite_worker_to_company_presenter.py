from dataclasses import dataclass

from arbeitszeit.use_cases.invite_worker_to_company import InviteWorkerToCompanyUseCase
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.translator import Translator


@dataclass
class ViewModel:
    status_code: int
    worker: str


@dataclass
class InviteWorkerToCompanyPresenter:
    translator: Translator
    notifier: Notifier

    def present(
        self, use_case_response: InviteWorkerToCompanyUseCase.Response
    ) -> ViewModel:
        match use_case_response.rejection_reason:
            case InviteWorkerToCompanyUseCase.Response.RejectionReason.WORKER_NOT_FOUND:
                self.notifier.display_warning(
                    self.translator.gettext("Worker could not be found.")
                )
                return ViewModel(status_code=400, worker=str(use_case_response.worker))
            case (
                InviteWorkerToCompanyUseCase.Response.RejectionReason.COMPANY_NOT_FOUND
            ):
                self.notifier.display_warning(
                    self.translator.gettext("Company could not be found.")
                )
                return ViewModel(status_code=400, worker=str(use_case_response.worker))
            case (
                InviteWorkerToCompanyUseCase.Response.RejectionReason.WORKER_ALREADY_WORKS_FOR_COMPANY
            ):
                self.notifier.display_warning(
                    self.translator.gettext("Worker already works for the company.")
                )
                return ViewModel(status_code=400, worker=str(use_case_response.worker))
            case (
                InviteWorkerToCompanyUseCase.Response.RejectionReason.INVITATION_ALREADY_ISSUED
            ):
                self.notifier.display_warning(
                    self.translator.gettext("Invitation has already been issued.")
                )
                return ViewModel(status_code=400, worker=str(use_case_response.worker))
            case None:
                self.notifier.display_info(
                    self.translator.gettext("Worker has been invited successfully.")
                )
                return ViewModel(status_code=302, worker=str(use_case_response.worker))
