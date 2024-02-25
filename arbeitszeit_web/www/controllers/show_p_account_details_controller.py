from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.use_cases.show_p_account_details import ShowPAccountDetailsUseCase


@dataclass
class ShowPAccountDetailsController:
    def create_request(self, company: UUID) -> ShowPAccountDetailsUseCase.Request:
        return ShowPAccountDetailsUseCase.Request(company=company)
