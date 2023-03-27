from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from arbeitszeit.entities import ProductionCosts
from arbeitszeit.use_cases.get_company_summary import GetCompanySummary
from arbeitszeit.use_cases.update_plans_and_payout import UpdatePlansAndPayout

from ..base_test_case import BaseTestCase


class UseCaseTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.get_company_summary = self.injector.get(GetCompanySummary)
        self.payout = self.injector.get(UpdatePlansAndPayout)

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

    def test_without_any_plans_or_purchases_account_balances_must_be_zero(self) -> None:
        company = self.company_generator.create_company_entity()
        response = self.get_company_summary(company.id)
        assert response
        assert response.account_balances.means == 0
        assert response.account_balances.raw_material == 0
        assert response.account_balances.work == 0
        assert response.account_balances.product == 0

    def test_labour_account_shows_planned_labour_certs_after_plan_expired_and_no_workers_were_paid(
        self,
    ) -> None:
        self.datetime_service.freeze_time(datetime(2000, 2, 1))
        expected_amount = Decimal(12)
        company = self.company_generator.create_company()
        self.plan_generator.create_plan(
            costs=ProductionCosts(
                means_cost=Decimal(0),
                resource_cost=Decimal(0),
                labour_cost=expected_amount,
            ),
            timeframe=1,
            planner=company,
        )
        self.datetime_service.advance_time(timedelta(days=2))
        self.payout()
        response = self.get_company_summary(company)
        assert response
        assert response.account_balances.work == expected_amount

    def test_returns_empty_list_of_companys_plans_when_there_are_none(self) -> None:
        company = self.company_generator.create_company()
        response = self.get_company_summary(company)
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

    def test_show_sales_balance_of_half_production_costs_if_one_of_two_units_were_sold(
        self,
    ) -> None:
        costs = ProductionCosts(Decimal(1), Decimal(1), Decimal(1))
        company = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(
            planner=company,
            costs=costs,
            amount=2,
        )
        self.purchase_generator.create_fixed_means_purchase(plan=plan.id)
        response = self.get_company_summary(company)
        assert response
        assert response.plan_details[0].sales_balance == -costs.total_cost() / 2

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
        company = self.company_generator.create_company()
        self.purchase_generator.create_resource_purchase_by_company(buyer=company)
        response = self.get_company_summary(company)
        assert response
        assert len(response.suppliers_ordered_by_volume) == 1

    def test_that_list_of_suppliers_contains_one_supplier_when_company_did_two_purchases_from_same_supplier(
        self,
    ) -> None:
        buyer = self.company_generator.create_company_entity()
        seller = self.company_generator.create_company_entity()
        plan1 = self.plan_generator.create_plan(planner=seller.id)
        plan2 = self.plan_generator.create_plan(planner=seller.id)
        self.purchase_generator.create_resource_purchase_by_company(
            buyer=buyer.id, plan=plan1.id
        )
        self.purchase_generator.create_resource_purchase_by_company(
            buyer=buyer.id, plan=plan2.id
        )
        response = self.get_company_summary(buyer.id)
        assert response
        assert len(response.suppliers_ordered_by_volume) == 1

    def test_that_list_of_suppliers_contains_two_supplier_when_company_did_two_purchases_from_different_suppliers(
        self,
    ) -> None:
        buyer = self.company_generator.create_company_entity()
        self.company_generator.create_company_entity()
        self.purchase_generator.create_resource_purchase_by_company(buyer=buyer.id)
        self.purchase_generator.create_resource_purchase_by_company(buyer=buyer.id)
        response = self.get_company_summary(buyer.id)
        assert response
        assert len(response.suppliers_ordered_by_volume) == 2

    def test_that_correct_supplier_id_is_shown(self) -> None:
        buyer = self.company_generator.create_company_entity()
        supplier = self.company_generator.create_company_entity()
        offered_plan = self.plan_generator.create_plan(planner=supplier.id).id
        self.purchase_generator.create_resource_purchase_by_company(
            buyer=buyer.id, plan=offered_plan
        )
        response = self.get_company_summary(buyer.id)
        assert response
        assert response.suppliers_ordered_by_volume[0].company_id == supplier.id

    def test_that_correct_supplier_name_is_shown(self) -> None:
        buyer = self.company_generator.create_company_entity()
        supplier_name = "supplier coop"
        supplier = self.company_generator.create_company_entity(name=supplier_name)
        offered_plan = self.plan_generator.create_plan(planner=supplier.id)
        self.purchase_generator.create_resource_purchase_by_company(
            buyer=buyer.id, plan=offered_plan.id
        )
        response = self.get_company_summary(buyer.id)
        assert response
        assert response.suppliers_ordered_by_volume[0].company_name == supplier_name

    def test_that_correct_volume_of_sale_of_supplier_is_calculated_after_one_purchase(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan(
            costs=ProductionCosts(
                labour_cost=Decimal(1),
                means_cost=Decimal(2),
                resource_cost=Decimal(3),
            ),
            amount=1,
        )
        company = self.company_generator.create_company_entity()
        self.purchase_generator.create_resource_purchase_by_company(
            buyer=company.id, plan=plan.id, amount=1
        )
        response = self.get_company_summary(company.id)
        assert response
        assert response.suppliers_ordered_by_volume[0].volume_of_sales == Decimal("6")

    def test_that_correct_volume_of_sale_of_supplier_is_calculated_after_two_purchases_from_same_supplier(
        self,
    ) -> None:
        buyer = self.company_generator.create_company_entity()
        seller = self.company_generator.create_company_entity()
        plan1 = self.plan_generator.create_plan(
            planner=seller.id,
            costs=ProductionCosts(Decimal(1), Decimal(1), Decimal(1)),
            amount=1,
        )
        plan2 = self.plan_generator.create_plan(
            planner=seller.id,
            costs=ProductionCosts(Decimal(4), Decimal(5), Decimal(6)),
            amount=1,
        )
        self.purchase_generator.create_resource_purchase_by_company(
            buyer=buyer.id, plan=plan1.id, amount=1
        )
        self.purchase_generator.create_resource_purchase_by_company(
            buyer=buyer.id, plan=plan2.id, amount=1
        )
        response = self.get_company_summary(buyer.id)
        assert response
        assert response.suppliers_ordered_by_volume[0].volume_of_sales == Decimal("18")

    def test_that_supplier_with_highest_sales_volume_is_listed_before_other_suppliers(
        self,
    ) -> None:
        buyer = self.company_generator.create_company_entity()
        top_supplier_plan = self.plan_generator.create_plan()
        medium_supplier_plan = self.plan_generator.create_plan()
        low_supplier_plan = self.plan_generator.create_plan()
        self.purchase_generator.create_resource_purchase_by_company(
            buyer=buyer.id, amount=1, plan=low_supplier_plan.id
        )
        self.purchase_generator.create_resource_purchase_by_company(
            buyer=buyer.id, amount=20, plan=top_supplier_plan.id
        )
        self.purchase_generator.create_resource_purchase_by_company(
            buyer=buyer.id, amount=10, plan=medium_supplier_plan.id
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
        plan1 = self.plan_generator.create_plan(
            costs=ProductionCosts(Decimal(1), Decimal(2), Decimal(3)),
            amount=1,
        )
        plan2 = self.plan_generator.create_plan(
            costs=ProductionCosts(Decimal(4), Decimal(5), Decimal(6)),
            amount=1,
        )
        self.purchase_generator.create_resource_purchase_by_company(
            buyer=buyer.id, plan=plan1.id, amount=1
        )
        self.purchase_generator.create_resource_purchase_by_company(
            buyer=buyer.id,
            plan=plan2.id,
            amount=1,
        )
        response = self.get_company_summary(buyer.id)
        assert response
        assert response.suppliers_ordered_by_volume[0].volume_of_sales == Decimal("15")
        assert response.suppliers_ordered_by_volume[1].volume_of_sales == Decimal("6")
