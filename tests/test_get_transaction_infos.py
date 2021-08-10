from datetime import datetime

from arbeitszeit.entities import AccountTypes, SocialAccounting
from arbeitszeit.use_cases import GetTransactionInfos
from tests.data_generators import (
    CompanyGenerator,
    MemberGenerator,
    SocialAccountingGenerator,
    TransactionGenerator,
)
from tests.dependency_injection import injection_test
from tests.repositories import TransactionRepository


@injection_test
def test_that_no_info_is_generated_when_no_transaction_took_place(
    get_transaction_infos: GetTransactionInfos,
    member_generator: MemberGenerator,
    company_generator: CompanyGenerator,
):
    member = member_generator.create_member()
    company_generator.create_company()

    info = get_transaction_infos(member)
    assert not info


@injection_test
def test_that_info_is_generated_after_transaction_between_member_and_company(
    get_transaction_infos: GetTransactionInfos,
    member_generator: MemberGenerator,
    company_generator: CompanyGenerator,
    transaction_generator: TransactionGenerator,
    transaction_repository: TransactionRepository,
):
    member = member_generator.create_member()
    company = company_generator.create_company()

    trans_sent_by_member_to_company = transaction_generator.create_transaction(
        account_from=member.account, account_to=company.product_account
    )
    transaction_repository.add(trans_sent_by_member_to_company)

    info = get_transaction_infos(member)
    expected_sender_name = "Mir"
    assert len(info) == 1
    assert type(info[0].date) == datetime
    assert info[0].sender_name == expected_sender_name


@injection_test
def test_that_correct_info_for_sender_is_generated_after_transaction_between_company_and_company(
    get_transaction_infos: GetTransactionInfos,
    company_generator: CompanyGenerator,
    transaction_generator: TransactionGenerator,
    transaction_repository: TransactionRepository,
):
    company1 = company_generator.create_company()
    company2 = company_generator.create_company()

    trans_sent_by_company_to_company = transaction_generator.create_transaction(
        account_from=company1.means_account, account_to=company2.product_account
    )
    transaction_repository.add(trans_sent_by_company_to_company)

    info = get_transaction_infos(company1)
    expected_sender_name = "Mir"
    expected_receiver_name = company2.name
    expected_amount_p = -trans_sent_by_company_to_company.amount
    assert info[0].sender_name == expected_sender_name
    assert info[0].receiver_name == expected_receiver_name
    assert info[0].transaction_volumes[AccountTypes.p.value] == expected_amount_p


@injection_test
def test_that_correct_info_for_receiver_is_generated_after_transaction_between_company_and_company(
    get_transaction_infos: GetTransactionInfos,
    company_generator: CompanyGenerator,
    transaction_generator: TransactionGenerator,
    transaction_repository: TransactionRepository,
):
    company1 = company_generator.create_company()
    company2 = company_generator.create_company()

    trans_sent_by_company_to_company = transaction_generator.create_transaction(
        account_from=company1.means_account, account_to=company2.product_account
    )
    transaction_repository.add(trans_sent_by_company_to_company)

    info = get_transaction_infos(company2)
    expected_sender_name = company1.name
    expected_receiver_name = "Mich"
    expected_amount_prd = trans_sent_by_company_to_company.amount
    assert info[0].sender_name == expected_sender_name
    assert info[0].receiver_name == expected_receiver_name
    assert info[0].transaction_volumes[AccountTypes.prd.value] == expected_amount_prd


@injection_test
def test_that_correct_info_for_sender_is_generated_after_several_transactions_between_company_and_company(
    get_transaction_infos: GetTransactionInfos,
    company_generator: CompanyGenerator,
    transaction_generator: TransactionGenerator,
    transaction_repository: TransactionRepository,
):
    company1 = company_generator.create_company()
    company2 = company_generator.create_company()

    trans1_sent_by_company_to_company = transaction_generator.create_transaction(
        account_from=company1.means_account, account_to=company2.product_account
    )
    trans2_sent_by_company_to_company = transaction_generator.create_transaction(
        account_from=company2.means_account, account_to=company1.product_account
    )
    trans3_sent_by_company_to_company = transaction_generator.create_transaction(
        account_from=company1.means_account, account_to=company2.product_account
    )
    transaction_repository.add(trans1_sent_by_company_to_company)
    transaction_repository.add(trans2_sent_by_company_to_company)
    transaction_repository.add(trans3_sent_by_company_to_company)

    info = get_transaction_infos(company1)

    expected_sender_name1 = "Mir"
    expected_sender_name2 = company2.name
    expected_sender_name3 = "Mir"

    expected_receiver_name1 = company2.name
    expected_receiver_name2 = "Mich"
    expected_receiver_name3 = company2.name

    assert len(info) == 3
    assert (
        (info[0].sender_name == expected_sender_name1)
        and (info[1].sender_name == expected_sender_name2)
        and (info[2].sender_name == expected_sender_name3)
    )
    assert (
        (info[0].receiver_name == expected_receiver_name1)
        and (info[1].receiver_name == expected_receiver_name2)
        and (info[2].receiver_name == expected_receiver_name3)
    )


@injection_test
def test_that_correct_info_for_receiver_is_generated_after_transaction_between_social_accounting_and_company(
    get_transaction_infos: GetTransactionInfos,
    company_generator: CompanyGenerator,
    transaction_generator: TransactionGenerator,
    transaction_repository: TransactionRepository,
    social_accounting: SocialAccounting,
):
    company = company_generator.create_company()

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
    assert info[0].sender_name == expected_sender_name
    assert info[0].receiver_name == expected_receiver_name
    assert info[0].transaction_volumes[AccountTypes.p.value] == expected_amount_p


@injection_test
def test_that_correct_info_for_company_is_generated_in_correct_order_after_several_transactions_of_different_kind(
    get_transaction_infos: GetTransactionInfos,
    company_generator: CompanyGenerator,
    transaction_generator: TransactionGenerator,
    member_generator: MemberGenerator,
    transaction_repository: TransactionRepository,
    social_accounting_generator: SocialAccountingGenerator,
):
    company1 = company_generator.create_company()
    company2 = company_generator.create_company()
    member = member_generator.create_member()
    social_accounting = social_accounting_generator.create_social_accounting()

    trans1 = transaction_generator.create_transaction(
        account_from=company1.means_account, account_to=company2.product_account
    )
    trans2 = transaction_generator.create_transaction(
        account_from=company2.means_account, account_to=company1.product_account
    )
    trans3 = transaction_generator.create_transaction(
        account_from=company1.means_account, account_to=company2.product_account
    )
    trans4 = transaction_generator.create_transaction(
        account_from=member.account, account_to=company1.product_account
    )
    trans5 = transaction_generator.create_transaction(
        account_from=social_accounting.account, account_to=company1.product_account
    )

    transaction_repository.add(trans1)
    transaction_repository.add(trans2)
    transaction_repository.add(trans3)
    transaction_repository.add(trans4)
    transaction_repository.add(trans5)

    info = get_transaction_infos(company1)
    assert len(info) == 5

    # trans1
    expected_sender_name = "Mir"
    expected_receiver_name = company2.name
    assert info[4].sender_name == expected_sender_name
    assert info[4].receiver_name == expected_receiver_name

    # trans2
    expected_sender_name = company2.name
    expected_receiver_name = "Mich"
    assert info[3].sender_name == expected_sender_name
    assert info[3].receiver_name == expected_receiver_name

    # trans3
    expected_sender_name = "Mir"
    expected_receiver_name = company2.name
    assert info[2].sender_name == expected_sender_name
    assert info[2].receiver_name == expected_receiver_name

    # trans4
    expected_sender_name = member.name
    expected_receiver_name = "Mich"
    assert info[1].sender_name == expected_sender_name
    assert info[1].receiver_name == expected_receiver_name

    # trans5
    expected_sender_name = "Öff. Buchhaltung"
    expected_receiver_name = "Mich"
    assert info[0].sender_name == expected_sender_name
    assert info[0].receiver_name == expected_receiver_name
