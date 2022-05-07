from datetime import datetime
from decimal import Decimal

from arbeitszeit.entities import SocialAccounting
from arbeitszeit.transactions import TransactionTypes
from arbeitszeit.use_cases import ShowPRDAccountDetails
from tests.data_generators import (
    CompanyGenerator,
    MemberGenerator,
    TransactionGenerator,
)

from .dependency_injection import injection_test


@injection_test
def test_no_transactions_returned_when_no_transactions_took_place(
    show_prd_account_details: ShowPRDAccountDetails,
    member_generator: MemberGenerator,
    company_generator: CompanyGenerator,
):
    member_generator.create_member()
    company = company_generator.create_company()

    response = show_prd_account_details(company.id)
    assert not response.transactions


@injection_test
def test_balance_is_zero_when_no_transactions_took_place(
    show_prd_account_details: ShowPRDAccountDetails,
    member_generator: MemberGenerator,
    company_generator: CompanyGenerator,
):
    member_generator.create_member()
    company = company_generator.create_company()

    response = show_prd_account_details(company.id)
    assert response.account_balance == 0


@injection_test
def test_company_id_is_returned(
    show_prd_account_details: ShowPRDAccountDetails,
    member_generator: MemberGenerator,
    company_generator: CompanyGenerator,
):
    member_generator.create_member()
    company = company_generator.create_company()

    response = show_prd_account_details(company.id)
    assert response.company_id == company.id


@injection_test
def test_that_no_info_is_generated_after_company_buying_p(
    show_prd_account_details: ShowPRDAccountDetails,
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

    response = show_prd_account_details(company1.id)
    assert len(response.transactions) == 0


@injection_test
def test_that_no_info_is_generated_after_company_buying_r(
    show_prd_account_details: ShowPRDAccountDetails,
    company_generator: CompanyGenerator,
    transaction_generator: TransactionGenerator,
):
    company1 = company_generator.create_company()
    company2 = company_generator.create_company()

    transaction_generator.create_transaction(
        sending_account=company1.raw_material_account,
        receiving_account=company2.product_account,
        amount_sent=Decimal(10),
        amount_received=Decimal(8.5),
    )

    response = show_prd_account_details(company1.id)
    assert len(response.transactions) == 0


@injection_test
def test_that_no_info_is_generated_when_credit_for_r_is_granted(
    show_prd_account_details: ShowPRDAccountDetails,
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
    response = show_prd_account_details(company.id)
    assert len(response.transactions) == 0


@injection_test
def test_that_no_info_is_generated_when_credit_for_p_is_granted(
    show_prd_account_details: ShowPRDAccountDetails,
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
    response = show_prd_account_details(company.id)
    assert len(response.transactions) == 0


@injection_test
def test_that_no_info_is_generated_when_credit_for_a_is_granted(
    show_prd_account_details: ShowPRDAccountDetails,
    company_generator: CompanyGenerator,
    transaction_generator: TransactionGenerator,
    social_accounting: SocialAccounting,
):
    company = company_generator.create_company()

    transaction_generator.create_transaction(
        sending_account=social_accounting.account,
        receiving_account=company.work_account,
        amount_sent=Decimal(10),
        amount_received=Decimal(8.5),
    )
    response = show_prd_account_details(company.id)
    assert len(response.transactions) == 0


@injection_test
def test_that_correct_info_is_generated_after_selling_of_consumer_product(
    show_prd_account_details: ShowPRDAccountDetails,
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

    response = show_prd_account_details(company.id)
    assert len(response.transactions) == 1
    assert response.transactions[0].transaction_volume == Decimal(8.5)
    assert response.transactions[0].purpose is not None
    assert isinstance(response.transactions[0].date, datetime)
    assert (
        response.transactions[0].transaction_type
        == TransactionTypes.sale_of_consumer_product
    )
    assert response.account_balance == Decimal(8.5)


@injection_test
def test_that_correct_info_is_generated_after_selling_of_means_of_production(
    show_prd_account_details: ShowPRDAccountDetails,
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

    response = show_prd_account_details(company2.id)
    assert len(response.transactions) == 1
    assert response.transactions[0].transaction_volume == Decimal(8.5)
    assert response.transactions[0].purpose is not None
    assert isinstance(response.transactions[0].date, datetime)
    assert (
        response.transactions[0].transaction_type
        == TransactionTypes.sale_of_fixed_means
    )
    assert response.account_balance == Decimal(8.5)


@injection_test
def test_that_correct_info_is_generated_after_selling_of_raw_material(
    show_prd_account_details: ShowPRDAccountDetails,
    company_generator: CompanyGenerator,
    transaction_generator: TransactionGenerator,
):
    company1 = company_generator.create_company()
    company2 = company_generator.create_company()

    transaction_generator.create_transaction(
        sending_account=company1.raw_material_account,
        receiving_account=company2.product_account,
        amount_sent=Decimal(10),
        amount_received=Decimal(8.5),
    )

    response = show_prd_account_details(company2.id)
    assert len(response.transactions) == 1
    assert response.transactions[0].transaction_volume == Decimal(8.5)
    assert response.transactions[0].purpose is not None
    assert isinstance(response.transactions[0].date, datetime)
    assert (
        response.transactions[0].transaction_type
        == TransactionTypes.sale_of_liquid_means
    )
    assert response.account_balance == Decimal(8.5)


@injection_test
def test_that_plotting_info_is_empty_when_no_transactions_occurred(
    show_prd_account_details: ShowPRDAccountDetails,
    member_generator: MemberGenerator,
    company_generator: CompanyGenerator,
):
    member_generator.create_member()
    company = company_generator.create_company()

    response = show_prd_account_details(company.id)
    assert not response.plot.timestamps
    assert not response.plot.accumulated_volumes


@injection_test
def test_that_plotting_info_is_generated_after_selling_of_consumer_product(
    show_prd_account_details: ShowPRDAccountDetails,
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

    response = show_prd_account_details(company.id)
    assert response.plot.timestamps
    assert response.plot.accumulated_volumes


@injection_test
def test_that_correct_plotting_info_is_generated_after_selling_of_two_consumer_products(
    show_prd_account_details: ShowPRDAccountDetails,
    member_generator: MemberGenerator,
    company_generator: CompanyGenerator,
    transaction_generator: TransactionGenerator,
):
    member = member_generator.create_member()
    company = company_generator.create_company()

    trans1 = transaction_generator.create_transaction(
        sending_account=member.account,
        receiving_account=company.product_account,
        amount_sent=Decimal(10),
        amount_received=Decimal(5),
    )

    trans2 = transaction_generator.create_transaction(
        sending_account=member.account,
        receiving_account=company.product_account,
        amount_sent=Decimal(10),
        amount_received=Decimal(10),
    )

    response = show_prd_account_details(company.id)
    assert len(response.plot.timestamps) == 2
    assert len(response.plot.accumulated_volumes) == 2

    assert trans1.date in response.plot.timestamps
    assert trans2.date in response.plot.timestamps

    assert trans1.amount_received in response.plot.accumulated_volumes
    assert (
        trans1.amount_received + trans2.amount_received
    ) in response.plot.accumulated_volumes


@injection_test
def test_that_plotting_info_is_generated_in_the_correct_order_after_selling_of_three_consumer_products(
    show_prd_account_details: ShowPRDAccountDetails,
    member_generator: MemberGenerator,
    company_generator: CompanyGenerator,
    transaction_generator: TransactionGenerator,
):
    member = member_generator.create_member()
    company = company_generator.create_company()

    trans1 = transaction_generator.create_transaction(
        sending_account=member.account,
        receiving_account=company.product_account,
        amount_sent=Decimal(10),
        amount_received=Decimal(1),
    )

    trans2 = transaction_generator.create_transaction(
        sending_account=member.account,
        receiving_account=company.product_account,
        amount_sent=Decimal(10),
        amount_received=Decimal(2),
    )

    trans3 = transaction_generator.create_transaction(
        sending_account=member.account,
        receiving_account=company.product_account,
        amount_sent=Decimal(10),
        amount_received=Decimal(3),
    )

    response = show_prd_account_details(company.id)
    assert response.plot.timestamps[0] == trans1.date
    assert response.plot.timestamps[2] == trans3.date

    assert response.plot.accumulated_volumes[0] == trans1.amount_received
    assert response.plot.accumulated_volumes[2] == (
        trans1.amount_received + trans2.amount_received + trans3.amount_received
    )
