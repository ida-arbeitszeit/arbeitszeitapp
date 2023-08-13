from decimal import Decimal

from arbeitszeit.records import ProductionCosts
from arbeitszeit.use_cases.get_company_summary import GetCompanySummary

from ..base_test_case import BaseTestCase


class UseCaseTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.get_company_summary = self.injector.get(GetCompanySummary)

    def test_show_relative_deviation_of_zero_for_all_accounts_when_no_transactions_took_place(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        response = self.get_company_summary(company)
        assert response
        for i in range(4):
            assert response.deviations_relative[i] == 0

    def test_show_infinite_relative_deviation_if_company_buyes_fixed_means_without_planning_for_some(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(
            costs=ProductionCosts(Decimal(5), Decimal(0), Decimal(0))
        )
        self.purchase_generator.create_fixed_means_purchase(
            buyer=company, amount=1, plan=plan.id
        )
        response = self.get_company_summary(company)
        assert response
        assert response.deviations_relative[0] == Decimal("Infinity")
        assert response.deviations_relative[1] == 0

    def test_show_100_percent_deviation_for_p_if_right_after_plan_was_approved_when_p_was_planned(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        self.plan_generator.create_plan(
            planner=company,
            costs=ProductionCosts(
                means_cost=Decimal(1),
                resource_cost=Decimal(0),
                labour_cost=Decimal(0),
            ),
        )
        response = self.get_company_summary(company)
        assert response
        assert response.deviations_relative[0] == Decimal(100)  # fixed means
        assert response.deviations_relative[1] == Decimal(0)  # liquid means
        assert response.deviations_relative[2] == Decimal(0)  # labour

    def test_show_100_percent_deviation_right_after_a_plan_of_company_was_approved(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        self.plan_generator.create_plan(planner=company)
        response = self.get_company_summary(company)
        assert response
        assert response.deviations_relative[3] == Decimal(100)

    def test_show_relative_deviation_of_50_when_company_sells_half_of_expected_sales(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(amount=2, planner=company)
        self.purchase_generator.create_fixed_means_purchase(plan=plan.id, amount=1)
        response = self.get_company_summary(company)
        assert response
        assert response.deviations_relative[3] == Decimal(50)

    def test_show_100_percent_sales_deviation_if_double_amount_of_products_was_sold(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(
            planner=company,
            costs=ProductionCosts(Decimal(5), Decimal(5), Decimal(0)),
            amount=1,
        )
        self.purchase_generator.create_fixed_means_purchase(plan=plan.id, amount=2)
        response = self.get_company_summary(company)
        assert response
        assert response.plan_details[0].deviation_relative == Decimal(100)

    def test_show_100_percent_sales_deviation_if_no_product_for_plan_was_sold(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        self.plan_generator.create_plan(
            planner=company,
            costs=ProductionCosts(Decimal(5), Decimal(5), Decimal(0)),
            amount=1,
        )
        response = self.get_company_summary(company)
        assert response
        assert response.plan_details[0].deviation_relative == Decimal(100)

    def test_show_0_sales_deviation_of_planned_amount_if_planned_product_was_sold(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=company, amount=12)
        self.purchase_generator.create_fixed_means_purchase(plan=plan.id, amount=12)
        response = self.get_company_summary(company)
        assert response
        assert response.plan_details[0].deviation_relative == Decimal(0)

    def test_show_0_sales_deviation_for_public_plan_after_one_private_consumption(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(
            planner=company,
            is_public_service=True,
        )
        self.purchase_generator.create_private_consumption(plan=plan.id)
        response = self.get_company_summary(company)
        assert response
        assert response.plan_details[0].deviation_relative == Decimal("0")
