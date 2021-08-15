from decimal import Decimal

import pytest

from arbeitszeit.errors import WorkerNotAtCompany
from arbeitszeit.use_cases import SendWorkCertificatesToWorker
from tests.data_generators import CompanyGenerator, MemberGenerator
from tests.dependency_injection import injection_test
from tests.repositories import (
    AccountRepository,
    CompanyWorkerRepository,
    TransactionRepository,
)


@injection_test
def test_that_after_transfer_balances_of_worker_and_company_are_correct(
    send_work_certificates_to_worker: SendWorkCertificatesToWorker,
    company_worker_repository: CompanyWorkerRepository,
    company_generator: CompanyGenerator,
    member_generator: MemberGenerator,
    account_repository: AccountRepository,
):
    company = company_generator.create_company()
    worker = member_generator.create_member()
    company_worker_repository.add_worker_to_company(company, worker)
    amount_to_transfer = Decimal(50)
    send_work_certificates_to_worker(
        company,
        worker,
        amount_to_transfer,
    )
    assert (
        account_repository.get_account_balance(company.work_account)
        == -amount_to_transfer
    )
    assert account_repository.get_account_balance(worker.account) == amount_to_transfer


@injection_test
def test_that_error_is_raised_if_money_is_sent_to_worker_not_working_in_company(
    send_work_certificates_to_worker: SendWorkCertificatesToWorker,
    company_worker_repository: CompanyWorkerRepository,
    company_generator: CompanyGenerator,
    member_generator: MemberGenerator,
):
    company = company_generator.create_company()
    worker1 = member_generator.create_member()
    company_worker_repository.add_worker_to_company(company, worker1)
    worker2 = member_generator.create_member()
    amount_to_transfer = Decimal(50)
    with pytest.raises(WorkerNotAtCompany):
        send_work_certificates_to_worker(
            company,
            worker2,
            amount_to_transfer,
        )


@injection_test
def test_that_after_transfer_one_transaction_is_added(
    send_work_certificates_to_worker: SendWorkCertificatesToWorker,
    company_worker_repository: CompanyWorkerRepository,
    transaction_repository: TransactionRepository,
    company_generator: CompanyGenerator,
    member_generator: MemberGenerator,
):
    company = company_generator.create_company()
    worker = member_generator.create_member()
    company_worker_repository.add_worker_to_company(company, worker)
    amount_to_transfer = Decimal(50)
    send_work_certificates_to_worker(
        company,
        worker,
        amount_to_transfer,
    )
    assert len(transaction_repository.transactions) == 1


@injection_test
def test_that_after_transfer_correct_transaction_is_added(
    send_work_certificates_to_worker: SendWorkCertificatesToWorker,
    company_worker_repository: CompanyWorkerRepository,
    transaction_repository: TransactionRepository,
    company_generator: CompanyGenerator,
    member_generator: MemberGenerator,
):
    company = company_generator.create_company()
    worker = member_generator.create_member()
    company_worker_repository.add_worker_to_company(company, worker)
    amount_to_transfer = Decimal(50)
    send_work_certificates_to_worker(
        company,
        worker,
        amount_to_transfer,
    )
    transaction = transaction_repository.transactions[0]
    assert transaction.amount == amount_to_transfer
    assert transaction.account_from == company.work_account
    assert transaction.account_to == worker.account
