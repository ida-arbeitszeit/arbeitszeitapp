from dataclasses import dataclass

from arbeitszeit.use_cases.remove_worker_from_company import Response as UseCaseResponse
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex
from arbeitszeit_web.www.response import Redirect


@dataclass
class ErrorCode:
    code: int


ViewModel = Redirect | ErrorCode


@dataclass
class RemoveWorkerFromCompanyPresenter:
    notifier: Notifier
    translator: Translator
    url_index: UrlIndex

    def present(self, use_case_response: UseCaseResponse) -> ViewModel:
        if not use_case_response.is_rejected:
            self.notifier.display_info(
                self.translator.gettext("Worker successfully removed from company.")
            )
            return Redirect(url=self.url_index.get_invite_worker_to_company_url())

        assert use_case_response.rejection_reason is not None

        match use_case_response.rejection_reason:
            case UseCaseResponse.RejectionReason.company_not_found:
                message = "Company not found."
                code = 404
            case UseCaseResponse.RejectionReason.not_workplace_of_worker:
                message = "Worker is not a member of the company."
                code = 400
            case UseCaseResponse.RejectionReason.worker_not_found:
                message = "Worker not found."
                code = 404
            case _:
                message = "An unknown error occurred."
                code = 500
        self.notifier.display_warning(self.translator.gettext(message))
        return ErrorCode(code)
