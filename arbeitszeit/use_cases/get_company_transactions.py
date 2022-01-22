from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List
from uuid import UUID

from injector import inject

from arbeitszeit.entities import AccountTypes, Company, Transaction
from arbeitszeit.repositories import CompanyRepository
from arbeitszeit.transactions import TransactionTypes, UserAccountingService


@dataclass
class TransactionInfo:
    type_of_transaction: TransactionTypes
    date: datetime
    transaction_volume: Decimal
    account_type: AccountTypes
    purpose: str


@dataclass
class GetCompanyTransactionsResponse:
    transactions: List[TransactionInfo]


@inject
@dataclass
class GetCompanyTransactions:
    accounting_service: UserAccountingService
    company_repository: CompanyRepository

    def __call__(self, company_id: UUID) -> GetCompanyTransactionsResponse:
        company = self.company_repository.get_by_id(company_id)
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
        user_is_sender = self._user_is_sender(transaction, company)
        transaction_type = self._get_transaction_type(transaction, user_is_sender)
        account_type = self._get_account_type(transaction, user_is_sender)
        transaction_volume = self._get_volume_for_transaction(
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

    def _user_is_sender(self, transaction: Transaction, company: Company) -> bool:
        return True if transaction.sending_account in company.accounts() else False

    def _get_volume_for_transaction(
        self,
        transaction: Transaction,
        user_is_sender: bool,
    ) -> Decimal:
        if user_is_sender:
            return -1 * transaction.amount_sent
        return transaction.amount_received

    def _get_transaction_type(
        self, transaction: Transaction, user_is_sender: bool
    ) -> TransactionTypes:
        transaction_type = self.accounting_service.get_transaction_type(
            transaction, user_is_sender
        )
        return transaction_type

    def _get_account_type(
        self, transaction: Transaction, user_is_sender: bool
    ) -> AccountTypes:
        if user_is_sender:
            account_type = transaction.sending_account.account_type
        else:
            account_type = transaction.receiving_account.account_type
        return account_type
