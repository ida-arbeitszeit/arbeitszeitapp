from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.interactors import show_r_account_details


@dataclass
class ShowRAccountDetailsController:
    def create_request(self, company: UUID) -> show_r_account_details.Request:
        return show_r_account_details.Request(company=company)
