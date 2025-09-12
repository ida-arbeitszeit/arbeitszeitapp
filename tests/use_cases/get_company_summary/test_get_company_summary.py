from datetime import timedelta
from decimal import Decimal
from uuid import uuid4

from arbeitszeit.records import ProductionCosts
from arbeitszeit.use_cases.get_company_summary import GetCompanySummary
from tests.datetime_service import datetime_utc

from ..base_test_case import BaseTestCase


class UseCaseTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.get_company_summary = self.injector.get(GetCompanySummary)

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
        expected_registration_date = datetime_utc(2022, 1, 25)
        self.datetime_service.freeze_time(expected_registration_date)
        company = self.company_generator.create_company()
        self.datetime_service.freeze_time(datetime_utc(2022, 1, 26))
        response = self.get_company_summary(company)
        assert response
        assert response.registered_on == expected_registration_date

    def test_without_any_plans_or_consumptions_account_balances_must_be_zero(
        self,
    ) -> None:
        company = self.company_generator.create_company_record()
        response = self.get_company_summary(company.id)
        assert response
        assert response.account_balances.means == 0
        assert response.account_balances.raw_material == 0
        assert response.account_balances.work == 0
        assert response.account_balances.product == 0

    def test_labour_account_shows_planned_labour_certs_after_plan_expired_and_no_workers_were_paid(
        self,
    ) -> None:
        self.datetime_service.freeze_time(datetime_utc(2000, 2, 1))
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
        self.datetime_service.freeze_time(datetime_utc(2000, 1, 1))
        third = self.plan_generator.create_plan(planner=company)
        self.datetime_service.freeze_time(
            self.datetime_service.now() - timedelta(days=9)
        )
        first = self.plan_generator.create_plan(planner=company)
        self.datetime_service.freeze_time(
            self.datetime_service.now() + timedelta(days=8)
        )
        second = self.plan_generator.create_plan(planner=company)
        self.datetime_service.freeze_time(datetime_utc(2000, 1, 2))
        response = self.get_company_summary(company)
        assert response
        assert response.plan_details[0].id == third
        assert response.plan_details[1].id == second
        assert response.plan_details[2].id == first

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

    def test_that_empty_list_of_suppliers_is_returned_when_company_did_not_consume_anything(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        response = self.get_company_summary(company)
        assert response
        assert not response.suppliers_ordered_by_volume

    def test_that_list_of_suppliers_contains_one_supplier_when_company_did_one_productive_consumption(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=company
        )
        response = self.get_company_summary(company)
        assert response
        assert len(response.suppliers_ordered_by_volume) == 1

    def test_that_list_of_suppliers_contains_one_supplier_when_company_did_two_consumptions_from_same_supplier(
        self,
    ) -> None:
        consumer = self.company_generator.create_company_record()
        seller = self.company_generator.create_company_record()
        plan1 = self.plan_generator.create_plan(planner=seller.id)
        plan2 = self.plan_generator.create_plan(planner=seller.id)
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=consumer.id, plan=plan1
        )
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=consumer.id, plan=plan2
        )
        response = self.get_company_summary(consumer.id)
        assert response
        assert len(response.suppliers_ordered_by_volume) == 1

    def test_that_list_of_suppliers_contains_two_supplier_when_company_did_two_consumptions_from_different_suppliers(
        self,
    ) -> None:
        consumer = self.company_generator.create_company_record()
        self.company_generator.create_company_record()
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=consumer.id
        )
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=consumer.id
        )
        response = self.get_company_summary(consumer.id)
        assert response
        assert len(response.suppliers_ordered_by_volume) == 2

    def test_that_correct_supplier_id_is_shown(self) -> None:
        consumer = self.company_generator.create_company_record()
        supplier = self.company_generator.create_company_record()
        offered_plan = self.plan_generator.create_plan(planner=supplier.id)
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=consumer.id, plan=offered_plan
        )
        response = self.get_company_summary(consumer.id)
        assert response
        assert response.suppliers_ordered_by_volume[0].company_id == supplier.id

    def test_that_correct_supplier_name_is_shown(self) -> None:
        consumer = self.company_generator.create_company_record()
        supplier_name = "supplier coop"
        supplier = self.company_generator.create_company_record(name=supplier_name)
        offered_plan = self.plan_generator.create_plan(planner=supplier.id)
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=consumer.id, plan=offered_plan
        )
        response = self.get_company_summary(consumer.id)
        assert response
        assert response.suppliers_ordered_by_volume[0].company_name == supplier_name

    def test_that_correct_volume_of_sale_of_supplier_is_calculated_after_one_consumption(
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
        company = self.company_generator.create_company_record()
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=company.id, plan=plan, amount=1
        )
        response = self.get_company_summary(company.id)
        assert response
        assert response.suppliers_ordered_by_volume[0].volume_of_sales == Decimal("6")

    def test_that_correct_volume_of_sale_of_supplier_is_calculated_after_two_consumptions_from_same_supplier(
        self,
    ) -> None:
        consumer = self.company_generator.create_company_record()
        seller = self.company_generator.create_company_record()
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
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=consumer.id, plan=plan1, amount=1
        )
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=consumer.id, plan=plan2, amount=1
        )
        response = self.get_company_summary(consumer.id)
        assert response
        assert response.suppliers_ordered_by_volume[0].volume_of_sales == Decimal("18")

    def test_that_supplier_with_highest_sales_volume_is_listed_before_other_suppliers(
        self,
    ) -> None:
        consumer = self.company_generator.create_company_record()
        top_supplier = self.company_generator.create_company()
        top_supplier_plan = self.plan_generator.create_plan(planner=top_supplier)
        medium_supplier = self.company_generator.create_company()
        medium_supplier_plan = self.plan_generator.create_plan(planner=medium_supplier)
        low_supplier = self.company_generator.create_company()
        low_supplier_plan = self.plan_generator.create_plan(planner=low_supplier)
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=consumer.id, amount=1, plan=low_supplier_plan
        )
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=consumer.id, amount=20, plan=top_supplier_plan
        )
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=consumer.id, amount=10, plan=medium_supplier_plan
        )
        response = self.get_company_summary(consumer.id)
        assert response
        assert response.suppliers_ordered_by_volume[0].company_id == top_supplier
        assert response.suppliers_ordered_by_volume[1].company_id == medium_supplier
        assert response.suppliers_ordered_by_volume[2].company_id == low_supplier

    def test_that_correct_volumes_of_sale_of_suppliers_are_calculated_after_two_consumptions_from_different_suppliers(
        self,
    ) -> None:
        consumer = self.company_generator.create_company_record()
        plan1 = self.plan_generator.create_plan(
            costs=ProductionCosts(Decimal(1), Decimal(2), Decimal(3)),
            amount=1,
        )
        plan2 = self.plan_generator.create_plan(
            costs=ProductionCosts(Decimal(4), Decimal(5), Decimal(6)),
            amount=1,
        )
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=consumer.id, plan=plan1, amount=1
        )
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=consumer.id,
            plan=plan2,
            amount=1,
        )
        response = self.get_company_summary(consumer.id)
        assert response
        assert response.suppliers_ordered_by_volume[0].volume_of_sales == Decimal("15")
        assert response.suppliers_ordered_by_volume[1].volume_of_sales == Decimal("6")
