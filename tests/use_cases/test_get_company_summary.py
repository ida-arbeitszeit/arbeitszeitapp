from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from arbeitszeit.entities import ProductionCosts, SocialAccounting
from arbeitszeit.repositories import TransactionRepository
from arbeitszeit.use_cases import GetCompanySummary
from tests.data_generators import (
    CompanyGenerator,
    PlanGenerator,
    PurchaseGenerator,
    TransactionGenerator,
)
from tests.datetime_service import FakeDatetimeService

from .dependency_injection import injection_test


@injection_test
def test_returns_none_when_company_does_not_exist(
    get_company_summary: GetCompanySummary,
):
    response = get_company_summary(uuid4())
    assert response is None


@injection_test
def test_returns_id(
    get_company_summary: GetCompanySummary, company_generator: CompanyGenerator
):
    company = company_generator.create_company()
    response = get_company_summary(company.id)
    assert response
    assert response.id == company.id


@injection_test
def test_returns_name(
    get_company_summary: GetCompanySummary, company_generator: CompanyGenerator
):
    company = company_generator.create_company(name="Company XYZ")
    response = get_company_summary(company.id)
    assert response
    assert response.name == "Company XYZ"


@injection_test
def test_returns_email(
    get_company_summary: GetCompanySummary, company_generator: CompanyGenerator
):
    company = company_generator.create_company(email="company@cp.org")
    response = get_company_summary(company.id)
    assert response
    assert response.email == "company@cp.org"


@injection_test
def test_returns_register_date(
    get_company_summary: GetCompanySummary, company_generator: CompanyGenerator
):
    company = company_generator.create_company(registered_on=datetime(2022, 1, 25))
    response = get_company_summary(company.id)
    assert response
    assert response.registered_on == datetime(2022, 1, 25)


@injection_test
def test_returns_expectations_of_zero_when_no_transactions_took_place(
    get_company_summary: GetCompanySummary, company_generator: CompanyGenerator
):
    company = company_generator.create_company()
    response = get_company_summary(company.id)
    assert response
    assert response.expectations.means == 0
    assert response.expectations.raw_material == 0
    assert response.expectations.work == 0
    assert response.expectations.product == 0


@injection_test
def test_returns_correct_expectations_after_company_receives_credit_for_means_of_production(
    get_company_summary: GetCompanySummary,
    company_generator: CompanyGenerator,
    transaction_repository: TransactionRepository,
    social_accounting: SocialAccounting,
):
    receiving_company = company_generator.create_company()
    amount_transferred = Decimal(20)
    transaction_repository.create_transaction(
        date=datetime.min,
        sending_account=social_accounting.account,
        receiving_account=receiving_company.means_account,
        amount_sent=amount_transferred,
        amount_received=amount_transferred,
        purpose="test",
    )
    response = get_company_summary(receiving_company.id)
    assert response
    assert response.expectations.means == amount_transferred


@injection_test
def test_returns_correct_expectations_after_company_receives_credit_for_raw_materials(
    get_company_summary: GetCompanySummary,
    company_generator: CompanyGenerator,
    transaction_repository: TransactionRepository,
    social_accounting: SocialAccounting,
):
    receiving_company = company_generator.create_company()
    amount_transferred = Decimal(20)
    transaction_repository.create_transaction(
        date=datetime.min,
        sending_account=social_accounting.account,
        receiving_account=receiving_company.raw_material_account,
        amount_sent=amount_transferred,
        amount_received=amount_transferred,
        purpose="test",
    )
    response = get_company_summary(receiving_company.id)
    assert response
    assert response.expectations.raw_material == amount_transferred


@injection_test
def test_returns_correct_expectations_after_company_receives_credit_for_labour(
    get_company_summary: GetCompanySummary,
    company_generator: CompanyGenerator,
    transaction_repository: TransactionRepository,
    social_accounting: SocialAccounting,
):
    receiving_company = company_generator.create_company()
    amount_transferred = Decimal(20)
    transaction_repository.create_transaction(
        date=datetime.min,
        sending_account=social_accounting.account,
        receiving_account=receiving_company.work_account,
        amount_sent=amount_transferred,
        amount_received=amount_transferred,
        purpose="test",
    )
    response = get_company_summary(receiving_company.id)
    assert response
    assert response.expectations.work == amount_transferred


@injection_test
def test_returns_correct_expectations_after_company_receives_negative_amount_on_prd_account_from_social_accounting(
    get_company_summary: GetCompanySummary,
    company_generator: CompanyGenerator,
    transaction_repository: TransactionRepository,
    social_accounting: SocialAccounting,
):
    receiving_company = company_generator.create_company()
    amount_transferred = Decimal(-20)
    transaction_repository.create_transaction(
        date=datetime.min,
        sending_account=social_accounting.account,
        receiving_account=receiving_company.product_account,
        amount_sent=amount_transferred,
        amount_received=amount_transferred,
        purpose="test",
    )
    response = get_company_summary(receiving_company.id)
    assert response
    assert response.expectations.product == amount_transferred


@injection_test
def test_returns_correct_expectations_after_company_receives_positive_amount_on_prd_account_from_social_accounting(
    get_company_summary: GetCompanySummary,
    company_generator: CompanyGenerator,
    transaction_repository: TransactionRepository,
    social_accounting: SocialAccounting,
):
    receiving_company = company_generator.create_company()
    amount_transferred = Decimal(20)
    transaction_repository.create_transaction(
        date=datetime.min,
        sending_account=social_accounting.account,
        receiving_account=receiving_company.product_account,
        amount_sent=amount_transferred,
        amount_received=amount_transferred,
        purpose="test",
    )
    response = get_company_summary(receiving_company.id)
    assert response
    assert response.expectations.product == amount_transferred


@injection_test
def test_returns_no_expectations_for_product_after_company_receives_amount_on_prd_account_from_another_company(
    get_company_summary: GetCompanySummary,
    company_generator: CompanyGenerator,
    transaction_repository: TransactionRepository,
):
    receiving_company = company_generator.create_company()
    amount_transferred = Decimal(20)
    transaction_repository.create_transaction(
        date=datetime.min,
        sending_account=company_generator.create_company().work_account,
        receiving_account=receiving_company.product_account,
        amount_sent=amount_transferred,
        amount_received=amount_transferred,
        purpose="test",
    )
    response = get_company_summary(receiving_company.id)
    assert response
    assert response.expectations.product == 0


@injection_test
def test_all_four_accounts_have_balance_of_zero(
    get_company_summary: GetCompanySummary, company_generator: CompanyGenerator
):
    company = company_generator.create_company()
    response = get_company_summary(company.id)
    assert response
    assert response.account_balances.means == 0
    assert response.account_balances.raw_material == 0
    assert response.account_balances.work == 0
    assert response.account_balances.product == 0


@injection_test
def test_labour_account_shows_correct_balance_after_company_received_a_transaction(
    get_company_summary: GetCompanySummary,
    company_generator: CompanyGenerator,
    transaction_repository: TransactionRepository,
):
    sending_company = company_generator.create_company()
    receiving_company = company_generator.create_company()
    amount_transferred = Decimal(10)
    transaction_repository.create_transaction(
        date=datetime.min,
        sending_account=sending_company.means_account,
        receiving_account=receiving_company.work_account,
        amount_sent=amount_transferred,
        amount_received=amount_transferred,
        purpose="test",
    )
    response = get_company_summary(receiving_company.id)
    assert response
    assert response.account_balances.work == amount_transferred
    assert response.account_balances.means == 0


@injection_test
def test_show_relative_deviation_of_zero_for_all_accounts_when_no_transactions_took_place(
    get_company_summary: GetCompanySummary, company_generator: CompanyGenerator
):
    company = company_generator.create_company()
    response = get_company_summary(company.id)
    assert response
    for i in range(4):
        assert response.deviations_relative[i] == 0


@injection_test
def test_show_relative_deviation_of_infinite_when_company_receives_minus_5_on_p_account(
    get_company_summary: GetCompanySummary,
    company_generator: CompanyGenerator,
    transaction_repository: TransactionRepository,
):
    sending_company = company_generator.create_company()
    receiving_company = company_generator.create_company()
    amount_transferred = Decimal(-5)
    transaction_repository.create_transaction(
        date=datetime.min,
        sending_account=sending_company.means_account,
        receiving_account=receiving_company.means_account,
        amount_sent=amount_transferred,
        amount_received=amount_transferred,
        purpose="test",
    )
    response = get_company_summary(receiving_company.id)
    assert response
    assert response.deviations_relative[0] == Decimal("Infinity")
    assert response.deviations_relative[1] == 0


@injection_test
def test_show_relative_deviation_of_100_after_social_accounting_sends_credit_to_p_account(
    get_company_summary: GetCompanySummary,
    company_generator: CompanyGenerator,
    transaction_repository: TransactionRepository,
    social_accounting: SocialAccounting,
):
    receiving_company = company_generator.create_company()
    amount_transferred = Decimal(5)
    transaction_repository.create_transaction(
        date=datetime.min,
        sending_account=social_accounting.account,
        receiving_account=receiving_company.means_account,
        amount_sent=amount_transferred,
        amount_received=amount_transferred,
        purpose="test",
    )
    response = get_company_summary(receiving_company.id)
    assert response
    assert response.deviations_relative[0] == Decimal(100)
    for i in range(1, 4):
        assert response.deviations_relative[i] == 0


@injection_test
def test_show_relative_deviation_of_infinite_when_company_receives_minus_5_on_prd_account(
    get_company_summary: GetCompanySummary,
    company_generator: CompanyGenerator,
    transaction_repository: TransactionRepository,
):
    sending_company = company_generator.create_company()
    receiving_company = company_generator.create_company()
    amount_transferred = Decimal(-5)
    transaction_repository.create_transaction(
        date=datetime.min,
        sending_account=sending_company.means_account,
        receiving_account=receiving_company.product_account,
        amount_sent=amount_transferred,
        amount_received=amount_transferred,
        purpose="test",
    )
    response = get_company_summary(receiving_company.id)
    assert response
    for i in range(0, 3):
        assert response.deviations_relative[i] == 0
    assert response.deviations_relative[3] == Decimal("Infinity")


@injection_test
def test_show_relative_deviation_of_100_when_social_accounting_sends_minus_5_to_prd_account(
    get_company_summary: GetCompanySummary,
    company_generator: CompanyGenerator,
    transaction_repository: TransactionRepository,
    social_accounting: SocialAccounting,
):
    receiving_company = company_generator.create_company()
    amount_transferred = Decimal(-5)
    transaction_repository.create_transaction(
        date=datetime.min,
        sending_account=social_accounting.account,
        receiving_account=receiving_company.product_account,
        amount_sent=amount_transferred,
        amount_received=amount_transferred,
        purpose="test",
    )
    response = get_company_summary(receiving_company.id)
    assert response
    for i in range(3):
        assert response.deviations_relative[i] == 0
    assert response.deviations_relative[3] == Decimal(100)


@injection_test
def test_show_relative_deviation_of_50_when_company_sells_half_of_expected_sales(
    get_company_summary: GetCompanySummary,
    company_generator: CompanyGenerator,
    transaction_repository: TransactionRepository,
    social_accounting: SocialAccounting,
):
    company = company_generator.create_company()
    expected_sales = Decimal(-10)
    transaction_repository.create_transaction(
        date=datetime.min,
        sending_account=social_accounting.account,
        receiving_account=company.product_account,
        amount_sent=expected_sales,
        amount_received=expected_sales,
        purpose="test",
    )
    buying_company = company_generator.create_company()
    sales_value = Decimal(5)
    transaction_repository.create_transaction(
        date=datetime.min,
        sending_account=buying_company.product_account,
        receiving_account=company.product_account,
        amount_sent=sales_value,
        amount_received=sales_value,
        purpose="test",
    )

    response = get_company_summary(company.id)
    assert response
    for i in range(3):
        assert response.deviations_relative[i] == 0
    assert response.deviations_relative[3] == Decimal(50)


@injection_test
def test_returns_empty_list_of_companys_plans_when_there_are_none(
    get_company_summary: GetCompanySummary,
    company_generator: CompanyGenerator,
):
    company = company_generator.create_company()
    response = get_company_summary(company.id)
    assert response
    assert response.plan_details == []


@injection_test
def test_returns_list_of_companys_plans_when_there_are_any(
    get_company_summary: GetCompanySummary,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
):
    company = company_generator.create_company()
    plan_generator.create_plan(planner=company, activation_date=datetime.min)
    plan_generator.create_plan(planner=company, activation_date=None)
    response = get_company_summary(company.id)
    assert response
    assert len(response.plan_details) == 2


@injection_test
def test_returns_list_of_companys_plans_in_descending_order(
    get_company_summary: GetCompanySummary,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
):
    company = company_generator.create_company()
    third = plan_generator.create_plan(
        planner=company, plan_creation_date=datetime_service.now_minus_one_day()
    )
    first = plan_generator.create_plan(
        planner=company, plan_creation_date=datetime_service.now_minus_ten_days()
    )
    second = plan_generator.create_plan(
        planner=company, plan_creation_date=datetime_service.now_minus_two_days()
    )
    response = get_company_summary(company.id)
    assert response
    assert response.plan_details[0].id == third.id
    assert response.plan_details[1].id == second.id
    assert response.plan_details[2].id == first.id


@injection_test
def test_returns_correct_sales_volume_of_zero_if_plan_is_public(
    get_company_summary: GetCompanySummary,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
):
    company = company_generator.create_company()
    plan_generator.create_plan(
        planner=company,
        is_public_service=True,
        costs=ProductionCosts(Decimal(2), Decimal(2), Decimal(2)),
    )
    response = get_company_summary(company.id)
    assert response
    assert response.plan_details[0].sales_volume == 0


@injection_test
def test_returns_correct_sales_volume_if_plan_is_productive(
    get_company_summary: GetCompanySummary,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
):
    company = company_generator.create_company()
    plan_generator.create_plan(
        planner=company,
        costs=ProductionCosts(Decimal(2), Decimal(2), Decimal(2)),
    )
    response = get_company_summary(company.id)
    assert response
    assert response.plan_details[0].sales_volume == Decimal(6)


@injection_test
def test_returns_correct_sales_balance_if_plan_is_productive_and_no_transactions_took_place(
    get_company_summary: GetCompanySummary,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
):
    company = company_generator.create_company()
    plan_generator.create_plan(
        planner=company,
    )
    response = get_company_summary(company.id)
    assert response
    assert response.plan_details[0].sales_balance == Decimal(0)


@injection_test
def test_returns_correct_sales_balance_if_plan_is_productive_and_one_transaction_took_place(
    get_company_summary: GetCompanySummary,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
    transaction_generator: TransactionGenerator,
):
    company = company_generator.create_company()
    plan = plan_generator.create_plan(
        planner=company,
    )
    transaction_generator.create_transaction(
        receiving_account=company.product_account,
        amount_received=Decimal(15),
        purpose=f"Plan ID: {plan.id}",
    )
    response = get_company_summary(company.id)
    assert response
    assert response.plan_details[0].sales_balance == Decimal(15)


@injection_test
def test_returns_correct_infinite_sales_deviation_if_plan_is_productive_with_costs_of_0_and_balance_of_1(
    get_company_summary: GetCompanySummary,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
    transaction_generator: TransactionGenerator,
):
    company = company_generator.create_company()
    plan = plan_generator.create_plan(
        planner=company,
        costs=ProductionCosts(Decimal(0), Decimal(0), Decimal(0)),
    )
    transaction_generator.create_transaction(
        receiving_account=company.product_account,
        amount_received=Decimal(1),
        purpose=f"Plan ID: {plan.id}",
    )
    response = get_company_summary(company.id)
    assert response
    assert response.plan_details[0].deviation_relative == Decimal("Infinity")


@injection_test
def test_returns_correct_sales_deviation_of_100_if_plan_is_productive_with_costs_of_10_and_balance_of_10(
    get_company_summary: GetCompanySummary,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
    transaction_generator: TransactionGenerator,
):
    company = company_generator.create_company()
    plan = plan_generator.create_plan(
        planner=company,
        costs=ProductionCosts(Decimal(5), Decimal(5), Decimal(0)),
    )
    transaction_generator.create_transaction(
        receiving_account=company.product_account,
        amount_received=Decimal(10),
        purpose=f"Plan ID: {plan.id}",
    )
    response = get_company_summary(company.id)
    assert response
    assert response.plan_details[0].deviation_relative == Decimal(100)


@injection_test
def test_returns_correct_sales_deviation_of_100_if_plan_is_productive_with_costs_of_10_and_balance_of_minus_10(
    get_company_summary: GetCompanySummary,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
    transaction_generator: TransactionGenerator,
):
    company = company_generator.create_company()
    plan = plan_generator.create_plan(
        planner=company,
        costs=ProductionCosts(Decimal(5), Decimal(5), Decimal(0)),
    )
    transaction_generator.create_transaction(
        receiving_account=company.product_account,
        amount_received=Decimal(-10),
        purpose=f"Plan ID: {plan.id}",
    )
    response = get_company_summary(company.id)
    assert response
    assert response.plan_details[0].deviation_relative == Decimal(100)


@injection_test
def test_returns_correct_sales_deviation_of_0_if_plan_is_productive_with_costs_of_10_and_balance_of_0(
    get_company_summary: GetCompanySummary,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
):
    company = company_generator.create_company()
    plan_generator.create_plan(
        planner=company,
        costs=ProductionCosts(Decimal(5), Decimal(5), Decimal(0)),
    )
    response = get_company_summary(company.id)
    assert response
    assert response.plan_details[0].deviation_relative == Decimal(0)


@injection_test
def test_returns_correct_sales_deviation_of_infinite_if_plan_is_public_but_received_transaction_on_prd(
    get_company_summary: GetCompanySummary,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
    transaction_generator: TransactionGenerator,
):
    company = company_generator.create_company()
    plan = plan_generator.create_plan(
        planner=company,
        is_public_service=True,
        costs=ProductionCosts(Decimal(5), Decimal(5), Decimal(0)),
    )
    transaction_generator.create_transaction(
        receiving_account=company.product_account,
        amount_received=Decimal(10),
        purpose=f"Plan ID: {plan.id}",
    )
    response = get_company_summary(company.id)
    assert response
    assert response.plan_details[0].deviation_relative == Decimal("Infinity")


@injection_test
def test_returns_correct_sales_deviation_of_0_if_plan_is_public_with_balance_of_0(
    get_company_summary: GetCompanySummary,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
    transaction_generator: TransactionGenerator,
):
    company = company_generator.create_company()
    plan = plan_generator.create_plan(
        planner=company,
        is_public_service=True,
        costs=ProductionCosts(Decimal(5), Decimal(5), Decimal(0)),
    )
    transaction_generator.create_transaction(
        receiving_account=company.product_account,
        amount_received=Decimal(0),
        purpose=f"Plan ID: {plan.id}",
    )
    response = get_company_summary(company.id)
    assert response
    assert response.plan_details[0].deviation_relative == Decimal("0")


@injection_test
def test_that_empty_list_of_suppliers_is_returned_when_company_did_not_purchase_anything(
    get_company_summary: GetCompanySummary,
    company_generator: CompanyGenerator,
):
    company = company_generator.create_company()
    response = get_company_summary(company.id)
    assert response
    assert not response.suppliers_ordered_by_volume


@injection_test
def test_that_list_of_suppliers_contains_one_supplier_when_company_did_one_purchase(
    get_company_summary: GetCompanySummary,
    company_generator: CompanyGenerator,
    purchase_generator: PurchaseGenerator,
):
    company = company_generator.create_company()
    purchase_generator.create_purchase_by_company(buyer=company)
    response = get_company_summary(company.id)
    assert response
    assert len(response.suppliers_ordered_by_volume) == 1


@injection_test
def test_that_list_of_suppliers_contains_one_supplier_when_company_did_two_purchases_from_same_supplier(
    get_company_summary: GetCompanySummary,
    company_generator: CompanyGenerator,
    purchase_generator: PurchaseGenerator,
    plan_generator: PlanGenerator,
):
    buyer = company_generator.create_company()
    seller = company_generator.create_company()
    plan1 = plan_generator.create_plan(planner=seller)
    plan2 = plan_generator.create_plan(planner=seller)
    purchase_generator.create_purchase_by_company(buyer=buyer, plan=plan1)
    purchase_generator.create_purchase_by_company(buyer=buyer, plan=plan2)
    response = get_company_summary(buyer.id)
    assert response
    assert len(response.suppliers_ordered_by_volume) == 1


@injection_test
def test_that_list_of_suppliers_contains_two_supplier_when_company_did_two_purchases_from_different_suppliers(
    get_company_summary: GetCompanySummary,
    company_generator: CompanyGenerator,
    purchase_generator: PurchaseGenerator,
):
    buyer = company_generator.create_company()
    company_generator.create_company()
    purchase_generator.create_purchase_by_company(buyer=buyer)
    purchase_generator.create_purchase_by_company(buyer=buyer)
    response = get_company_summary(buyer.id)
    assert response
    assert len(response.suppliers_ordered_by_volume) == 2


@injection_test
def test_that_correct_supplier_id_is_shown(
    get_company_summary: GetCompanySummary,
    company_generator: CompanyGenerator,
    purchase_generator: PurchaseGenerator,
    plan_generator: PlanGenerator,
):
    buyer = company_generator.create_company()
    supplier = company_generator.create_company()
    offered_plan = plan_generator.create_plan(planner=supplier)
    purchase_generator.create_purchase_by_company(buyer=buyer, plan=offered_plan)
    response = get_company_summary(buyer.id)
    assert response
    assert response.suppliers_ordered_by_volume[0].company_id == supplier.id


@injection_test
def test_that_correct_supplier_name_is_shown(
    get_company_summary: GetCompanySummary,
    company_generator: CompanyGenerator,
    purchase_generator: PurchaseGenerator,
    plan_generator: PlanGenerator,
):
    buyer = company_generator.create_company()
    supplier = company_generator.create_company()
    offered_plan = plan_generator.create_plan(planner=supplier)
    purchase_generator.create_purchase_by_company(buyer=buyer, plan=offered_plan)
    response = get_company_summary(buyer.id)
    assert response
    assert response.suppliers_ordered_by_volume[0].company_name == supplier.name


@injection_test
def test_that_correct_volume_of_sale_of_supplier_is_calculated_after_one_purchase(
    get_company_summary: GetCompanySummary,
    company_generator: CompanyGenerator,
    purchase_generator: PurchaseGenerator,
):
    company = company_generator.create_company()
    purchase_generator.create_purchase_by_company(
        buyer=company, price_per_unit=Decimal("8.5"), amount=1
    )
    response = get_company_summary(company.id)
    assert response
    assert response.suppliers_ordered_by_volume[0].volume_of_sales == Decimal("8.5")


@injection_test
def test_that_correct_volume_of_sale_of_supplier_is_calculated_after_two_purchases_from_same_supplier(
    get_company_summary: GetCompanySummary,
    company_generator: CompanyGenerator,
    purchase_generator: PurchaseGenerator,
    plan_generator: PlanGenerator,
):
    buyer = company_generator.create_company()
    seller = company_generator.create_company()
    plan1 = plan_generator.create_plan(planner=seller)
    plan2 = plan_generator.create_plan(planner=seller)
    purchase_generator.create_purchase_by_company(
        buyer=buyer, plan=plan1, price_per_unit=Decimal("8.5"), amount=1
    )
    purchase_generator.create_purchase_by_company(
        buyer=buyer, plan=plan2, price_per_unit=Decimal("5"), amount=2
    )
    response = get_company_summary(buyer.id)
    assert response
    assert response.suppliers_ordered_by_volume[0].volume_of_sales == Decimal("18.5")


@injection_test
def test_that_supplier_with_highest_sales_volume_is_listed_before_other_suppliers(
    get_company_summary: GetCompanySummary,
    company_generator: CompanyGenerator,
    purchase_generator: PurchaseGenerator,
    plan_generator: PlanGenerator,
):
    buyer = company_generator.create_company()
    top_supplier_plan = plan_generator.create_plan()
    medium_supplier_plan = plan_generator.create_plan()
    low_supplier_plan = plan_generator.create_plan()
    purchase_generator.create_purchase_by_company(
        buyer=buyer, amount=1, plan=low_supplier_plan
    )
    purchase_generator.create_purchase_by_company(
        buyer=buyer, amount=20, plan=top_supplier_plan
    )
    purchase_generator.create_purchase_by_company(
        buyer=buyer, amount=10, plan=medium_supplier_plan
    )
    response = get_company_summary(buyer.id)
    assert response
    assert (
        response.suppliers_ordered_by_volume[0].company_id
        == top_supplier_plan.planner.id
    )
    assert (
        response.suppliers_ordered_by_volume[1].company_id
        == medium_supplier_plan.planner.id
    )
    assert (
        response.suppliers_ordered_by_volume[2].company_id
        == low_supplier_plan.planner.id
    )


@injection_test
def test_that_correct_volumes_of_sale_of_suppliers_are_calculated_after_two_purchases_from_different_suppliers(
    get_company_summary: GetCompanySummary,
    company_generator: CompanyGenerator,
    purchase_generator: PurchaseGenerator,
    plan_generator: PlanGenerator,
):
    buyer = company_generator.create_company()
    plan1 = plan_generator.create_plan()
    plan2 = plan_generator.create_plan()
    purchase_generator.create_purchase_by_company(
        buyer=buyer, plan=plan1, price_per_unit=Decimal("8.5"), amount=1
    )
    purchase_generator.create_purchase_by_company(
        buyer=buyer, plan=plan2, price_per_unit=Decimal("5"), amount=2
    )
    response = get_company_summary(buyer.id)
    assert response
    assert response.suppliers_ordered_by_volume[0].volume_of_sales == Decimal("10")
    assert response.suppliers_ordered_by_volume[1].volume_of_sales == Decimal("8.5")
