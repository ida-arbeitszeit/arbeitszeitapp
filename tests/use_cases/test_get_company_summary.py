from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from arbeitszeit.entities import ProductionCosts, SocialAccounting
from arbeitszeit.use_cases.get_company_summary import GetCompanySummary
from tests.data_generators import TransactionGenerator

from .base_test_case import BaseTestCase
from .repositories import TransactionRepository


class UseCaseTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.get_company_summary = self.injector.get(GetCompanySummary)
        self.transaction_repository = self.injector.get(TransactionRepository)
        self.social_accounting = self.injector.get(SocialAccounting)
        self.transaction_generator = self.injector.get(TransactionGenerator)

    def test_returns_none_when_company_does_not_exist(self) -> None:
        response = self.get_company_summary(uuid4())
        assert response is None

    def test_returns_id(self) -> None:
        company = self.company_generator.create_company()
        response = self.get_company_summary(company)
        assert response
        assert response.id == company

    def test_returns_name(self) -> None:
        company = self.company_generator.create_company(name="Company XYZ")
        response = self.get_company_summary(company)
        assert response
        assert response.name == "Company XYZ"

    def test_returns_email(self) -> None:
        company = self.company_generator.create_company(email="company@cp.org")
        response = self.get_company_summary(company)
        assert response
        assert response.email == "company@cp.org"

    def test_returns_register_date(self) -> None:
        expected_registration_date = datetime(2022, 1, 25)
        self.datetime_service.freeze_time(expected_registration_date)
        company = self.company_generator.create_company()
        self.datetime_service.freeze_time(datetime(2022, 1, 26))
        response = self.get_company_summary(company)
        assert response
        assert response.registered_on == expected_registration_date

    def test_returns_expectations_of_zero_when_no_transactions_took_place(self) -> None:
        company = self.company_generator.create_company()
        response = self.get_company_summary(company)
        assert response
        assert response.expectations.means == 0
        assert response.expectations.raw_material == 0
        assert response.expectations.work == 0
        assert response.expectations.product == 0

    def test_returns_correct_expectations_after_company_receives_credit_for_means_of_production(
        self,
    ) -> None:
        receiving_company = self.company_generator.create_company_entity()
        amount_transferred = Decimal(20)
        self.transaction_repository.create_transaction(
            date=datetime.min,
            sending_account=self.social_accounting.account.id,
            receiving_account=receiving_company.means_account,
            amount_sent=amount_transferred,
            amount_received=amount_transferred,
            purpose="test",
        )
        response = self.get_company_summary(receiving_company.id)
        assert response
        assert response.expectations.means == amount_transferred

    def test_returns_correct_expectations_after_company_receives_credit_for_raw_materials(
        self,
    ) -> None:
        receiving_company = self.company_generator.create_company_entity()
        amount_transferred = Decimal(20)
        self.transaction_repository.create_transaction(
            date=datetime.min,
            sending_account=self.social_accounting.account.id,
            receiving_account=receiving_company.raw_material_account,
            amount_sent=amount_transferred,
            amount_received=amount_transferred,
            purpose="test",
        )
        response = self.get_company_summary(receiving_company.id)
        assert response
        assert response.expectations.raw_material == amount_transferred

    def test_returns_correct_expectations_after_company_receives_credit_for_labour(
        self,
    ) -> None:
        receiving_company = self.company_generator.create_company_entity()
        amount_transferred = Decimal(20)
        self.transaction_repository.create_transaction(
            date=datetime.min,
            sending_account=self.social_accounting.account.id,
            receiving_account=receiving_company.work_account,
            amount_sent=amount_transferred,
            amount_received=amount_transferred,
            purpose="test",
        )
        response = self.get_company_summary(receiving_company.id)
        assert response
        assert response.expectations.work == amount_transferred

    def test_returns_correct_expectations_after_company_receives_negative_amount_on_prd_account_from_social_accounting(
        self,
    ) -> None:
        receiving_company = self.company_generator.create_company_entity()
        amount_transferred = Decimal(-20)
        self.transaction_repository.create_transaction(
            date=datetime.min,
            sending_account=self.social_accounting.account.id,
            receiving_account=receiving_company.product_account,
            amount_sent=amount_transferred,
            amount_received=amount_transferred,
            purpose="test",
        )
        response = self.get_company_summary(receiving_company.id)
        assert response
        assert response.expectations.product == amount_transferred

    def test_returns_correct_expectations_after_company_receives_positive_amount_on_prd_account_from_social_accounting(
        self,
    ) -> None:
        receiving_company = self.company_generator.create_company_entity()
        amount_transferred = Decimal(20)
        self.transaction_repository.create_transaction(
            date=datetime.min,
            sending_account=self.social_accounting.account.id,
            receiving_account=receiving_company.product_account,
            amount_sent=amount_transferred,
            amount_received=amount_transferred,
            purpose="test",
        )
        response = self.get_company_summary(receiving_company.id)
        assert response
        assert response.expectations.product == amount_transferred

    def test_returns_no_expectations_for_product_after_company_receives_amount_on_prd_account_from_another_company(
        self,
    ) -> None:
        receiving_company = self.company_generator.create_company_entity()
        amount_transferred = Decimal(20)
        self.transaction_repository.create_transaction(
            date=datetime.min,
            sending_account=self.company_generator.create_company_entity().work_account,
            receiving_account=receiving_company.product_account,
            amount_sent=amount_transferred,
            amount_received=amount_transferred,
            purpose="test",
        )
        response = self.get_company_summary(receiving_company.id)
        assert response
        assert response.expectations.product == 0

    def test_all_four_accounts_have_balance_of_zero(self) -> None:
        company = self.company_generator.create_company_entity()
        response = self.get_company_summary(company.id)
        assert response
        assert response.account_balances.means == 0
        assert response.account_balances.raw_material == 0
        assert response.account_balances.work == 0
        assert response.account_balances.product == 0

    def test_labour_account_shows_correct_balance_after_company_received_a_transaction(
        self,
    ) -> None:
        sending_company = self.company_generator.create_company_entity()
        receiving_company = self.company_generator.create_company_entity()
        amount_transferred = Decimal(10)
        self.transaction_repository.create_transaction(
            date=datetime.min,
            sending_account=sending_company.means_account,
            receiving_account=receiving_company.work_account,
            amount_sent=amount_transferred,
            amount_received=amount_transferred,
            purpose="test",
        )
        response = self.get_company_summary(receiving_company.id)
        assert response
        assert response.account_balances.work == amount_transferred
        assert response.account_balances.means == 0

    def test_show_relative_deviation_of_zero_for_all_accounts_when_no_transactions_took_place(
        self,
    ) -> None:
        company = self.company_generator.create_company_entity()
        response = self.get_company_summary(company.id)
        assert response
        for i in range(4):
            assert response.deviations_relative[i] == 0

    def test_show_relative_deviation_of_infinite_when_company_receives_minus_5_on_p_account(
        self,
    ) -> None:
        sending_company = self.company_generator.create_company_entity()
        receiving_company = self.company_generator.create_company_entity()
        amount_transferred = Decimal(-5)
        self.transaction_repository.create_transaction(
            date=datetime.min,
            sending_account=sending_company.means_account,
            receiving_account=receiving_company.means_account,
            amount_sent=amount_transferred,
            amount_received=amount_transferred,
            purpose="test",
        )
        response = self.get_company_summary(receiving_company.id)
        assert response
        assert response.deviations_relative[0] == Decimal("Infinity")
        assert response.deviations_relative[1] == 0

    def test_show_relative_deviation_of_100_after_social_accounting_sends_credit_to_p_account(
        self,
    ) -> None:
        receiving_company = self.company_generator.create_company_entity()
        amount_transferred = Decimal(5)
        self.transaction_repository.create_transaction(
            date=datetime.min,
            sending_account=self.social_accounting.account.id,
            receiving_account=receiving_company.means_account,
            amount_sent=amount_transferred,
            amount_received=amount_transferred,
            purpose="test",
        )
        response = self.get_company_summary(receiving_company.id)
        assert response
        assert response.deviations_relative[0] == Decimal(100)
        for i in range(1, 4):
            assert response.deviations_relative[i] == 0

    def test_show_relative_deviation_of_infinite_when_company_receives_minus_5_on_prd_account(
        self,
    ) -> None:
        sending_company = self.company_generator.create_company_entity()
        receiving_company = self.company_generator.create_company_entity()
        amount_transferred = Decimal(-5)
        self.transaction_repository.create_transaction(
            date=datetime.min,
            sending_account=sending_company.means_account,
            receiving_account=receiving_company.product_account,
            amount_sent=amount_transferred,
            amount_received=amount_transferred,
            purpose="test",
        )
        response = self.get_company_summary(receiving_company.id)
        assert response
        for i in range(0, 3):
            assert response.deviations_relative[i] == 0
        assert response.deviations_relative[3] == Decimal("Infinity")

    def test_show_relative_deviation_of_100_when_social_accounting_sends_minus_5_to_prd_account(
        self,
    ) -> None:
        receiving_company = self.company_generator.create_company_entity()
        amount_transferred = Decimal(-5)
        self.transaction_repository.create_transaction(
            date=datetime.min,
            sending_account=self.social_accounting.account.id,
            receiving_account=receiving_company.product_account,
            amount_sent=amount_transferred,
            amount_received=amount_transferred,
            purpose="test",
        )
        response = self.get_company_summary(receiving_company.id)
        assert response
        for i in range(3):
            assert response.deviations_relative[i] == 0
        assert response.deviations_relative[3] == Decimal(100)

    def test_show_relative_deviation_of_50_when_company_sells_half_of_expected_sales(
        self,
    ) -> None:
        company = self.company_generator.create_company_entity()
        expected_sales = Decimal(-10)
        self.transaction_repository.create_transaction(
            date=datetime.min,
            sending_account=self.social_accounting.account.id,
            receiving_account=company.product_account,
            amount_sent=expected_sales,
            amount_received=expected_sales,
            purpose="test",
        )
        buying_company = self.company_generator.create_company_entity()
        sales_value = Decimal(5)
        self.transaction_repository.create_transaction(
            date=datetime.min,
            sending_account=buying_company.product_account,
            receiving_account=company.product_account,
            amount_sent=sales_value,
            amount_received=sales_value,
            purpose="test",
        )

        response = self.get_company_summary(company.id)
        assert response
        for i in range(3):
            assert response.deviations_relative[i] == 0
        assert response.deviations_relative[3] == Decimal(50)

    def test_returns_empty_list_of_companys_plans_when_there_are_none(self) -> None:
        company = self.company_generator.create_company_entity()
        response = self.get_company_summary(company.id)
        assert response
        assert response.plan_details == []

    def test_returns_list_of_companys_plans_when_there_are_any(self) -> None:
        company = self.company_generator.create_company()
        self.plan_generator.create_plan(planner=company)
        self.plan_generator.create_plan(planner=company, approved=False)
        response = self.get_company_summary(company)
        assert response
        assert len(response.plan_details) == 2

    def test_returns_list_of_companys_plans_in_descending_order(self) -> None:
        company = self.company_generator.create_company()
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        third = self.plan_generator.create_plan(planner=company)
        self.datetime_service.freeze_time(
            self.datetime_service.now() - timedelta(days=9)
        )
        first = self.plan_generator.create_plan(planner=company)
        self.datetime_service.freeze_time(
            self.datetime_service.now() + timedelta(days=8)
        )
        second = self.plan_generator.create_plan(planner=company)
        self.datetime_service.freeze_time(datetime(2000, 1, 2))
        response = self.get_company_summary(company)
        assert response
        assert response.plan_details[0].id == third.id
        assert response.plan_details[1].id == second.id
        assert response.plan_details[2].id == first.id

    def test_returns_correct_sales_volume_of_zero_if_plan_is_public(self) -> None:
        company = self.company_generator.create_company()
        self.plan_generator.create_plan(
            planner=company,
            is_public_service=True,
            costs=ProductionCosts(Decimal(2), Decimal(2), Decimal(2)),
        )
        response = self.get_company_summary(company)
        assert response
        assert response.plan_details[0].sales_volume == 0

    def test_returns_correct_sales_volume_if_plan_is_productive(self) -> None:
        company = self.company_generator.create_company()
        self.plan_generator.create_plan(
            planner=company,
            costs=ProductionCosts(Decimal(2), Decimal(2), Decimal(2)),
        )
        response = self.get_company_summary(company)
        assert response
        assert response.plan_details[0].sales_volume == Decimal(6)

    def test_returns_correct_sales_balance_if_plan_is_productive_and_no_transactions_took_place(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        self.plan_generator.create_plan(
            planner=company, costs=ProductionCosts(Decimal(1), Decimal(1), Decimal(1))
        )
        response = self.get_company_summary(company)
        assert response
        assert response.plan_details[0].sales_balance == Decimal("-3")

    def test_returns_correct_sales_balance_if_plan_is_productive_and_one_transaction_took_place(
        self,
    ) -> None:
        company = self.company_generator.create_company_entity()
        plan = self.plan_generator.create_plan(
            planner=company.id,
            costs=ProductionCosts(Decimal(1), Decimal(1), Decimal(1)),
        )
        self.transaction_generator.create_transaction(
            receiving_account=company.product_account,
            amount_received=Decimal(15),
            purpose=f"Plan ID: {plan.id}",
        )
        response = self.get_company_summary(company.id)
        assert response
        assert response.plan_details[0].sales_balance == Decimal(12)

    def test_returns_correct_infinite_sales_deviation_if_plan_is_productive_with_costs_of_0_and_balance_of_1(
        self,
    ) -> None:
        company = self.company_generator.create_company_entity()
        plan = self.plan_generator.create_plan(
            planner=company.id,
            costs=ProductionCosts(Decimal(0), Decimal(0), Decimal(0)),
        )
        self.transaction_generator.create_transaction(
            receiving_account=company.product_account,
            amount_received=Decimal(1),
            purpose=f"Plan ID: {plan.id}",
        )
        response = self.get_company_summary(company.id)
        assert response
        assert response.plan_details[0].deviation_relative == Decimal("Infinity")

    def test_returns_correct_sales_deviation_of_100_if_plan_is_productive_with_costs_of_10_and_balance_of_10(
        self,
    ) -> None:
        company = self.company_generator.create_company_entity()
        plan = self.plan_generator.create_plan(
            planner=company.id,
            costs=ProductionCosts(Decimal(5), Decimal(5), Decimal(0)),
        )
        self.transaction_generator.create_transaction(
            receiving_account=company.product_account,
            amount_received=Decimal(20),
            purpose=f"Plan ID: {plan.id}",
        )
        response = self.get_company_summary(company.id)
        assert response
        assert response.plan_details[0].deviation_relative == Decimal(100)

    def test_returns_correct_sales_deviation_of_100_if_plan_is_productive_with_costs_of_10_and_balance_of_minus_10(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        self.plan_generator.create_plan(
            planner=company,
            costs=ProductionCosts(Decimal(5), Decimal(5), Decimal(0)),
        )
        response = self.get_company_summary(company)
        assert response
        assert response.plan_details[0].deviation_relative == Decimal(100)

    def test_returns_correct_sales_deviation_of_0_if_plan_is_productive_with_costs_of_10_and_balance_of_0(
        self,
    ) -> None:
        company = self.company_generator.create_company_entity()
        plan = self.plan_generator.create_plan(
            planner=company.id,
            costs=ProductionCosts(Decimal(5), Decimal(5), Decimal(0)),
        )
        self.transaction_generator.create_transaction(
            receiving_account=company.product_account,
            amount_received=Decimal(10),
            purpose=f"Plan ID: {plan.id}",
        )
        response = self.get_company_summary(company.id)
        assert response
        assert response.plan_details[0].deviation_relative == Decimal(0)

    def test_returns_correct_sales_deviation_of_infinite_if_plan_is_public_but_received_transaction_on_prd(
        self,
    ) -> None:
        company = self.company_generator.create_company_entity()
        plan = self.plan_generator.create_plan(
            planner=company.id,
            is_public_service=True,
            costs=ProductionCosts(Decimal(5), Decimal(5), Decimal(0)),
        )
        self.transaction_generator.create_transaction(
            receiving_account=company.product_account,
            amount_received=Decimal(10),
            purpose=f"Plan ID: {plan.id}",
        )
        response = self.get_company_summary(company.id)
        assert response
        assert response.plan_details[0].deviation_relative == Decimal("Infinity")

    def test_returns_correct_sales_deviation_of_0_if_plan_is_public_with_balance_of_0(
        self,
    ) -> None:
        company = self.company_generator.create_company_entity()
        plan = self.plan_generator.create_plan(
            planner=company.id,
            is_public_service=True,
            costs=ProductionCosts(Decimal(5), Decimal(5), Decimal(0)),
        )
        self.transaction_generator.create_transaction(
            receiving_account=company.product_account,
            amount_received=Decimal(0),
            purpose=f"Plan ID: {plan.id}",
        )
        response = self.get_company_summary(company.id)
        assert response
        assert response.plan_details[0].deviation_relative == Decimal("0")

    def test_that_empty_list_of_suppliers_is_returned_when_company_did_not_purchase_anything(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        response = self.get_company_summary(company)
        assert response
        assert not response.suppliers_ordered_by_volume

    def test_that_list_of_suppliers_contains_one_supplier_when_company_did_one_purchase(
        self,
    ) -> None:
        company = self.company_generator.create_company_entity()
        self.purchase_generator.create_purchase_by_company(buyer=company)
        response = self.get_company_summary(company.id)
        assert response
        assert len(response.suppliers_ordered_by_volume) == 1

    def test_that_list_of_suppliers_contains_one_supplier_when_company_did_two_purchases_from_same_supplier(
        self,
    ) -> None:
        buyer = self.company_generator.create_company_entity()
        seller = self.company_generator.create_company_entity()
        plan1 = self.plan_generator.create_plan(planner=seller.id)
        plan2 = self.plan_generator.create_plan(planner=seller.id)
        self.purchase_generator.create_purchase_by_company(buyer=buyer, plan=plan1)
        self.purchase_generator.create_purchase_by_company(buyer=buyer, plan=plan2)
        response = self.get_company_summary(buyer.id)
        assert response
        assert len(response.suppliers_ordered_by_volume) == 1

    def test_that_list_of_suppliers_contains_two_supplier_when_company_did_two_purchases_from_different_suppliers(
        self,
    ) -> None:
        buyer = self.company_generator.create_company_entity()
        self.company_generator.create_company_entity()
        self.purchase_generator.create_purchase_by_company(buyer=buyer)
        self.purchase_generator.create_purchase_by_company(buyer=buyer)
        response = self.get_company_summary(buyer.id)
        assert response
        assert len(response.suppliers_ordered_by_volume) == 2

    def test_that_correct_supplier_id_is_shown(self) -> None:
        buyer = self.company_generator.create_company_entity()
        supplier = self.company_generator.create_company_entity()
        offered_plan = self.plan_generator.create_plan(planner=supplier.id)
        self.purchase_generator.create_purchase_by_company(
            buyer=buyer, plan=offered_plan
        )
        response = self.get_company_summary(buyer.id)
        assert response
        assert response.suppliers_ordered_by_volume[0].company_id == supplier.id

    def test_that_correct_supplier_name_is_shown(self) -> None:
        buyer = self.company_generator.create_company_entity()
        supplier_name = "supplier coop"
        supplier = self.company_generator.create_company_entity(name=supplier_name)
        offered_plan = self.plan_generator.create_plan(planner=supplier.id)
        self.purchase_generator.create_purchase_by_company(
            buyer=buyer, plan=offered_plan
        )
        response = self.get_company_summary(buyer.id)
        assert response
        assert response.suppliers_ordered_by_volume[0].company_name == supplier_name

    def test_that_correct_volume_of_sale_of_supplier_is_calculated_after_one_purchase(
        self,
    ) -> None:
        company = self.company_generator.create_company_entity()
        self.purchase_generator.create_purchase_by_company(
            buyer=company, price_per_unit=Decimal("8.5"), amount=1
        )
        response = self.get_company_summary(company.id)
        assert response
        assert response.suppliers_ordered_by_volume[0].volume_of_sales == Decimal("8.5")

    def test_that_correct_volume_of_sale_of_supplier_is_calculated_after_two_purchases_from_same_supplier(
        self,
    ) -> None:
        buyer = self.company_generator.create_company_entity()
        seller = self.company_generator.create_company_entity()
        plan1 = self.plan_generator.create_plan(planner=seller.id)
        plan2 = self.plan_generator.create_plan(planner=seller.id)
        self.purchase_generator.create_purchase_by_company(
            buyer=buyer, plan=plan1, price_per_unit=Decimal("8.5"), amount=1
        )
        self.purchase_generator.create_purchase_by_company(
            buyer=buyer, plan=plan2, price_per_unit=Decimal("5"), amount=2
        )
        response = self.get_company_summary(buyer.id)
        assert response
        assert response.suppliers_ordered_by_volume[0].volume_of_sales == Decimal(
            "18.5"
        )

    def test_that_supplier_with_highest_sales_volume_is_listed_before_other_suppliers(
        self,
    ) -> None:
        buyer = self.company_generator.create_company_entity()
        top_supplier_plan = self.plan_generator.create_plan()
        medium_supplier_plan = self.plan_generator.create_plan()
        low_supplier_plan = self.plan_generator.create_plan()
        self.purchase_generator.create_purchase_by_company(
            buyer=buyer, amount=1, plan=low_supplier_plan
        )
        self.purchase_generator.create_purchase_by_company(
            buyer=buyer, amount=20, plan=top_supplier_plan
        )
        self.purchase_generator.create_purchase_by_company(
            buyer=buyer, amount=10, plan=medium_supplier_plan
        )
        response = self.get_company_summary(buyer.id)
        assert response
        assert (
            response.suppliers_ordered_by_volume[0].company_id
            == top_supplier_plan.planner
        )
        assert (
            response.suppliers_ordered_by_volume[1].company_id
            == medium_supplier_plan.planner
        )
        assert (
            response.suppliers_ordered_by_volume[2].company_id
            == low_supplier_plan.planner
        )

    def test_that_correct_volumes_of_sale_of_suppliers_are_calculated_after_two_purchases_from_different_suppliers(
        self,
    ) -> None:
        buyer = self.company_generator.create_company_entity()
        plan1 = self.plan_generator.create_plan()
        plan2 = self.plan_generator.create_plan()
        self.purchase_generator.create_purchase_by_company(
            buyer=buyer, plan=plan1, price_per_unit=Decimal("8.5"), amount=1
        )
        self.purchase_generator.create_purchase_by_company(
            buyer=buyer, plan=plan2, price_per_unit=Decimal("5"), amount=2
        )
        response = self.get_company_summary(buyer.id)
        assert response
        assert response.suppliers_ordered_by_volume[0].volume_of_sales == Decimal("10")
        assert response.suppliers_ordered_by_volume[1].volume_of_sales == Decimal("8.5")
