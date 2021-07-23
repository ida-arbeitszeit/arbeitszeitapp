from dataclasses import dataclass
from decimal import Decimal

from injector import inject

from arbeitszeit import errors
from arbeitszeit.entities import Company, Member
from arbeitszeit.repositories import CompanyWorkerRepository, TransactionRepository
from arbeitszeit.transaction_factory import TransactionFactory

from .adjust_balance import adjust_balance


@inject
@dataclass
class SendWorkCertificatesToWorker:
    company_worker_repository: CompanyWorkerRepository
    transaction_repository: TransactionRepository
    transaction_factory: TransactionFactory

    def __call__(self, company: Company, worker: Member, amount: Decimal) -> None:
        """
        A company sends work certificates to an employee.

        What this function does:
        - It adjusts the balances of the company and employee accounts
        - It adds the transaction to the repository

        This function may raise a WorkerNotAtCompany if the worker is not employed at the company
        or a WorkerDoesNotExist exception if the worker does not exist.
        """
        company_workers = self.company_worker_repository.get_company_workers(company)
        if not worker:
            raise errors.WorkerDoesNotExist(
                worker=worker,
            )
        if worker not in company_workers:
            raise errors.WorkerNotAtCompany(
                worker=worker,
                company=company,
            )

        # adjust balances
        adjust_balance(company.work_account, -amount)
        adjust_balance(worker.account, amount)

        # create transaction
        transaction = self.transaction_factory.create_transaction(
            account_from=company.work_account,
            account_to=worker.account,
            amount=amount,
            purpose="Lohn",
        )
        self.transaction_repository.add(transaction)
