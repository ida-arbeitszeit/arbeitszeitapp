from datetime import datetime, timedelta
from decimal import Decimal

from arbeitszeit.entities import AccountTypes, SocialAccounting
from arbeitszeit.transactions import TransactionTypes
from arbeitszeit.use_cases import GetCompanyTransactions
from tests.data_generators import (
    CompanyGenerator,
    FakeDatetimeService,
    MemberGenerator,
    TransactionGenerator,
)

from .dependency_injection import injection_test


@injection_test
def test_that_no_info_is_generated_when_no_transaction_took_place(
    get_company_transactions: GetCompanyTransactions,
    member_generator: MemberGenerator,
    company_generator: CompanyGenerator,
):
    member_generator.create_member()
    company = company_generator.create_company_entity()

    info = get_company_transactions(company.id)
    assert not info.transactions


@injection_test
def test_that_correct_info_is_generated_after_transaction_of_member_buying_consumer_product(
    get_company_transactions: GetCompanyTransactions,
    member_generator: MemberGenerator,
    company_generator: CompanyGenerator,
    transaction_generator: TransactionGenerator,
):
    member = member_generator.create_member_entity()
    company = company_generator.create_company_entity()

    transaction_generator.create_transaction(
        sending_account=member.account,
        receiving_account=company.product_account,
        amount_sent=Decimal(10),
        amount_received=Decimal(8.5),
    )

    info_company = get_company_transactions(company.id)
    assert len(info_company.transactions) == 1
    transaction = info_company.transactions[0]
    assert type(transaction.date) == datetime
    assert transaction.transaction_type == TransactionTypes.sale_of_consumer_product
    assert transaction.transaction_volume == Decimal(8.5)
    assert transaction.account_type == AccountTypes.prd


@injection_test
def test_that_correct_info_for_sender_is_generated_after_transaction_of_company_buying_p(
    get_company_transactions: GetCompanyTransactions,
    company_generator: CompanyGenerator,
    transaction_generator: TransactionGenerator,
):
    company1 = company_generator.create_company_entity()
    company2 = company_generator.create_company_entity()

    trans = transaction_generator.create_transaction(
        sending_account=company1.means_account,
        receiving_account=company2.product_account,
        amount_sent=Decimal(10),
        amount_received=Decimal(8.5),
    )

    info_sender = get_company_transactions(company1.id)
    transaction = info_sender.transactions[0]
    assert transaction.transaction_type == TransactionTypes.payment_of_fixed_means
    assert transaction.transaction_volume == -trans.amount_sent
    assert transaction.account_type == AccountTypes.p


@injection_test
def test_that_correct_info_for_receiver_is_generated_after_transaction_of_company_buying_p(
    get_company_transactions: GetCompanyTransactions,
    company_generator: CompanyGenerator,
    transaction_generator: TransactionGenerator,
):
    company1 = company_generator.create_company_entity()
    company2 = company_generator.create_company_entity()

    trans = transaction_generator.create_transaction(
        sending_account=company1.means_account,
        receiving_account=company2.product_account,
        amount_sent=Decimal(10),
        amount_received=Decimal(8.5),
    )

    info_receiver = get_company_transactions(company2.id)
    transaction = info_receiver.transactions[0]
    assert transaction.transaction_type == TransactionTypes.sale_of_fixed_means
    assert transaction.transaction_volume == trans.amount_received
    assert transaction.account_type == AccountTypes.prd


@injection_test
def test_that_correct_info_for_company_is_generated_after_transaction_where_credit_for_p_is_granted(
    get_company_transactions: GetCompanyTransactions,
    company_generator: CompanyGenerator,
    transaction_generator: TransactionGenerator,
    social_accounting: SocialAccounting,
):
    company = company_generator.create_company_entity()

    trans = transaction_generator.create_transaction(
        sending_account=social_accounting.account.id,
        receiving_account=company.means_account,
        amount_sent=Decimal(10),
        amount_received=Decimal(8.5),
    )

    info_receiver = get_company_transactions(company.id)
    assert info_receiver.transactions[0].transaction_volume == trans.amount_received
    assert (
        info_receiver.transactions[0].transaction_type
        == TransactionTypes.credit_for_fixed_means
    )


@injection_test
def test_that_correct_info_for_company_is_generated_after_transaction_where_credit_for_r_is_granted(
    get_company_transactions: GetCompanyTransactions,
    company_generator: CompanyGenerator,
    transaction_generator: TransactionGenerator,
    social_accounting: SocialAccounting,
):
    company = company_generator.create_company_entity()

    trans = transaction_generator.create_transaction(
        sending_account=social_accounting.account.id,
        receiving_account=company.raw_material_account,
        amount_sent=Decimal(10),
        amount_received=Decimal(8.5),
    )

    info_receiver = get_company_transactions(company.id)
    assert info_receiver.transactions[0].transaction_volume == trans.amount_received
    assert (
        info_receiver.transactions[0].transaction_type
        == TransactionTypes.credit_for_liquid_means
    )


@injection_test
def test_that_correct_info_for_company_is_generated_after_transaction_where_credit_for_a_is_granted(
    get_company_transactions: GetCompanyTransactions,
    company_generator: CompanyGenerator,
    transaction_generator: TransactionGenerator,
    social_accounting: SocialAccounting,
):
    company = company_generator.create_company_entity()

    trans = transaction_generator.create_transaction(
        sending_account=social_accounting.account.id,
        receiving_account=company.work_account,
        amount_sent=Decimal(10),
        amount_received=Decimal(8.5),
    )

    info_receiver = get_company_transactions(company.id)
    assert info_receiver.transactions[0].transaction_volume == trans.amount_received
    assert (
        info_receiver.transactions[0].transaction_type
        == TransactionTypes.credit_for_wages
    )


@injection_test
def test_correct_info_is_generated_after_several_transactions_where_companies_buy_each_others_product(
    get_company_transactions: GetCompanyTransactions,
    company_generator: CompanyGenerator,
    transaction_generator: TransactionGenerator,
    datetime_service: FakeDatetimeService,
):
    company1 = company_generator.create_company_entity()
    company2 = company_generator.create_company_entity()

    transaction_generator.create_transaction(
        sending_account=company1.means_account,
        receiving_account=company2.product_account,
        date=datetime_service.now() - timedelta(hours=3),
    )
    transaction_generator.create_transaction(
        sending_account=company2.means_account,
        receiving_account=company1.product_account,
        date=datetime_service.now() - timedelta(hours=2),
    )
    transaction_generator.create_transaction(
        sending_account=company1.raw_material_account,
        receiving_account=company2.product_account,
        date=datetime_service.now() - timedelta(hours=1),
    )

    info_company1 = get_company_transactions(company1.id)
    assert len(info_company1.transactions) == 3

    trans1 = info_company1.transactions.pop()
    assert trans1.transaction_type == TransactionTypes.payment_of_fixed_means

    trans2 = info_company1.transactions.pop()
    assert trans2.transaction_type == TransactionTypes.sale_of_fixed_means

    trans3 = info_company1.transactions.pop()
    assert trans3.transaction_type == TransactionTypes.payment_of_liquid_means


@injection_test
def test_that_correct_info_for_company_is_generated_in_correct_order_after_several_transactions_of_different_kind(
    get_company_transactions: GetCompanyTransactions,
    company_generator: CompanyGenerator,
    transaction_generator: TransactionGenerator,
    member_generator: MemberGenerator,
    social_accounting: SocialAccounting,
    datetime_service: FakeDatetimeService,
):
    company1 = company_generator.create_company_entity()
    company2 = company_generator.create_company_entity()
    member = member_generator.create_member_entity()

    transaction_generator.create_transaction(
        sending_account=company1.means_account,
        receiving_account=company2.product_account,
        date=datetime_service.now() - timedelta(hours=5),
    )
    transaction_generator.create_transaction(
        sending_account=company2.means_account,
        receiving_account=company1.product_account,
        date=datetime_service.now() - timedelta(hours=4),
    )
    transaction_generator.create_transaction(
        sending_account=company1.raw_material_account,
        receiving_account=company2.product_account,
        date=datetime_service.now() - timedelta(hours=3),
    )
    transaction_generator.create_transaction(
        sending_account=member.account,
        receiving_account=company1.product_account,
        date=datetime_service.now() - timedelta(hours=2),
    )
    expected_trans5 = transaction_generator.create_transaction(
        sending_account=social_accounting.account.id,
        receiving_account=company1.product_account,
        date=datetime_service.now() - timedelta(hours=1),
    )

    info = get_company_transactions(company1.id)
    assert len(info.transactions) == 5

    # trans1
    trans1 = info.transactions.pop()
    assert trans1.transaction_type == TransactionTypes.payment_of_fixed_means

    # trans2
    trans2 = info.transactions.pop()
    assert trans2.transaction_type == TransactionTypes.sale_of_fixed_means

    # trans3
    trans3 = info.transactions.pop()
    assert trans3.transaction_type == TransactionTypes.payment_of_liquid_means

    # trans4
    trans4 = info.transactions.pop()
    assert trans4.transaction_type == TransactionTypes.sale_of_consumer_product

    # trans5
    trans5 = info.transactions.pop()
    assert trans5.transaction_type == TransactionTypes.expected_sales
    assert trans5.transaction_volume == expected_trans5.amount_received
