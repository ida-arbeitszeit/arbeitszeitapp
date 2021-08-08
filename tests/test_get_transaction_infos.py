from datetime import datetime

from arbeitszeit.use_cases import GetTransactionInfos
from tests.data_generators import (
    CompanyGenerator,
    MemberGenerator,
    SocialAccountingGenerator,
    TransactionGenerator,
)
from tests.dependency_injection import injection_test
from tests.repositories import AccountOwnerRepository, TransactionRepository


@injection_test
def test_that_no_info_is_generated_when_no_transaction_took_place(
    get_transaction_infos: GetTransactionInfos,
    member_generator: MemberGenerator,
    company_generator: CompanyGenerator,
    account_owner_repository: AccountOwnerRepository,
):
    member = member_generator.create_member()
    company = company_generator.create_company()

    account_owner_repository.add(member)
    account_owner_repository.add(company)

    info = get_transaction_infos(member)
    assert not info


@injection_test
def test_that_info_is_generated_after_transaction_between_member_and_company(
    get_transaction_infos: GetTransactionInfos,
    member_generator: MemberGenerator,
    company_generator: CompanyGenerator,
    transaction_generator: TransactionGenerator,
    account_owner_repository: AccountOwnerRepository,
    transaction_repository: TransactionRepository,
):
    member = member_generator.create_member()
    company = company_generator.create_company()

    account_owner_repository.add(member)
    account_owner_repository.add(company)

    trans_sent_by_member_to_company = transaction_generator.create_transaction(
        account_from=member.account, account_to=company.product_account
    )
    transaction_repository.add(trans_sent_by_member_to_company)

    info = get_transaction_infos(member)
    expected_sender_name = "Mir"
    assert len(info) == 1
    assert type(info[0][0]) == datetime
    assert info[0][1] == expected_sender_name


@injection_test
def test_that_correct_info_for_sender_is_generated_after_transaction_between_company_and_company(
    get_transaction_infos: GetTransactionInfos,
    company_generator: CompanyGenerator,
    transaction_generator: TransactionGenerator,
    account_owner_repository: AccountOwnerRepository,
    transaction_repository: TransactionRepository,
):
    company1 = company_generator.create_company()
    company2 = company_generator.create_company()

    account_owner_repository.add(company1)
    account_owner_repository.add(company2)

    trans_sent_by_company_to_company = transaction_generator.create_transaction(
        account_from=company1.means_account, account_to=company2.product_account
    )
    transaction_repository.add(trans_sent_by_company_to_company)

    info = get_transaction_infos(company1)
    expected_sender_name = "Mir"
    expected_receiver_name = company2.name
    expected_amount_p = -trans_sent_by_company_to_company.amount
    assert info[0][1] == expected_sender_name
    assert info[0][2] == expected_receiver_name
    assert info[0][3] == expected_amount_p


@injection_test
def test_that_correct_info_for_receiver_is_generated_after_transaction_between_company_and_company(
    get_transaction_infos: GetTransactionInfos,
    company_generator: CompanyGenerator,
    transaction_generator: TransactionGenerator,
    account_owner_repository: AccountOwnerRepository,
    transaction_repository: TransactionRepository,
):
    company1 = company_generator.create_company()
    company2 = company_generator.create_company()

    account_owner_repository.add(company1)
    account_owner_repository.add(company2)

    trans_sent_by_company_to_company = transaction_generator.create_transaction(
        account_from=company1.means_account, account_to=company2.product_account
    )
    transaction_repository.add(trans_sent_by_company_to_company)

    info = get_transaction_infos(company2)
    expected_sender_name = company1.name
    expected_receiver_name = "Mich"
    expected_amount_prd = trans_sent_by_company_to_company.amount
    assert info[0][1] == expected_sender_name
    assert info[0][2] == expected_receiver_name
    assert info[0][6] == expected_amount_prd


@injection_test
def test_that_correct_info_for_receiver_is_generated_after_transaction_between_social_accounting_and_company(
    get_transaction_infos: GetTransactionInfos,
    company_generator: CompanyGenerator,
    transaction_generator: TransactionGenerator,
    account_owner_repository: AccountOwnerRepository,
    transaction_repository: TransactionRepository,
    social_accounting_generator: SocialAccountingGenerator,
):
    social_accounting = social_accounting_generator.create_social_accounting()
    company = company_generator.create_company()

    account_owner_repository.add(social_accounting)
    account_owner_repository.add(company)

    trans_sent_by_social_accounting_to_company = (
        transaction_generator.create_transaction(
            account_from=social_accounting.account, account_to=company.means_account
        )
    )
    transaction_repository.add(trans_sent_by_social_accounting_to_company)

    info = get_transaction_infos(company)
    expected_sender_name = "Öff. Buchhaltung"
    expected_receiver_name = "Mich"
    expected_amount_p = trans_sent_by_social_accounting_to_company.amount
    assert info[0][1] == expected_sender_name
    assert info[0][2] == expected_receiver_name
    assert info[0][3] == expected_amount_p


# test_that_transactions_are_returned_in_correct_order
