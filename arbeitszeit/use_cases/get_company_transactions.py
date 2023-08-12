from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List
from uuid import UUID

from arbeitszeit.records import AccountTypes
from arbeitszeit.repositories import DatabaseGateway
from arbeitszeit.transactions import TransactionTypes, UserAccountingService


@dataclass
class TransactionInfo:
    transaction_type: TransactionTypes
    date: datetime
    transaction_volume: Decimal
    account_type: AccountTypes
    purpose: str


@dataclass
class GetCompanyTransactionsResponse:
    transactions: List[TransactionInfo]


@dataclass
class GetCompanyTransactions:
    accounting_service: UserAccountingService
    database_gateway: DatabaseGateway

    def __call__(self, company_id: UUID) -> GetCompanyTransactionsResponse:
        company = self.database_gateway.get_companies().with_id(company_id).first()
        assert company
        transactions = [
            TransactionInfo(
                transaction_type=row.transaction_type,
                date=row.transaction.date,
                transaction_volume=row.volume,
                account_type=row.account_type,
                purpose=row.transaction.purpose,
            )
            for row in self.accounting_service.get_statement_of_account(
                company, company.accounts()
            )
        ]
        return GetCompanyTransactionsResponse(transactions=transactions)
