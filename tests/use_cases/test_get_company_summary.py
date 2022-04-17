from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from arbeitszeit.entities import ProductionCosts
from arbeitszeit.repositories import TransactionRepository
from arbeitszeit.use_cases import GetCompanySummary
from tests.data_generators import CompanyGenerator, PlanGenerator, TransactionGenerator

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
def test_returns_correct_sales_volume_of_zero_if_plan_is_public(
    get_company_summary: GetCompanySummary,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
):
    company = company_generator.create_company()
    plan_generator.create_plan(planner=company, is_public_service=True)
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
def test_returns_correct_deviation_if_plan_is_productive_with_costs_of_10_and_balance_of_10(
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
def test_returns_correct_deviation_if_plan_is_productive_with_costs_of_10_and_balance_of_minus_10(
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
    assert response.plan_details[0].deviation_relative == Decimal(-100)


@injection_test
def test_returns_correct_deviation_if_plan_is_productive_with_costs_of_10_and_balance_of_0(
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
def test_returns_correct_deviation_if_plan_is_public(
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
    assert response.plan_details[0].deviation_relative == Decimal(0)
