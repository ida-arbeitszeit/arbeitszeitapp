from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.use_cases import show_prd_account_details


@dataclass
class ShowPRDAccountDetailsController:
    def create_request(self, company: UUID) -> show_prd_account_details.Request:
        return show_prd_account_details.Request(company_id=company)
