from datetime import datetime
from decimal import Decimal

from arbeitszeit.entities import AccountTypes, SocialAccounting
from arbeitszeit.use_cases import GetTransactionInfos
from tests.data_generators import (
    CompanyGenerator,
    MemberGenerator,
    SocialAccountingGenerator,
    TransactionGenerator,
)

from .dependency_injection import injection_test


@injection_test
def test_that_no_info_is_generated_when_no_transaction_took_place(
    get_transaction_infos: GetTransactionInfos,
    member_generator: MemberGenerator,
    company_generator: CompanyGenerator,
):
    member_generator.create_member()
    company = company_generator.create_company()

    info = get_transaction_infos(company)
    assert not info


@injection_test
def test_that_correct_info_is_generated_after_transaction_between_member_and_company(
    get_transaction_infos: GetTransactionInfos,
    member_generator: MemberGenerator,
    company_generator: CompanyGenerator,
    transaction_generator: TransactionGenerator,
):
    member = member_generator.create_member()
    company = company_generator.create_company()

    transaction_generator.create_transaction(
        sending_account=member.account,
        receiving_account=company.product_account,
        amount_sent=Decimal(10),
        amount_received=Decimal(8.5),
    )

    info_company = get_transaction_infos(company)
    assert len(info_company) == 1
    assert type(info_company[0].date) == datetime
    assert info_company[0].receiver_name == "Mich"
    assert info_company[0].transaction_volumes["prd"] == Decimal(8.5)


@injection_test
def test_that_correct_info_for_sender_is_generated_after_transaction_between_company_and_company(
    get_transaction_infos: GetTransactionInfos,
    company_generator: CompanyGenerator,
    transaction_generator: TransactionGenerator,
):
    company1 = company_generator.create_company()
    company2 = company_generator.create_company()

    trans = transaction_generator.create_transaction(
        sending_account=company1.means_account,
        receiving_account=company2.product_account,
        amount_sent=Decimal(10),
        amount_received=Decimal(8.5),
    )

    info_sender = get_transaction_infos(company1)
    assert info_sender[0].sender_name == "Mir"
    assert info_sender[0].receiver_name == company2.name
    assert (
        info_sender[0].transaction_volumes[AccountTypes.p.value] == -trans.amount_sent
    )


@injection_test
def test_that_correct_info_is_generated_when_the_same_company_is_sender_and_receiver(
    get_transaction_infos: GetTransactionInfos,
    company_generator: CompanyGenerator,
    transaction_generator: TransactionGenerator,
):
    company = company_generator.create_company()

    trans = transaction_generator.create_transaction(
        sending_account=company.means_account,
        receiving_account=company.product_account,
        amount_sent=Decimal(10),
        amount_received=Decimal(8.5),
    )

    info = get_transaction_infos(company)
    assert len(info) == 1
    assert info[0].sender_name == "Mir"
    assert info[0].receiver_name == "Mich"
    assert info[0].transaction_volumes[AccountTypes.p.value] == -trans.amount_sent
    assert info[0].transaction_volumes[AccountTypes.prd.value] == trans.amount_received


@injection_test
def test_that_correct_info_for_receiver_is_generated_after_transaction_between_company_and_company(
    get_transaction_infos: GetTransactionInfos,
    company_generator: CompanyGenerator,
    transaction_generator: TransactionGenerator,
):
    company1 = company_generator.create_company()
    company2 = company_generator.create_company()

    trans = transaction_generator.create_transaction(
        sending_account=company1.means_account,
        receiving_account=company2.product_account,
        amount_sent=Decimal(10),
        amount_received=Decimal(8.5),
    )

    info_receiver = get_transaction_infos(company2)
    assert info_receiver[0].sender_name == company1.name
    assert info_receiver[0].receiver_name == "Mich"
    assert (
        info_receiver[0].transaction_volumes[AccountTypes.prd.value]
        == trans.amount_received
    )


@injection_test
def test_that_correct_info_for_sender_is_generated_after_several_transactions_between_company_and_company(
    get_transaction_infos: GetTransactionInfos,
    company_generator: CompanyGenerator,
    transaction_generator: TransactionGenerator,
):
    company1 = company_generator.create_company()
    company2 = company_generator.create_company()

    transaction_generator.create_transaction(
        sending_account=company1.means_account,
        receiving_account=company2.product_account,
    )
    transaction_generator.create_transaction(
        sending_account=company2.means_account,
        receiving_account=company1.product_account,
    )
    transaction_generator.create_transaction(
        sending_account=company1.means_account,
        receiving_account=company2.product_account,
    )

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
    social_accounting: SocialAccounting,
):
    company = company_generator.create_company()

    trans = transaction_generator.create_transaction(
        sending_account=social_accounting.account,
        receiving_account=company.means_account,
        amount_sent=Decimal(10),
        amount_received=Decimal(8.5),
    )

    info_receiver = get_transaction_infos(company)
    assert info_receiver[0].sender_name == "Öff. Buchhaltung"
    assert info_receiver[0].receiver_name == "Mich"
    assert (
        info_receiver[0].transaction_volumes[AccountTypes.p.value]
        == trans.amount_received
    )


@injection_test
def test_that_correct_info_for_company_is_generated_in_correct_order_after_several_transactions_of_different_kind(
    get_transaction_infos: GetTransactionInfos,
    company_generator: CompanyGenerator,
    transaction_generator: TransactionGenerator,
    member_generator: MemberGenerator,
    social_accounting_generator: SocialAccountingGenerator,
):
    company1 = company_generator.create_company()
    company2 = company_generator.create_company()
    member = member_generator.create_member()
    social_accounting = social_accounting_generator.create_social_accounting()

    transaction_generator.create_transaction(
        sending_account=company1.means_account,
        receiving_account=company2.product_account,
    )
    transaction_generator.create_transaction(
        sending_account=company2.means_account,
        receiving_account=company1.product_account,
    )
    transaction_generator.create_transaction(
        sending_account=company1.means_account,
        receiving_account=company2.product_account,
    )
    transaction_generator.create_transaction(
        sending_account=member.account, receiving_account=company1.product_account
    )
    transaction_generator.create_transaction(
        sending_account=social_accounting.account,
        receiving_account=company1.product_account,
    )

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
