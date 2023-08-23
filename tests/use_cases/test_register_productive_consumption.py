from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID, uuid4

from arbeitszeit.records import Company, ConsumptionType, ProductionCosts
from arbeitszeit.use_cases.get_company_transactions import GetCompanyTransactions
from arbeitszeit.use_cases.query_company_consumptions import QueryCompanyConsumptions
from arbeitszeit.use_cases.register_productive_consumption import (
    RegisterProductiveConsumption,
    RegisterProductiveConsumptionRequest,
)
from arbeitszeit_web.www.presenters.get_company_transactions_presenter import (
    GetCompanyTransactionsResponse,
)

from .base_test_case import BaseTestCase
from .repositories import MockDatabase


class RegisterProductiveConsumptionTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.register_productive_consumption = self.injector.get(
            RegisterProductiveConsumption
        )
        self.mock_database = self.injector.get(MockDatabase)
        self.query_company_consumptions = self.injector.get(QueryCompanyConsumptions)

    def test_reject_registration_if_plan_is_expired(self) -> None:
        self.datetime_service.freeze_time(datetime(2000, 1, 1))
        sender = self.company_generator.create_company_record()
        plan = self.plan_generator.create_plan(timeframe=1)
        self.datetime_service.freeze_time(datetime(2001, 1, 1))
        consumption_type = ConsumptionType.means_of_prod
        pieces = 5
        response = self.register_productive_consumption(
            RegisterProductiveConsumptionRequest(
                sender.id, plan.id, pieces, consumption_type
            )
        )
        assert response.is_rejected
        assert response.rejection_reason == response.RejectionReason.plan_is_not_active

    def test_registration_is_rejected_when_consumption_type_is_private_consumption(
        self,
    ) -> None:
        sender = self.company_generator.create_company_record()
        plan = self.plan_generator.create_plan()
        consumption_type = ConsumptionType.consumption
        response = self.register_productive_consumption(
            RegisterProductiveConsumptionRequest(
                sender.id, plan.id, 5, consumption_type
            )
        )
        assert response.is_rejected
        assert (
            response.rejection_reason
            == response.RejectionReason.invalid_consumption_type
        )

    def test_reject_registration_trying_to_consume_public_service(self) -> None:
        sender = self.company_generator.create_company_record()
        plan = self.plan_generator.create_plan(is_public_service=True)
        consumption_type = ConsumptionType.means_of_prod
        response = self.register_productive_consumption(
            RegisterProductiveConsumptionRequest(
                sender.id, plan.id, 5, consumption_type
            )
        )
        assert response.is_rejected
        assert (
            response.rejection_reason
            == response.RejectionReason.cannot_consume_public_service
        )

    def test_reject_registration_trying_to_consume_own_product(self) -> None:
        sender = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(planner=sender)
        consumption_type = ConsumptionType.means_of_prod
        response = self.register_productive_consumption(
            RegisterProductiveConsumptionRequest(sender, plan.id, 5, consumption_type)
        )
        assert response.is_rejected
        assert response.rejection_reason == response.RejectionReason.consumer_is_planner

    def test_balance_of_consumer_gets_reduced(self) -> None:
        sender = self.company_generator.create_company()
        plan = self.plan_generator.create_plan()
        consumption_type = ConsumptionType.means_of_prod
        pieces = 5

        self.register_productive_consumption(
            RegisterProductiveConsumptionRequest(
                sender, plan.id, pieces, consumption_type
            )
        )

        price_total = pieces * self.price_checker.get_unit_price(plan.id)
        assert (
            self.balance_checker.get_company_account_balances(sender).p_account
            == -price_total
        )

    def test_balance_of_consumer_of_raw_materials_reduced(self) -> None:
        sender = self.company_generator.create_company()
        plan = self.plan_generator.create_plan()
        consumption_type = ConsumptionType.raw_materials
        pieces = 5

        self.register_productive_consumption(
            RegisterProductiveConsumptionRequest(
                sender, plan.id, pieces, consumption_type
            )
        )

        price_total = pieces * self.price_checker.get_unit_price(plan.id)
        assert (
            self.balance_checker.get_company_account_balances(sender).r_account
            == -price_total
        )

    def test_balance_of_seller_increased(self) -> None:
        sender = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(
            costs=ProductionCosts(
                labour_cost=Decimal(1),
                means_cost=Decimal(1),
                resource_cost=Decimal(1),
            ),
            amount=5,
        )
        consumption_type = ConsumptionType.raw_materials
        pieces = 5
        assert self.balance_checker.get_company_account_balances(
            plan.planner
        ).prd_account == Decimal("-3")
        self.register_productive_consumption(
            RegisterProductiveConsumptionRequest(
                sender, plan.id, pieces, consumption_type
            )
        )
        assert self.balance_checker.get_company_account_balances(
            plan.planner
        ).prd_account == Decimal("0")

    def test_balance_of_seller_increased_correctly_when_plan_is_in_cooperation(
        self,
    ) -> None:
        coop = self.cooperation_generator.create_cooperation()
        sender = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(amount=50, cooperation=coop)
        self.plan_generator.create_plan(amount=200, cooperation=coop)
        consumption_type = ConsumptionType.raw_materials
        pieces = 5
        balance_before_transaction = self.balance_checker.get_company_account_balances(
            plan.planner
        ).prd_account
        self.register_productive_consumption(
            RegisterProductiveConsumptionRequest(
                sender, plan.id, pieces, consumption_type
            )
        )
        assert (
            self.balance_checker.get_company_account_balances(plan.planner).prd_account
            == balance_before_transaction
            + self.price_checker.get_unit_cost(plan.id) * 5
        )

    def test_that_unit_cost_for_cooperating_plans_only_considers_non_expired_plans(
        self,
    ) -> None:
        self.datetime_service.freeze_time(datetime(2010, 1, 1))
        coop = self.cooperation_generator.create_cooperation()
        sender = self.company_generator.create_company()
        self.plan_generator.create_plan(
            cooperation=coop,
            timeframe=1,
            amount=1,
            costs=ProductionCosts(
                labour_cost=Decimal(10), means_cost=Decimal(0), resource_cost=Decimal(0)
            ),
        )
        plan = self.plan_generator.create_plan(
            amount=1,
            cooperation=coop,
            timeframe=10,
            costs=ProductionCosts(
                labour_cost=Decimal(1), means_cost=Decimal(0), resource_cost=Decimal(0)
            ),
        )
        self.datetime_service.advance_time(timedelta(days=2))
        consumption_type = ConsumptionType.raw_materials
        balance_before_transaction = self.balance_checker.get_company_account_balances(
            sender
        ).r_account
        self.register_productive_consumption(
            RegisterProductiveConsumptionRequest(sender, plan.id, 1, consumption_type)
        )
        assert self.balance_checker.get_company_account_balances(
            sender
        ).r_account == balance_before_transaction - Decimal(1)

    def test_correct_transaction_added_if_means_of_production_were_consumed(
        self,
    ) -> None:
        sender = self.company_generator.create_company_record()
        plan = self.plan_generator.create_plan()
        consumption_type = ConsumptionType.means_of_prod
        pieces = 5
        transactions_before_payment = len(self.mock_database.get_transactions())
        self.register_productive_consumption(
            RegisterProductiveConsumptionRequest(
                sender.id, plan.id, pieces, consumption_type
            )
        )
        price_total = pieces * self.price_checker.get_unit_price(plan.id)
        assert (
            len(self.mock_database.get_transactions())
            == transactions_before_payment + 1
        )
        latest_transaction = (
            self.mock_database.get_transactions()
            .ordered_by_transaction_date(descending=True)
            .first()
        )
        assert latest_transaction
        assert latest_transaction.sending_account == sender.means_account
        assert latest_transaction.receiving_account == self.get_product_account(
            plan.planner
        )
        assert latest_transaction.amount_sent == price_total
        assert latest_transaction.amount_received == price_total

    def test_correct_transaction_added_if_raw_materials_were_consumed(self) -> None:
        sender = self.company_generator.create_company_record()
        plan = self.plan_generator.create_plan()
        consumption_type = ConsumptionType.raw_materials
        pieces = 5
        transactions_before_payment = len(self.mock_database.get_transactions())
        self.register_productive_consumption(
            RegisterProductiveConsumptionRequest(
                sender.id, plan.id, pieces, consumption_type
            )
        )
        price_total = pieces * self.price_checker.get_unit_price(plan.id)
        assert (
            len(self.mock_database.get_transactions())
            == transactions_before_payment + 1
        )
        latest_transaction = (
            self.mock_database.get_transactions()
            .ordered_by_transaction_date(descending=True)
            .first()
        )
        assert latest_transaction
        assert latest_transaction.sending_account == sender.raw_material_account
        assert latest_transaction.receiving_account == self.get_product_account(
            plan.planner
        )
        assert latest_transaction.amount_sent == price_total
        assert latest_transaction.amount_received == price_total

    def test_correct_consumption_added_if_means_of_production_were_consumed(
        self,
    ) -> None:
        sender = self.company_generator.create_company_record()
        plan = self.plan_generator.create_plan()
        consumption_type = ConsumptionType.means_of_prod
        pieces = 5
        self.register_productive_consumption(
            RegisterProductiveConsumptionRequest(
                sender.id, plan.id, pieces, consumption_type
            )
        )
        consumptions = list(self.query_company_consumptions(sender.id))
        assert len(consumptions) == 1
        latest_consumption = consumptions[0]
        assert latest_consumption.plan_id == plan.id
        assert latest_consumption.price_per_unit == self.price_checker.get_unit_price(
            plan.id
        )
        assert latest_consumption.amount == pieces
        assert latest_consumption.consumption_type == ConsumptionType.means_of_prod

    def test_correct_consumption_added_if_raw_materials_were_consumed(self) -> None:
        sender = self.company_generator.create_company_record()
        plan = self.plan_generator.create_plan()
        consumption_type = ConsumptionType.raw_materials
        pieces = 5
        self.register_productive_consumption(
            RegisterProductiveConsumptionRequest(
                sender.id, plan.id, pieces, consumption_type
            )
        )
        consumptions = list(self.query_company_consumptions(sender.id))
        assert len(consumptions) == 1
        latest_consumption = consumptions[0]
        assert latest_consumption.plan_id == plan.id
        assert latest_consumption.price_per_unit == self.price_checker.get_unit_price(
            plan.id
        )
        assert latest_consumption.amount == pieces
        assert latest_consumption.consumption_type == ConsumptionType.raw_materials

    def test_plan_not_found_rejects_registration(self) -> None:
        consumer = self.company_generator.create_company_record()
        response = self.register_productive_consumption(
            RegisterProductiveConsumptionRequest(
                consumer=consumer.id,
                plan=uuid4(),
                amount=1,
                consumption_type=ConsumptionType.means_of_prod,
            )
        )
        assert response.is_rejected
        assert response.rejection_reason == response.RejectionReason.plan_not_found

    def test_plan_found_accepts_registration(self) -> None:
        consumer = self.company_generator.create_company_record()
        plan = self.plan_generator.create_plan()
        response = self.register_productive_consumption(
            RegisterProductiveConsumptionRequest(
                consumer=consumer.id,
                plan=plan.id,
                amount=1,
                consumption_type=ConsumptionType.means_of_prod,
            )
        )
        assert not response.is_rejected
        assert response.rejection_reason is None

    def get_product_account(self, company: UUID) -> UUID:
        company_model = self.mock_database.get_companies().with_id(company).first()
        assert company_model
        return company_model.product_account


class TestSuccessfulRegistrationTransactions(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.transaction_time = datetime(2020, 10, 1, 22, 30)
        self.datetime_service.freeze_time(self.transaction_time)
        self.consumer = self.company_generator.create_company_record()
        self.planner = self.company_generator.create_company()
        self.plan = self.plan_generator.create_plan(planner=self.planner, timeframe=2)
        self.register_productive_consumption = self.injector.get(
            RegisterProductiveConsumption
        )
        self.get_company_transactions = self.injector.get(GetCompanyTransactions)
        self.planner_transactions_before_payment = len(
            self.get_company_transactions(self.planner).transactions
        )
        self.response = self.register_productive_consumption(
            RegisterProductiveConsumptionRequest(
                consumer=self.consumer.id,
                plan=self.plan.id,
                amount=1,
                consumption_type=ConsumptionType.means_of_prod,
            )
        )
        self.datetime_service.advance_time(timedelta(days=1))

    def test_transaction_shows_up_in_transaction_listing_for_consumer(self) -> None:
        transaction_info = self.get_consumer_transaction_infos(self.consumer)
        self.assertEqual(len(transaction_info.transactions), 1)

    def test_transaction_shows_up_in_transaction_listing_for_planner(self) -> None:
        transaction_info = self.get_company_transactions(self.planner)
        self.assertEqual(
            len(transaction_info.transactions),
            self.planner_transactions_before_payment + 1,
        )

    def test_transaction_info_of_consumer_shows_transaction_timestamp(self) -> None:
        transaction_info = self.get_company_transactions(self.consumer.id)
        assert not self.response.is_rejected
        self.assertEqual(transaction_info.transactions[0].date, self.transaction_time)

    def test_transaction_info_of_planner_shows_transaction_timestamp(self) -> None:
        transaction_info = self.get_company_transactions(self.planner)
        self.assertEqual(transaction_info.transactions[-1].date, self.transaction_time)

    def get_consumer_transaction_infos(
        self, user: Company
    ) -> GetCompanyTransactionsResponse:
        return self.get_company_transactions(user.id)
