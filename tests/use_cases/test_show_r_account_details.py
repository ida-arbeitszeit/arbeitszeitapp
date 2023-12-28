from datetime import datetime
from decimal import Decimal

from arbeitszeit.records import ProductionCosts, SocialAccounting
from arbeitszeit.transactions import TransactionTypes
from arbeitszeit.use_cases.show_r_account_details import ShowRAccountDetailsUseCase
from tests.data_generators import TransactionGenerator

from .base_test_case import BaseTestCase


class UseCaseTester(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.show_r_account_details = self.injector.get(ShowRAccountDetailsUseCase)
        self.transaction_generator = self.injector.get(TransactionGenerator)
        self.social_accounting = self.injector.get(SocialAccounting)

    def test_no_transactions_returned_when_no_transactions_took_place(self) -> None:
        self.member_generator.create_member()
        company = self.company_generator.create_company_record()
        response = self.show_r_account_details(company.id)
        assert not response.transactions

    def test_balance_is_zero_when_no_transactions_took_place(self) -> None:
        self.member_generator.create_member()
        company = self.company_generator.create_company_record()

        response = self.show_r_account_details(company.id)
        assert response.account_balance == 0

    def test_company_id_is_returned(self) -> None:
        self.member_generator.create_member()
        company = self.company_generator.create_company_record()

        response = self.show_r_account_details(company.id)
        assert response.company_id == company.id

    def test_that_no_info_is_generated_after_selling_of_consumer_product(self) -> None:
        member = self.member_generator.create_member()
        company = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=company)
        transactions_before_consumption = len(
            self.show_r_account_details(company).transactions
        )
        self.consumption_generator.create_private_consumption(
            consumer=member, plan=plan.id
        )
        response = self.show_r_account_details(company)
        assert len(response.transactions) == transactions_before_consumption

    def test_that_no_info_is_generated_when_company_sells_p(self) -> None:
        company1 = self.company_generator.create_company_record()
        company2 = self.company_generator.create_company_record()

        self.transaction_generator.create_transaction(
            sending_account=company1.means_account,
            receiving_account=company2.product_account,
            amount_sent=Decimal(10),
            amount_received=Decimal(8.5),
        )

        response = self.show_r_account_details(company2.id)
        assert not response.transactions

    def test_that_no_info_is_generated_when_credit_for_p_is_granted(self) -> None:
        company = self.company_generator.create_company_record()

        self.transaction_generator.create_transaction(
            sending_account=self.social_accounting.account,
            receiving_account=company.means_account,
            amount_sent=Decimal(10),
            amount_received=Decimal(8.5),
        )

        response = self.show_r_account_details(company.id)
        assert len(response.transactions) == 0

    def test_that_one_transaction_is_shown_when_credit_for_r_is_granted(self) -> None:
        planner = self.company_generator.create_company()
        self.plan_generator.create_plan(
            planner=planner, costs=ProductionCosts(Decimal(1), Decimal(2), Decimal(3))
        )
        response = self.show_r_account_details(planner)
        assert len(response.transactions) == 1

    def test_that_two_transactions_are_shown_when_credit_for_r_is_granted_and_company_consumes_r(
        self,
    ) -> None:
        planner = self.company_generator.create_company()
        self.plan_generator.create_plan(
            planner=planner, costs=ProductionCosts(Decimal(1), Decimal(2), Decimal(3))
        )
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=planner, amount=2
        )
        response = self.show_r_account_details(planner)
        assert len(response.transactions) == 2

    def test_that_two_transactions_are_shown_in_descending_order(self) -> None:
        planner = self.company_generator.create_company()
        self.plan_generator.create_plan(
            planner=planner, costs=ProductionCosts(Decimal(1), Decimal(2), Decimal(3))
        )
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=planner, amount=2
        )
        response = self.show_r_account_details(planner)
        assert (
            response.transactions[0].transaction_type
            == TransactionTypes.consumption_of_liquid_means
        )
        assert (
            response.transactions[1].transaction_type
            == TransactionTypes.credit_for_liquid_means
        )

    def test_that_correct_info_is_generated_when_credit_for_r_is_granted(self) -> None:
        company = self.company_generator.create_company_record()

        self.transaction_generator.create_transaction(
            sending_account=self.social_accounting.account,
            receiving_account=company.raw_material_account,
            amount_sent=Decimal(10),
            amount_received=Decimal(8.5),
        )

        response = self.show_r_account_details(company.id)
        assert len(response.transactions) == 1
        assert response.transactions[0].transaction_volume == Decimal(8.5)
        assert response.transactions[0].purpose is not None
        assert isinstance(response.transactions[0].date, datetime)
        assert (
            response.transactions[0].transaction_type
            == TransactionTypes.credit_for_liquid_means
        )
        assert response.account_balance == Decimal(8.5)

    def test_that_correct_info_for_is_generated_after_company_consuming_r(self) -> None:
        company1 = self.company_generator.create_company_record()
        company2 = self.company_generator.create_company_record()

        trans = self.transaction_generator.create_transaction(
            sending_account=company1.raw_material_account,
            receiving_account=company2.product_account,
            amount_sent=Decimal(10),
            amount_received=Decimal(8.5),
        )

        response = self.show_r_account_details(company1.id)
        transaction = response.transactions[0]
        assert (
            transaction.transaction_type == TransactionTypes.consumption_of_liquid_means
        )
        assert transaction.transaction_volume == -trans.amount_sent
        assert response.account_balance == -trans.amount_sent

    def test_that_plotting_info_is_empty_when_no_transactions_occurred(self) -> None:
        self.member_generator.create_member()
        company = self.company_generator.create_company_record()

        response = self.show_r_account_details(company.id)
        assert not response.plot.timestamps
        assert not response.plot.accumulated_volumes

    def test_that_plotting_info_is_generated_after_consumption_of_liquid_means_of_production(
        self,
    ) -> None:
        own_company = self.company_generator.create_company_record()
        other_company = self.company_generator.create_company_record()

        self.transaction_generator.create_transaction(
            sending_account=own_company.raw_material_account,
            receiving_account=other_company.product_account,
            amount_sent=Decimal(10),
            amount_received=Decimal(8.5),
        )

        response = self.show_r_account_details(own_company.id)
        assert response.plot.timestamps
        assert response.plot.accumulated_volumes

    def test_that_correct_plotting_info_is_generated_after_consumption_of_two_liquid_means_of_production(
        self,
    ) -> None:
        own_company = self.company_generator.create_company_record()
        other_company = self.company_generator.create_company_record()

        trans1 = self.transaction_generator.create_transaction(
            sending_account=own_company.raw_material_account,
            receiving_account=other_company.product_account,
            amount_sent=Decimal(10),
            amount_received=Decimal(5),
        )

        trans2 = self.transaction_generator.create_transaction(
            sending_account=own_company.raw_material_account,
            receiving_account=other_company.product_account,
            amount_sent=Decimal(10),
            amount_received=Decimal(10),
        )

        response = self.show_r_account_details(own_company.id)
        assert len(response.plot.timestamps) == 2
        assert len(response.plot.accumulated_volumes) == 2

        assert trans1.date in response.plot.timestamps
        assert trans2.date in response.plot.timestamps

        assert trans1.amount_sent * (-1) in response.plot.accumulated_volumes
        assert (
            trans1.amount_sent * (-1) + trans2.amount_sent * (-1)
        ) in response.plot.accumulated_volumes

    def test_that_plotting_info_is_generated_in_the_correct_order_after_consumption_of_three_liquid_means_of_production(
        self,
    ) -> None:
        own_company = self.company_generator.create_company_record()
        other_company = self.company_generator.create_company_record()

        trans1 = self.transaction_generator.create_transaction(
            sending_account=own_company.raw_material_account,
            receiving_account=other_company.product_account,
            amount_sent=Decimal(10),
            amount_received=Decimal(1),
        )

        trans2 = self.transaction_generator.create_transaction(
            sending_account=own_company.raw_material_account,
            receiving_account=other_company.product_account,
            amount_sent=Decimal(10),
            amount_received=Decimal(2),
        )

        trans3 = self.transaction_generator.create_transaction(
            sending_account=own_company.raw_material_account,
            receiving_account=other_company.product_account,
            amount_sent=Decimal(10),
            amount_received=Decimal(3),
        )

        response = self.show_r_account_details(own_company.id)
        assert response.plot.timestamps[0] == trans1.date
        assert response.plot.timestamps[2] == trans3.date

        assert response.plot.accumulated_volumes[0] == trans1.amount_sent * (-1)
        assert response.plot.accumulated_volumes[2] == (
            trans1.amount_sent * (-1)
            + trans2.amount_sent * (-1)
            + trans3.amount_sent * (-1)
        )

    def test_that_correct_plotting_info_is_generated_after_receiving_of_credit_for_liquid_means_of_production(
        self,
    ) -> None:
        company = self.company_generator.create_company_record()
        trans = self.transaction_generator.create_transaction(
            sending_account=self.social_accounting.account,
            receiving_account=company.raw_material_account,
            amount_sent=Decimal(10),
            amount_received=Decimal(8.5),
        )
        response = self.show_r_account_details(company.id)
        assert response.plot.timestamps
        assert response.plot.accumulated_volumes
        assert len(response.plot.timestamps) == 1
        assert len(response.plot.accumulated_volumes) == 1
        assert trans.date in response.plot.timestamps
        assert trans.amount_received in response.plot.accumulated_volumes
