from datetime import datetime
from decimal import Decimal

from arbeitszeit.entities import SocialAccounting
from arbeitszeit.transactions import TransactionTypes
from arbeitszeit.use_cases import GetAccountP
from tests.data_generators import (
    CompanyGenerator,
    MemberGenerator,
    TransactionGenerator,
)

from .dependency_injection import injection_test


@injection_test
def test_no_transactions_returned_when_no_transactions_took_place(
    get_account_p: GetAccountP,
    member_generator: MemberGenerator,
    company_generator: CompanyGenerator,
):
    member_generator.create_member()
    company = company_generator.create_company()

    response = get_account_p(company.id)
    assert not response.transactions


@injection_test
def test_balance_is_zero_when_no_transactions_took_place(
    get_account_p: GetAccountP,
    member_generator: MemberGenerator,
    company_generator: CompanyGenerator,
):
    member_generator.create_member()
    company = company_generator.create_company()

    response = get_account_p(company.id)
    assert response.account_balance == 0


@injection_test
def test_that_no_info_is_generated_after_selling_of_consumer_product(
    get_account_p: GetAccountP,
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

    response = get_account_p(company.id)
    assert len(response.transactions) == 0


@injection_test
def test_that_no_info_is_generated_when_company_sells_p(
    get_account_p: GetAccountP,
    company_generator: CompanyGenerator,
    transaction_generator: TransactionGenerator,
):
    company1 = company_generator.create_company()
    company2 = company_generator.create_company()

    transaction_generator.create_transaction(
        sending_account=company1.means_account,
        receiving_account=company2.product_account,
        amount_sent=Decimal(10),
        amount_received=Decimal(8.5),
    )

    response = get_account_p(company2.id)
    assert not response.transactions


@injection_test
def test_that_no_info_is_generated_when_credit_for_r_is_granted(
    get_account_p: GetAccountP,
    company_generator: CompanyGenerator,
    transaction_generator: TransactionGenerator,
    social_accounting: SocialAccounting,
):
    company = company_generator.create_company()

    transaction_generator.create_transaction(
        sending_account=social_accounting.account,
        receiving_account=company.raw_material_account,
        amount_sent=Decimal(10),
        amount_received=Decimal(8.5),
    )

    response = get_account_p(company.id)
    assert len(response.transactions) == 0


@injection_test
def test_that_correct_info_is_generated_when_credit_for_p_is_granted(
    get_account_p: GetAccountP,
    company_generator: CompanyGenerator,
    transaction_generator: TransactionGenerator,
    social_accounting: SocialAccounting,
):
    company = company_generator.create_company()

    transaction_generator.create_transaction(
        sending_account=social_accounting.account,
        receiving_account=company.means_account,
        amount_sent=Decimal(10),
        amount_received=Decimal(8.5),
    )

    response = get_account_p(company.id)
    assert len(response.transactions) == 1
    assert response.transactions[0].transaction_volume == Decimal(8.5)
    assert response.transactions[0].purpose is not None
    assert isinstance(response.transactions[0].date, datetime)
    assert (
        response.transactions[0].type_of_transaction
        == TransactionTypes.credit_for_fixed_means
    )
    assert response.account_balance == Decimal(8.5)


@injection_test
def test_that_correct_info_for_is_generated_after_company_buying_p(
    get_account_p: GetAccountP,
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

    response = get_account_p(company1.id)
    transaction = response.transactions[0]
    assert transaction.type_of_transaction == TransactionTypes.payment_of_fixed_means
    assert transaction.transaction_volume == -trans.amount_sent
    assert response.account_balance == -trans.amount_sent
