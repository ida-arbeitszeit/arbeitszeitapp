from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List
from uuid import UUID

from injector import inject

from arbeitszeit.entities import Company, Transaction
from arbeitszeit.repositories import AccountRepository, CompanyRepository
from arbeitszeit.transactions import TransactionTypes, UserAccountingService


@dataclass
class TransactionInfo:
    type_of_transaction: TransactionTypes
    date: datetime
    transaction_volume: Decimal
    purpose: str


@dataclass
class GetAccountPResponse:
    transactions: List[TransactionInfo]
    account_balance: Decimal


@inject
@dataclass
class GetAccountP:
    accounting_service: UserAccountingService
    company_repository: CompanyRepository
    account_repository: AccountRepository

    def __call__(self, company_id: UUID) -> GetAccountPResponse:
        company = self.company_repository.get_by_id(company_id)
        assert company
        transactions = [
            self._create_info(company, transaction)
            for transaction in self.accounting_service.get_account_p_transactions_sorted(
                company
            )
        ]
        account_balance = self.account_repository.get_account_balance(
            company.means_account
        )
        return GetAccountPResponse(
            transactions=transactions, account_balance=account_balance
        )

    def _create_info(
        self,
        company: Company,
        transaction: Transaction,
    ) -> TransactionInfo:
        user_is_sender = self._user_is_sender(transaction, company)
        transaction_type = self._get_transaction_type(transaction, user_is_sender)
        transaction_volume = self._get_volume_for_transaction(
            transaction,
            user_is_sender,
        )
        return TransactionInfo(
            transaction_type,
            transaction.date,
            transaction_volume,
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
