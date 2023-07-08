from decimal import Decimal
from typing import Union

from arbeitszeit.entities import ProductionCosts
from arbeitszeit.use_cases.calculate_fic_and_update_expired_plans import (
    CalculateFicAndUpdateExpiredPlans,
)
from arbeitszeit.use_cases.get_company_summary import (
    GetCompanySummary,
    GetCompanySummarySuccess,
    PlanDetails,
)

from ..base_test_case import BaseTestCase


class UseCaseTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.get_company_summary = self.injector.get(GetCompanySummary)
        self.payout = self.injector.get(CalculateFicAndUpdateExpiredPlans)

    def test_returns_correct_sales_balance_if_plan_is_productive_and_no_transactions_took_place(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        self.plan_generator.create_plan(
            planner=company, costs=self._create_planning_costs(3)
        )
        response = self.get_company_summary(company)
        assert response
        assert response.plan_details[0].sales_balance == Decimal("-3")

    def test_show_sales_balance_of_half_production_costs_if_one_of_two_units_were_sold(
        self,
    ) -> None:
        costs = self._create_planning_costs(3)
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

    def test_that_sales_balance_is_0_if_no_product_of_plan_was_sold_but_product_of_another_plan_was_sold(
        self,
    ) -> None:
        expected_product_name = "my product name for testing"
        costs = self._create_planning_costs()
        planner = self.company_generator.create_company()
        self.plan_generator.create_plan(
            planner=planner, costs=costs, product_name=expected_product_name
        )
        other_plan = self.plan_generator.create_plan(planner=planner)
        self.purchase_generator.create_fixed_means_purchase(plan=other_plan.id)
        response = self.get_company_summary(planner)
        assert response
        plan_details = self._find_balance_for_named_product(
            expected_product_name, response
        )
        assert plan_details.sales_balance == -costs.total_cost()

    def _create_planning_costs(
        self, total_costs: Union[Decimal, float, str, int] = Decimal(3)
    ) -> ProductionCosts:
        total_costs = Decimal(total_costs)
        return ProductionCosts(total_costs / 3, total_costs / 3, total_costs / 3)

    def _find_balance_for_named_product(
        self, name: str, response: GetCompanySummarySuccess
    ) -> PlanDetails:
        for candidate in response.plan_details:
            if candidate.name == name:
                return candidate
        self.fail(
            f"Could not find plan details for product named `{name}` in response {response}"
        )
