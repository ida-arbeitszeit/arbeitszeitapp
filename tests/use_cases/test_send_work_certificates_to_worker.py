from decimal import Decimal

from arbeitszeit.use_cases import (
    SendWorkCertificatesToWorker,
    SendWorkCertificatesToWorkerRequest,
    SendWorkCertificatesToWorkerResponse,
)
from tests.data_generators import CompanyGenerator, MemberGenerator

from .dependency_injection import injection_test
from .repositories import (
    AccountRepository,
    CompanyWorkerRepository,
    TransactionRepository,
)


@injection_test
def test_that_transfer_is_rejected_if_money_is_sent_to_worker_not_working_in_company(
    send_work_certificates_to_worker: SendWorkCertificatesToWorker,
    company_worker_repository: CompanyWorkerRepository,
    company_generator: CompanyGenerator,
    member_generator: MemberGenerator,
):
    company = company_generator.create_company()
    worker1 = member_generator.create_member()
    company_worker_repository.add_worker_to_company(company.id, worker1.id)
    worker2 = member_generator.create_member()
    amount_to_transfer = Decimal(50)

    response = send_work_certificates_to_worker(
        SendWorkCertificatesToWorkerRequest(company.id, worker2.id, amount_to_transfer)
    )
    assert response.is_rejected
    assert (
        response.rejection_reason
        == SendWorkCertificatesToWorkerResponse.RejectionReason.worker_not_at_company
    )


@injection_test
def test_that_correct_transfer_does_not_get_rejected(
    send_work_certificates_to_worker: SendWorkCertificatesToWorker,
    company_worker_repository: CompanyWorkerRepository,
    company_generator: CompanyGenerator,
    member_generator: MemberGenerator,
):
    company = company_generator.create_company()
    worker = member_generator.create_member()
    company_worker_repository.add_worker_to_company(company.id, worker.id)
    amount_to_transfer = Decimal(50)
    response = send_work_certificates_to_worker(
        SendWorkCertificatesToWorkerRequest(company.id, worker.id, amount_to_transfer)
    )
    assert not response.is_rejected


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
    company_worker_repository.add_worker_to_company(company.id, worker.id)
    amount_to_transfer = Decimal(50)
    send_work_certificates_to_worker(
        SendWorkCertificatesToWorkerRequest(company.id, worker.id, amount_to_transfer)
    )
    assert (
        account_repository.get_account_balance(company.work_account)
        == -amount_to_transfer
    )
    assert account_repository.get_account_balance(worker.account) == amount_to_transfer


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
    company_worker_repository.add_worker_to_company(company.id, worker.id)
    amount_to_transfer = Decimal(50)
    send_work_certificates_to_worker(
        SendWorkCertificatesToWorkerRequest(company.id, worker.id, amount_to_transfer)
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
    company_worker_repository.add_worker_to_company(company.id, worker.id)
    amount_to_transfer = Decimal(50)
    send_work_certificates_to_worker(
        SendWorkCertificatesToWorkerRequest(company.id, worker.id, amount_to_transfer)
    )

    assert len(transaction_repository.transactions) == 1
    transaction = transaction_repository.transactions[0]
    assert transaction.amount_sent == amount_to_transfer
    assert transaction.amount_received == amount_to_transfer
    assert transaction.sending_account == company.work_account
    assert transaction.receiving_account == worker.account
