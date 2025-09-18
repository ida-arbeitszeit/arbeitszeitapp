from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.interactors.show_company_accounts import ShowCompanyAccountsRequest


@dataclass
class ShowCompanyAccountsController:
    def create_request(self, company_id: UUID) -> ShowCompanyAccountsRequest:
        return ShowCompanyAccountsRequest(company=company_id)
