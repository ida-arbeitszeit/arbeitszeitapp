from dataclasses import dataclass
from decimal import Decimal

from injector import inject

from arbeitszeit import errors
from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import Company, Member
from arbeitszeit.repositories import CompanyWorkerRepository, TransactionRepository


@inject
@dataclass
class SendWorkCertificatesToWorker:
    company_worker_repository: CompanyWorkerRepository
    transaction_repository: TransactionRepository
    datetime_service: DatetimeService

    def __call__(self, company: Company, worker: Member, amount: Decimal) -> None:
        """
        A company sends work certificates to an employee.

        What this function does:
        - It adjusts the balances of the company and employee accounts
        - It adds the transaction to the repository

        This function may raise a WorkerNotAtCompany if the worker is not employed at the company.
        """
        company_workers = self.company_worker_repository.get_company_workers(company)
        if worker not in company_workers:
            raise errors.WorkerNotAtCompany(
                worker=worker,
                company=company,
            )
        self.transaction_repository.create_transaction(
            date=self.datetime_service.now(),
            sending_account=company.work_account,
            receiving_account=worker.account,
            amount=amount,
            purpose="Lohn",
        )
