from datetime import datetime, timedelta
from decimal import Decimal

from arbeitszeit.records import AccountTypes, ProductionCosts
from arbeitszeit.transactions import TransactionTypes
from arbeitszeit.use_cases.get_company_transactions import GetCompanyTransactions

from .base_test_case import BaseTestCase


class GetCompanyTransactionsUseCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.get_company_transactions = self.injector.get(GetCompanyTransactions)

    def test_that_no_info_is_generated_when_no_transaction_took_place(self) -> None:
        company = self.company_generator.create_company()
        info = self.get_company_transactions(company)
        assert not info.transactions

    def test_that_response_contains_the_company_id_from_the_request(self) -> None:
        company = self.company_generator.create_company()
        response = self.get_company_transactions(company)
        assert response.company_id == company

    def test_that_correct_info_is_generated_after_member_consumes_product(
        self,
    ) -> None:
        self.control_thresholds.set_allowed_overdraw_of_member_account(10)
        company = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(
            planner=company,
            costs=ProductionCosts(
                labour_cost=Decimal(1),
                resource_cost=Decimal(1),
                means_cost=Decimal(1),
            ),
            amount=1,
        )
        info_company = self.get_company_transactions(company)
        transactions_before = len(info_company.transactions)
        self.consumption_generator.create_private_consumption(plan=plan, amount=1)
        info_company = self.get_company_transactions(company)
        assert len(info_company.transactions) == transactions_before + 1
        transaction = info_company.transactions[0]
        assert transaction.transaction_type == TransactionTypes.sale_of_consumer_product
        assert transaction.transaction_volume == Decimal(3)
        assert transaction.account_type == AccountTypes.prd

    def test_that_correct_info_for_sender_is_generated_after_transaction_of_company_consuming_p(
        self,
    ) -> None:
        company1 = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(
            amount=1,
            costs=ProductionCosts(
                labour_cost=Decimal(12),
                resource_cost=Decimal(0),
                means_cost=Decimal(0),
            ),
        )
        self.consumption_generator.create_fixed_means_consumption(
            consumer=company1, plan=plan
        )
        info_sender = self.get_company_transactions(company1)
        transaction = info_sender.transactions[0]
        assert (
            transaction.transaction_type == TransactionTypes.consumption_of_fixed_means
        )
        assert transaction.transaction_volume == Decimal(-12)
        assert transaction.account_type == AccountTypes.p

    def test_that_correct_info_for_receiver_is_generated_after_transaction_of_company_consuming_p(
        self,
    ) -> None:
        company1 = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(
            planner=company1,
            costs=ProductionCosts(
                labour_cost=Decimal("12.5"),
                means_cost=Decimal(0),
                resource_cost=Decimal(0),
            ),
            amount=1,
        )
        self.consumption_generator.create_fixed_means_consumption(plan=plan)
        info_receiver = self.get_company_transactions(company1)
        transaction = info_receiver.transactions[0]
        assert transaction.transaction_type == TransactionTypes.sale_of_fixed_means
        assert transaction.transaction_volume == Decimal("12.5")
        assert transaction.account_type == AccountTypes.prd

    def test_that_correct_info_for_company_is_generated_after_transaction_where_credit_for_p_is_granted(
        self,
    ) -> None:
        expected_p_amount = Decimal(4)
        expected_r_amount = Decimal(7)
        expected_prd_amount = Decimal(-15)
        company = self.company_generator.create_company()
        self.plan_generator.create_plan(
            planner=company,
            costs=ProductionCosts(
                means_cost=expected_p_amount,
                resource_cost=expected_r_amount,
                labour_cost=Decimal(4),
            ),
        )
        info_receiver = self.get_company_transactions(company)
        assert len(info_receiver.transactions) == 4
        transaction_volumes = [t.transaction_volume for t in info_receiver.transactions]
        assert expected_p_amount in transaction_volumes
        assert expected_r_amount in transaction_volumes
        assert expected_prd_amount in transaction_volumes
        transaction_purposes = [t.transaction_type for t in info_receiver.transactions]
        assert TransactionTypes.credit_for_fixed_means in transaction_purposes
        assert TransactionTypes.credit_for_liquid_means in transaction_purposes
        assert TransactionTypes.expected_sales in transaction_purposes

    def test_that_correct_info_for_company_is_generated_after_transaction_where_credit_for_a_is_granted(
        self,
    ) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        company = self.company_generator.create_company()
        self.plan_generator.create_plan(
            planner=company,
            costs=ProductionCosts(
                labour_cost=Decimal(10),
                means_cost=Decimal(0),
                resource_cost=Decimal(0),
            ),
            timeframe=1,
        )
        self.datetime_service.advance_time(timedelta(days=1))
        info_receiver = self.get_company_transactions(company)
        assert info_receiver.transactions[3].transaction_volume == Decimal(10)
        assert (
            info_receiver.transactions[3].transaction_type
            == TransactionTypes.credit_for_wages
        )

    def test_correct_info_is_generated_after_several_transactions_where_companies_consume_each_others_product(
        self,
    ) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        company1 = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=company1)
        self.datetime_service.advance_time(timedelta(hours=1))
        self.consumption_generator.create_fixed_means_consumption(
            consumer=company1,
        )
        self.datetime_service.advance_time(timedelta(hours=1))
        self.consumption_generator.create_fixed_means_consumption(
            plan=plan,
        )
        self.datetime_service.advance_time(timedelta(hours=1))
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=company1,
        )
        self.datetime_service.advance_time(timedelta(hours=1))
        info_company1 = self.get_company_transactions(company1)
        trans1 = info_company1.transactions[2]
        assert trans1.transaction_type == TransactionTypes.consumption_of_fixed_means
        trans2 = info_company1.transactions[1]
        assert trans2.transaction_type == TransactionTypes.sale_of_fixed_means
        trans3 = info_company1.transactions[0]
        assert trans3.transaction_type == TransactionTypes.consumption_of_liquid_means

    def test_that_correct_info_for_company_is_generated_in_correct_order_after_several_transactions_of_different_kind(
        self,
    ) -> None:
        self.control_thresholds.set_allowed_overdraw_of_member_account(100)
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        company1 = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=company1)
        self.datetime_service.advance_time(timedelta(hours=1))
        self.consumption_generator.create_fixed_means_consumption(consumer=company1)
        self.datetime_service.advance_time(timedelta(hours=1))
        self.consumption_generator.create_fixed_means_consumption(plan=plan)
        self.datetime_service.advance_time(timedelta(hours=1))
        self.consumption_generator.create_resource_consumption_by_company(
            consumer=company1
        )
        self.datetime_service.advance_time(timedelta(hours=1))
        self.consumption_generator.create_private_consumption(plan=plan)
        self.datetime_service.advance_time(timedelta(hours=1))
        info = self.get_company_transactions(company1)
        # trans1
        trans1 = info.transactions[3]
        assert trans1.transaction_type == TransactionTypes.consumption_of_fixed_means
        # trans2
        trans2 = info.transactions[2]
        assert trans2.transaction_type == TransactionTypes.sale_of_fixed_means
        # trans3
        trans3 = info.transactions[1]
        assert trans3.transaction_type == TransactionTypes.consumption_of_liquid_means
        # trans4
        trans4 = info.transactions[0]
        assert trans4.transaction_type == TransactionTypes.sale_of_consumer_product
