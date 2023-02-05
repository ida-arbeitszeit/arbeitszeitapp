from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List
from uuid import UUID

from arbeitszeit.entities import AccountTypes, Company, Transaction
from arbeitszeit.repositories import AccountRepository, CompanyRepository
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
    company_repository: CompanyRepository
    account_repository: AccountRepository

    def __call__(self, company_id: UUID) -> GetCompanyTransactionsResponse:
        company = self.company_repository.get_companies().with_id(company_id).first()
        assert company
        transactions = [
            self._create_info(company, transaction)
            for transaction in self.accounting_service.get_all_transactions_sorted(
                company
            )
        ]
        return GetCompanyTransactionsResponse(transactions=transactions)

    def _create_info(
        self,
        company: Company,
        transaction: Transaction,
    ) -> TransactionInfo:
        user_is_sender = self.accounting_service.user_is_sender(transaction, company)
        transaction_type = self.accounting_service.get_transaction_type(
            transaction, user_is_sender
        )
        account_type = self._get_account_type(transaction, user_is_sender)
        transaction_volume = self.accounting_service.get_transaction_volume(
            transaction,
            user_is_sender,
        )
        return TransactionInfo(
            transaction_type,
            transaction.date,
            transaction_volume,
            account_type,
            transaction.purpose,
        )

    def _get_account_type(
        self, transaction: Transaction, user_is_sender: bool
    ) -> AccountTypes:
        account = (
            self.account_repository.get_accounts()
            .with_id(
                transaction.sending_account
                if user_is_sender
                else transaction.receiving_account
            )
            .first()
        )
        assert account
        return account.account_type
