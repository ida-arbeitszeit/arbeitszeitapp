from datetime import datetime, timedelta
from decimal import Decimal

from arbeitszeit.entities import ProductionCosts
from arbeitszeit.use_cases.get_company_summary import GetCompanySummary

from ..base_test_case import BaseTestCase


class ExpectationsTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.get_company_summary = self.injector.get(GetCompanySummary)

    def test_returns_expectations_of_zero_when_no_transactions_took_place(self) -> None:
        company = self.company_generator.create_company()
        response = self.get_company_summary(company)
        assert response
        assert response.expectations.means == 0
        assert response.expectations.raw_material == 0
        assert response.expectations.work == 0
        assert response.expectations.product == 0

    def test_that_expectations_returned_for_p_are_exactly_what_company_planned_for_after_plan_was_approved(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        expected_p = Decimal(123)
        self.plan_generator.create_plan(
            costs=ProductionCosts(
                means_cost=expected_p, resource_cost=Decimal(0), labour_cost=Decimal(1)
            ),
            approved=True,
            planner=company,
        )
        response = self.get_company_summary(company)
        assert response
        assert response.expectations.means == expected_p

    def test_that_expectations_returned_for_r_are_exactly_what_company_planned_for_after_plan_was_approved(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        expected_r = Decimal(123)
        self.plan_generator.create_plan(
            costs=ProductionCosts(
                means_cost=Decimal(1), resource_cost=expected_r, labour_cost=Decimal(1)
            ),
            approved=True,
            planner=company,
        )
        response = self.get_company_summary(company)
        assert response
        assert response.expectations.raw_material == expected_r

    def test_that_expectations_for_a_are_exactly_planned_labour_after_approved_plan_expired(
        self,
    ) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        company = self.company_generator.create_company()
        expected_a = Decimal(1231)
        self.plan_generator.create_plan(
            costs=ProductionCosts(
                means_cost=Decimal(0),
                resource_cost=Decimal(0),
                labour_cost=expected_a,
            ),
            approved=True,
            timeframe=1,
            planner=company,
        )
        self.datetime_service.advance_time(timedelta(days=2))
        response = self.get_company_summary(company)
        assert response
        assert response.expectations.work == expected_a

    def test_that_expectations_for_prd_are_exactly_planned_costs_after_approved_plan_expired(
        self,
    ) -> None:
        expected_prd = Decimal(12 * 3)
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        company = self.company_generator.create_company()
        self.plan_generator.create_plan(
            costs=ProductionCosts(
                means_cost=expected_prd / 3,
                resource_cost=expected_prd / 3,
                labour_cost=expected_prd / 3,
            ),
            approved=True,
            timeframe=1,
            planner=company,
        )
        self.datetime_service.advance_time(timedelta(days=2))
        response = self.get_company_summary(company)
        assert response
        assert response.expectations.product == -expected_prd

    def test_that_expectations_for_prd_did_not_changed_after_sale_to_another_company(
        self,
    ) -> None:
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=planner)
        buyer = self.company_generator.create_company()
        response_before_sale = self.get_company_summary(planner)
        assert response_before_sale
        self.purchase_generator.create_fixed_means_purchase(
            buyer=buyer,
            plan=plan.id,
            amount=1,
        )
        response_after_sale = self.get_company_summary(planner)
        assert response_after_sale
        assert (
            response_before_sale.expectations.product
            == response_after_sale.expectations.product
        )
