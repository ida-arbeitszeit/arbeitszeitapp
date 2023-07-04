from dataclasses import dataclass
from typing import List

from arbeitszeit.use_cases.invite_worker_to_company import InviteWorkerToCompanyUseCase
from arbeitszeit_web.translator import Translator


@dataclass
class ViewModel:
    notifications: List[str]


@dataclass
class InviteWorkerToCompanyPresenter:
    translator: Translator

    def present(
        self, use_case_response: InviteWorkerToCompanyUseCase.Response
    ) -> ViewModel:
        if use_case_response.is_success:
            notifications = [
                self.translator.gettext("Worker has been invited successfully.")
            ]
        else:
            notifications = [self.translator.gettext("Worker could not be invited.")]
        return ViewModel(
            notifications=notifications,
        )
