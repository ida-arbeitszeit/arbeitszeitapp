from datetime import datetime
from decimal import Decimal
from uuid import UUID

from arbeitszeit.records import ProductionCosts, SocialAccounting
from arbeitszeit.transactions import TransactionTypes
from arbeitszeit.use_cases.show_p_account_details import ShowPAccountDetailsUseCase
from tests.data_generators import TransactionGenerator

from .base_test_case import BaseTestCase


class ShowPAccountDetailsTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(ShowPAccountDetailsUseCase)
        self.transaction_generator = self.injector.get(TransactionGenerator)
        self.social_accounting = self.injector.get(SocialAccounting)

    def test_no_transactions_returned_when_company_has_neither_consumed_nor_planned_p(
        self,
    ) -> None:
        self.member_generator.create_member()
        company = self.company_generator.create_company()

        response = self.use_case.show_details(self.create_use_case_request(company))
        assert not response.transactions

    def test_balance_is_zero_when_company_has_neither_consumed_nor_planned_p(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        response = self.use_case.show_details(self.create_use_case_request(company))
        assert response.account_balance == 0

    def test_balance_is_zero_when_company_has_consumed_the_same_amount_of_p_as_it_has_planned(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        self.plan_generator.create_plan(
            planner=company, costs=ProductionCosts(Decimal(0), Decimal(0), Decimal(3))
        )
        plan_to_be_consumed = self.plan_generator.create_plan(
            costs=ProductionCosts(Decimal(1), Decimal(1), Decimal(1)), amount=1
        )
        self.consumption_generator.create_fixed_means_consumption(
            consumer=company, amount=1, plan=plan_to_be_consumed
        )
        response = self.use_case.show_details(self.create_use_case_request(company))
        assert response.account_balance == 0

    def test_sum_of_planned_p_is_zero_when_when_company_has_not_planned_p(self) -> None:
        company = self.company_generator.create_company()
        response = self.use_case.show_details(self.create_use_case_request(company))
        assert response.sum_of_planned_p == 0

    def test_sum_of_consumed_p_is_zero_when_company_has_not_consumed_p(self) -> None:
        company = self.company_generator.create_company()
        response = self.use_case.show_details(self.create_use_case_request(company))
        assert response.sum_of_consumed_p == 0

    def test_id_of_the_company_that_owns_the_account_is_returned(self) -> None:
        company = self.company_generator.create_company()
        response = self.use_case.show_details(self.create_use_case_request(company))
        assert response.company_id == company

    def test_that_no_transactions_are_generated_after_company_passed_on_a_consumer_product(
        self,
    ) -> None:
        producer = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=producer)
        transactions_before_consumption = len(
            self.use_case.show_details(
                self.create_use_case_request(producer)
            ).transactions
        )
        self.consumption_generator.create_private_consumption(plan=plan)
        response = self.use_case.show_details(self.create_use_case_request(producer))
        assert len(response.transactions) == transactions_before_consumption

    def test_that_no_transactions_are_generated_after_company_passed_on_a_means_of_production(
        self,
    ) -> None:
        producer = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=producer)
        transactions_before_consumption = len(
            self.use_case.show_details(
                self.create_use_case_request(producer)
            ).transactions
        )

        self.consumption_generator.create_fixed_means_consumption(plan=plan)
        response = self.use_case.show_details(self.create_use_case_request(producer))
        assert len(response.transactions) == transactions_before_consumption

    def test_that_transactions_are_generated_when_credit_for_r_is_granted(self) -> None:
        company = self.company_generator.create_company_record()

        self.transaction_generator.create_transaction(
            sending_account=self.social_accounting.account,
            receiving_account=company.raw_material_account,
            amount_sent=Decimal(10),
            amount_received=Decimal(8.5),
        )

        response = self.use_case.show_details(self.create_use_case_request(company.id))
        assert len(response.transactions) == 0

    def test_that_one_transaction_is_shown_when_credit_for_p_is_granted(self) -> None:
        planner = self.company_generator.create_company()
        self.plan_generator.create_plan(
            planner=planner, costs=ProductionCosts(Decimal(1), Decimal(2), Decimal(3))
        )
        response = self.use_case.show_details(self.create_use_case_request(planner))
        assert len(response.transactions) == 1

    def test_that_two_transactions_are_shown_when_credit_for_p_is_granted_and_company_consumes_p(
        self,
    ) -> None:
        planner = self.company_generator.create_company()
        self.plan_generator.create_plan(
            planner=planner, costs=ProductionCosts(Decimal(1), Decimal(2), Decimal(3))
        )
        self.consumption_generator.create_fixed_means_consumption(
            consumer=planner, amount=2
        )
        response = self.use_case.show_details(self.create_use_case_request(planner))
        assert len(response.transactions) == 2

    def test_that_two_transactions_are_shown_in_descending_order(self) -> None:
        planner = self.company_generator.create_company()
        self.plan_generator.create_plan(
            planner=planner, costs=ProductionCosts(Decimal(1), Decimal(2), Decimal(3))
        )
        self.consumption_generator.create_fixed_means_consumption(
            consumer=planner, amount=2
        )
        response = self.use_case.show_details(self.create_use_case_request(planner))
        assert (
            response.transactions[0].transaction_type
            == TransactionTypes.consumption_of_fixed_means
        )
        assert (
            response.transactions[1].transaction_type
            == TransactionTypes.credit_for_fixed_means
        )

    def test_that_correct_info_is_generated_when_credit_for_p_is_granted(self) -> None:
        company = self.company_generator.create_company_record()

        self.transaction_generator.create_transaction(
            sending_account=self.social_accounting.account,
            receiving_account=company.means_account,
            amount_sent=Decimal(10),
            amount_received=Decimal(8.5),
        )

        response = self.use_case.show_details(self.create_use_case_request(company.id))
        assert len(response.transactions) == 1
        assert response.transactions[0].transaction_volume == Decimal(8.5)
        assert response.transactions[0].purpose is not None
        assert isinstance(response.transactions[0].date, datetime)
        assert (
            response.transactions[0].transaction_type
            == TransactionTypes.credit_for_fixed_means
        )
        assert response.account_balance == Decimal(8.5)

    def test_that_after_consumption_of_means_of_production_a_transaction_of_that_type_is_shown(
        self,
    ) -> None:
        consumer = self.company_generator.create_company()
        self.consumption_generator.create_fixed_means_consumption(consumer=consumer)

        response = self.use_case.show_details(self.create_use_case_request(consumer))
        transaction = response.transactions[0]
        assert (
            transaction.transaction_type == TransactionTypes.consumption_of_fixed_means
        )

    def test_that_after_consumption_of_fixed_means_a_transaction_with_volume_of_negated_costs_is_shown(
        self,
    ) -> None:
        consumer = self.company_generator.create_company()
        costs = ProductionCosts(Decimal(1), Decimal(2), Decimal(3))
        expected_volume = -costs.total_cost()
        plan = self.plan_generator.create_plan(costs=costs, amount=1)
        self.consumption_generator.create_fixed_means_consumption(
            consumer=consumer, plan=plan, amount=1
        )

        response = self.use_case.show_details(self.create_use_case_request(consumer))
        transaction = response.transactions[0]
        assert transaction.transaction_volume == expected_volume

    def test_that_after_consumption_of_fixed_means_the_balance_equals_the_negated_costs(
        self,
    ) -> None:
        consumer = self.company_generator.create_company()
        costs = ProductionCosts(Decimal(1), Decimal(2), Decimal(3))
        expected_balance = -costs.total_cost()
        plan = self.plan_generator.create_plan(costs=costs, amount=1)
        self.consumption_generator.create_fixed_means_consumption(
            consumer=consumer, plan=plan, amount=1
        )

        response = self.use_case.show_details(self.create_use_case_request(consumer))
        assert response.account_balance == expected_balance

    def test_that_after_consumption_of_two_fixed_means_the_p_balance_equals_negated_sum_of_costs(
        self,
    ) -> None:
        consumer = self.company_generator.create_company()
        costs1 = ProductionCosts(Decimal(1), Decimal(2), Decimal(3))
        costs2 = ProductionCosts(Decimal(4), Decimal(5), Decimal(6))
        expected_balance = -(costs1.total_cost() + costs2.total_cost())
        plan1 = self.plan_generator.create_plan(costs=costs1, amount=1)
        self.consumption_generator.create_fixed_means_consumption(
            consumer=consumer, plan=plan1, amount=1
        )
        plan2 = self.plan_generator.create_plan(costs=costs2, amount=1)
        self.consumption_generator.create_fixed_means_consumption(
            consumer=consumer, plan=plan2, amount=1
        )

        response = self.use_case.show_details(self.create_use_case_request(consumer))
        assert response.account_balance == expected_balance

    def test_that_after_filing_two_plans_the_sum_of_planned_p_is_equal_to_the_sum_of_the_costs_for_p(
        self,
    ) -> None:
        planner = self.company_generator.create_company()
        costs1 = ProductionCosts(Decimal(1), Decimal(2), Decimal(3))
        costs2 = ProductionCosts(Decimal(4), Decimal(5), Decimal(6))
        expected_sum = costs1.means_cost + costs2.means_cost
        self.plan_generator.create_plan(costs=costs1, amount=1, planner=planner)
        self.plan_generator.create_plan(costs=costs2, amount=1, planner=planner)

        response = self.use_case.show_details(self.create_use_case_request(planner))
        assert response.sum_of_planned_p == expected_sum

    def test_that_after_consuming_two_means_of_productions_the_sum_of_consumed_p_is_equal_to_the_sum_of_the_costs(
        self,
    ) -> None:
        consumer = self.company_generator.create_company()
        costs1 = ProductionCosts(Decimal(1), Decimal(2), Decimal(3))
        costs2 = ProductionCosts(Decimal(4), Decimal(5), Decimal(6))
        expected_sum = costs1.total_cost() + costs2.total_cost()
        plan1 = self.plan_generator.create_plan(costs=costs1, amount=1)
        self.consumption_generator.create_fixed_means_consumption(
            consumer=consumer, plan=plan1, amount=1
        )
        plan2 = self.plan_generator.create_plan(costs=costs2, amount=1)
        self.consumption_generator.create_fixed_means_consumption(
            consumer=consumer, plan=plan2, amount=1
        )

        response = self.use_case.show_details(self.create_use_case_request(consumer))
        assert response.sum_of_consumed_p == expected_sum

    def test_that_plotting_info_is_empty_when_no_transactions_occurred(self) -> None:
        self.member_generator.create_member()
        company = self.company_generator.create_company()

        response = self.use_case.show_details(self.create_use_case_request(company))
        assert not response.plot.timestamps
        assert not response.plot.accumulated_volumes

    def test_that_plotting_info_is_generated_after_consumption_of_fixed_means_of_production(
        self,
    ) -> None:
        own_company = self.company_generator.create_company_record()
        other_company = self.company_generator.create_company_record()

        self.transaction_generator.create_transaction(
            sending_account=own_company.means_account,
            receiving_account=other_company.product_account,
            amount_sent=Decimal(10),
            amount_received=Decimal(8.5),
        )

        response = self.use_case.show_details(
            self.create_use_case_request(own_company.id)
        )
        assert response.plot.timestamps
        assert response.plot.accumulated_volumes

    def test_that_correct_plotting_info_is_generated_after_consumption_of_two_fixed_means_of_production(
        self,
    ) -> None:
        own_company = self.company_generator.create_company_record()
        other_company = self.company_generator.create_company_record()

        trans1 = self.transaction_generator.create_transaction(
            sending_account=own_company.means_account,
            receiving_account=other_company.product_account,
            amount_sent=Decimal(10),
            amount_received=Decimal(5),
        )

        trans2 = self.transaction_generator.create_transaction(
            sending_account=own_company.means_account,
            receiving_account=other_company.product_account,
            amount_sent=Decimal(10),
            amount_received=Decimal(10),
        )

        response = self.use_case.show_details(
            self.create_use_case_request(own_company.id)
        )
        assert len(response.plot.timestamps) == 2
        assert len(response.plot.accumulated_volumes) == 2

        assert trans1.date in response.plot.timestamps
        assert trans2.date in response.plot.timestamps

        assert trans1.amount_sent * (-1) in response.plot.accumulated_volumes
        assert (
            trans1.amount_sent * (-1) + trans2.amount_sent * (-1)
        ) in response.plot.accumulated_volumes

    def test_that_plotting_info_is_generated_in_the_correct_order_after_consumption_of_three_fixed_means_of_production(
        self,
    ) -> None:
        own_company = self.company_generator.create_company_record()
        other_company = self.company_generator.create_company_record()

        trans1 = self.transaction_generator.create_transaction(
            sending_account=own_company.means_account,
            receiving_account=other_company.product_account,
            amount_sent=Decimal(10),
            amount_received=Decimal(1),
        )

        trans2 = self.transaction_generator.create_transaction(
            sending_account=own_company.means_account,
            receiving_account=other_company.product_account,
            amount_sent=Decimal(10),
            amount_received=Decimal(2),
        )

        trans3 = self.transaction_generator.create_transaction(
            sending_account=own_company.means_account,
            receiving_account=other_company.product_account,
            amount_sent=Decimal(10),
            amount_received=Decimal(3),
        )

        response = self.use_case.show_details(
            self.create_use_case_request(own_company.id)
        )
        assert response.plot.timestamps[0] == trans1.date
        assert response.plot.timestamps[2] == trans3.date

        assert response.plot.accumulated_volumes[0] == trans1.amount_sent * (-1)
        assert response.plot.accumulated_volumes[2] == (
            trans1.amount_sent * (-1)
            + trans2.amount_sent * (-1)
            + trans3.amount_sent * (-1)
        )

    def test_that_correct_plotting_info_is_generated_after_receiving_of_credit_for_fixed_means_of_production(
        self,
    ) -> None:
        company = self.company_generator.create_company_record()
        trans = self.transaction_generator.create_transaction(
            sending_account=self.social_accounting.account,
            receiving_account=company.means_account,
            amount_sent=Decimal(10),
            amount_received=Decimal(8.5),
        )

        response = self.use_case.show_details(self.create_use_case_request(company.id))
        assert response.plot.timestamps
        assert response.plot.accumulated_volumes

        assert len(response.plot.timestamps) == 1
        assert len(response.plot.accumulated_volumes) == 1

        assert trans.date in response.plot.timestamps
        assert trans.amount_received in response.plot.accumulated_volumes

    def create_use_case_request(
        self, company_id: UUID
    ) -> ShowPAccountDetailsUseCase.Request:
        return ShowPAccountDetailsUseCase.Request(company=company_id)
