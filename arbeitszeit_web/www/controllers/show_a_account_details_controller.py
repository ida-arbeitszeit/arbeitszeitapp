from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.use_cases import show_a_account_details


@dataclass
class ShowAAccountDetailsController:
    def create_request(self, company: UUID) -> show_a_account_details.Request:
        return show_a_account_details.Request(company=company)
