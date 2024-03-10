from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.use_cases import get_company_transactions


@dataclass
class GetCompanyTransactionsController:
    def create_request(self, company: UUID) -> get_company_transactions.Request:
        return get_company_transactions.Request(company=company)
