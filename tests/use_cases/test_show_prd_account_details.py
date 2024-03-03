from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID

from arbeitszeit.records import ProductionCosts, SocialAccounting
from arbeitszeit.transactions import TransactionTypes
from arbeitszeit.use_cases import show_prd_account_details

from .base_test_case import BaseTestCase


class UseCaseTester(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(
            show_prd_account_details.ShowPRDAccountDetailsUseCase
        )
        self.social_accounting = self.injector.get(SocialAccounting)
        self.control_thresholds.set_allowed_overdraw_of_member_account(10000)

    def test_no_transactions_returned_when_no_transactions_took_place(self) -> None:
        self.member_generator.create_member()
        company = self.company_generator.create_company()

        response = self.use_case.show_details(
            self.create_use_case_request(company_id=company)
        )
        assert not response.transactions

    def test_balance_is_zero_when_no_transactions_took_place(self) -> None:
        self.member_generator.create_member()
        company = self.company_generator.create_company()

        response = self.use_case.show_details(
            self.create_use_case_request(company_id=company)
        )
        assert response.account_balance == 0

    def test_company_id_is_returned(self) -> None:
        self.member_generator.create_member()
        company = self.company_generator.create_company()

        response = self.use_case.show_details(
            self.create_use_case_request(company_id=company)
        )
        assert response.company_id == company

    def test_that_no_info_is_generated_after_company_consuming_p(self) -> None:
        consumer = self.company_generator.create_company()
        self.consumption_generator.create_fixed_means_consumption(consumer=consumer)
        response = self.use_case.show_details(
            self.create_use_case_request(company_id=consumer)
        )
        assert len(response.transactions) == 0

    def test_that_no_info_is_generated_after_company_consuming_r(self) -> None:
        consumer = self.company_generator.create_company()
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=consumer
        )
        response = self.use_case.show_details(
            self.create_use_case_request(company_id=consumer)
        )
        assert len(response.transactions) == 0

    def test_that_one_transaction_is_shown_after_filed_plan_is_accepted(self) -> None:
        company = self.company_generator.create_company()
        assert not self.use_case.show_details(
            self.create_use_case_request(company_id=company)
        ).transactions
        self.plan_generator.create_plan(planner=company)
        response = self.use_case.show_details(
            self.create_use_case_request(company_id=company)
        )
        assert len(response.transactions) == 1

    def test_that_two_transactions_are_shown_after_filed_plan_is_accepted_and_product_is_sold(
        self,
    ) -> None:
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=planner)
        self.consumption_generator.create_private_consumption(plan=plan)
        response = self.use_case.show_details(
            self.create_use_case_request(company_id=planner)
        )
        assert len(response.transactions) == 2

    def test_that_transactions_are_shown_in_correct_descending_order(self) -> None:
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=planner)
        self.consumption_generator.create_private_consumption(plan=plan)
        response = self.use_case.show_details(
            self.create_use_case_request(company_id=planner)
        )
        transactions = response.transactions
        assert (
            transactions[0].transaction_type
            == TransactionTypes.sale_of_consumer_product
        )
        assert transactions[1].transaction_type == TransactionTypes.expected_sales

    def test_that_correct_info_is_generated_after_selling_of_consumer_product(
        self,
    ) -> None:
        consumer = self.member_generator.create_member()
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(
            planner=planner,
            costs=ProductionCosts(
                labour_cost=Decimal(2),
                means_cost=Decimal(0),
                resource_cost=Decimal(0),
            ),
            amount=1,
        )
        response = self.use_case.show_details(
            self.create_use_case_request(company_id=planner)
        )
        assert len(response.transactions) == 1
        self.consumption_generator.create_private_consumption(
            plan=plan,
            consumer=consumer,
            amount=1,
        )
        response = self.use_case.show_details(
            self.create_use_case_request(company_id=planner)
        )
        assert len(response.transactions) == 2
        transaction_of_sale = response.transactions[0]
        assert transaction_of_sale.transaction_volume == Decimal(2)
        assert transaction_of_sale.purpose is not None
        assert isinstance(response.transactions[-1].date, datetime)
        assert (
            transaction_of_sale.transaction_type
            == TransactionTypes.sale_of_consumer_product
        )
        assert response.account_balance == Decimal(0)

    def test_that_correct_info_is_generated_after_selling_of_means_of_production(
        self,
    ) -> None:
        consumer = self.company_generator.create_company()
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(
            planner=planner,
            costs=ProductionCosts(
                labour_cost=Decimal(2), means_cost=Decimal(0), resource_cost=Decimal(0)
            ),
            amount=1,
        )
        response = self.use_case.show_details(
            self.create_use_case_request(company_id=planner)
        )
        assert len(response.transactions) == 1
        self.consumption_generator.create_fixed_means_consumption(
            plan=plan, consumer=consumer
        )
        response = self.use_case.show_details(
            self.create_use_case_request(company_id=planner)
        )
        assert len(response.transactions) == 2
        transaction_of_sale = response.transactions[0]
        assert transaction_of_sale.transaction_volume == Decimal(2)
        assert transaction_of_sale.purpose is not None
        assert isinstance(transaction_of_sale.date, datetime)
        assert (
            transaction_of_sale.transaction_type == TransactionTypes.sale_of_fixed_means
        )
        assert response.account_balance == Decimal(0)

    def test_that_correct_info_is_generated_after_selling_of_raw_material(self) -> None:
        consumer = self.company_generator.create_company()
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(
            planner=planner,
            costs=ProductionCosts(
                labour_cost=Decimal(2), means_cost=Decimal(0), resource_cost=Decimal(0)
            ),
            amount=1,
        )
        response = self.use_case.show_details(
            self.create_use_case_request(company_id=planner)
        )
        assert len(response.transactions) == 1
        self.consumption_generator.create_resource_consumption_by_company(
            plan=plan, consumer=consumer
        )
        response = self.use_case.show_details(
            self.create_use_case_request(company_id=planner)
        )
        assert len(response.transactions) == 2
        transaction_of_sale = response.transactions[0]
        assert transaction_of_sale.transaction_volume == Decimal(2)
        assert transaction_of_sale.purpose is not None
        assert isinstance(transaction_of_sale.date, datetime)
        assert (
            transaction_of_sale.transaction_type
            == TransactionTypes.sale_of_liquid_means
        )
        assert response.account_balance == Decimal(0)

    def test_that_plotting_info_is_empty_when_no_transactions_occurred(self) -> None:
        company = self.company_generator.create_company()
        response = self.use_case.show_details(
            self.create_use_case_request(company_id=company)
        )
        assert not response.plot.timestamps
        assert not response.plot.accumulated_volumes

    def test_that_plotting_info_is_generated_after_selling_of_consumer_product(
        self,
    ) -> None:
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=planner)
        self.consumption_generator.create_private_consumption(plan=plan)
        response = self.use_case.show_details(
            self.create_use_case_request(company_id=planner)
        )
        assert response.plot.timestamps
        assert response.plot.accumulated_volumes

    def test_that_correct_plotting_info_is_generated_after_selling_of_two_consumer_products(
        self,
    ) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(
            planner=planner,
            costs=ProductionCosts(
                labour_cost=Decimal(1), means_cost=Decimal(0), resource_cost=Decimal(0)
            ),
            amount=1,
        )
        transaction_1_timestamp = self.datetime_service.advance_time(timedelta(days=1))
        self.consumption_generator.create_private_consumption(plan=plan, amount=1)
        transaction_2_timestamp = self.datetime_service.advance_time(timedelta(days=1))
        self.consumption_generator.create_private_consumption(plan=plan, amount=2)
        response = self.use_case.show_details(
            self.create_use_case_request(company_id=planner)
        )
        assert len(response.plot.timestamps) == 3
        assert len(response.plot.accumulated_volumes) == 3
        assert transaction_1_timestamp in response.plot.timestamps
        assert transaction_2_timestamp in response.plot.timestamps
        assert Decimal(0) in response.plot.accumulated_volumes
        assert Decimal(2) in response.plot.accumulated_volumes

    def test_that_plotting_info_is_generated_in_the_correct_order_after_selling_of_three_consumer_products(
        self,
    ) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(
            planner=planner,
            costs=ProductionCosts(
                labour_cost=Decimal(0), means_cost=Decimal(1), resource_cost=Decimal(0)
            ),
            amount=1,
        )
        transaction_1_timestamp = self.datetime_service.advance_time(timedelta(days=1))
        self.consumption_generator.create_private_consumption(plan=plan, amount=1)
        self.datetime_service.advance_time(timedelta(days=1))
        self.consumption_generator.create_private_consumption(plan=plan, amount=2)
        transaction_3_timestamp = self.datetime_service.advance_time(timedelta(days=1))
        self.consumption_generator.create_private_consumption(plan=plan, amount=3)
        response = self.use_case.show_details(
            self.create_use_case_request(company_id=planner)
        )
        assert response.plot.timestamps[1] == transaction_1_timestamp
        assert response.plot.timestamps[3] == transaction_3_timestamp
        # production costs were one so we have to take this into
        # consideration when checking for accumulated account volume.
        assert response.plot.accumulated_volumes[1] == Decimal(0)
        assert response.plot.accumulated_volumes[3] == Decimal(5)

    def test_that_peer_type_is_accounting_when_transaction_is_debit_for_expected_sales(
        self,
    ) -> None:
        planner = self.company_generator.create_company()
        self.plan_generator.create_plan(planner=planner)
        response = self.use_case.show_details(
            self.create_use_case_request(company_id=planner)
        )
        assert isinstance(
            response.transactions[0].peer, show_prd_account_details.SocialAccountingPeer
        )

    def test_that_correct_accounting_id_is_shown_when_transaction_is_debit_for_expected_sales(
        self,
    ) -> None:
        planner = self.company_generator.create_company()
        self.plan_generator.create_plan(planner=planner)
        response = self.use_case.show_details(
            self.create_use_case_request(company_id=planner)
        )
        assert isinstance(
            response.transactions[0].peer, show_prd_account_details.SocialAccountingPeer
        )
        assert response.transactions[0].peer.id == self.social_accounting.id

    def test_that_peer_type_is_member_when_company_sold_to_member(
        self,
    ) -> None:
        expected_consumer_name = "test 123 name"
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=planner)
        consumer = self.member_generator.create_member(name=expected_consumer_name)
        self.consumption_generator.create_private_consumption(
            plan=plan, consumer=consumer
        )
        response = self.use_case.show_details(
            self.create_use_case_request(company_id=planner)
        )
        transaction_of_sale = response.transactions[0]
        assert isinstance(transaction_of_sale.peer, show_prd_account_details.MemberPeer)

    def test_that_correct_consumer_id_is_shown_when_company_sold_to_company(
        self,
    ) -> None:
        consumer = self.company_generator.create_company()
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=planner)
        self.consumption_generator.create_fixed_means_consumption(
            consumer=consumer, plan=plan
        )
        response = self.use_case.show_details(
            self.create_use_case_request(company_id=planner)
        )
        transaction_of_sale = response.transactions[0]
        assert isinstance(
            transaction_of_sale.peer, show_prd_account_details.CompanyPeer
        )
        assert transaction_of_sale.peer.id == consumer

    def test_that_correct_consumer_name_is_shown_when_company_sold_to_company(
        self,
    ) -> None:
        consumer = self.company_generator.create_company_record()
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=planner)
        self.consumption_generator.create_fixed_means_consumption(
            consumer=consumer.id, plan=plan
        )
        response = self.use_case.show_details(
            self.create_use_case_request(company_id=planner)
        )
        transaction_of_sale = response.transactions[0]
        assert isinstance(
            transaction_of_sale.peer, show_prd_account_details.CompanyPeer
        )
        assert transaction_of_sale.peer.name == consumer.name

    def create_use_case_request(
        self, company_id: UUID
    ) -> show_prd_account_details.Request:
        return show_prd_account_details.Request(company_id=company_id)
