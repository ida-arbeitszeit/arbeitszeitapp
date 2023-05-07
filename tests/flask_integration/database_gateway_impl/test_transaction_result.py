from datetime import datetime
from decimal import Decimal
from uuid import UUID

from arbeitszeit.entities import SocialAccounting, Transaction
from arbeitszeit_flask.database.repositories import DatabaseGatewayImpl
from tests.control_thresholds import ControlThresholdsTestImpl
from tests.data_generators import AccountGenerator, PlanGenerator, PurchaseGenerator
from tests.datetime_service import FakeDatetimeService

from ..flask import FlaskTestCase


class TransactionRepositoryTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.account_generator = self.injector.get(AccountGenerator)
        self.database_gateway = self.injector.get(DatabaseGatewayImpl)
        self.plan_generator: PlanGenerator = self.injector.get(PlanGenerator)
        self.datetime_service: FakeDatetimeService = self.injector.get(
            FakeDatetimeService
        )
        self.social_accounting: SocialAccounting = self.injector.get(SocialAccounting)

    def test_created_transactions_show_up_in_all_transactions_received_by_account(
        self,
    ) -> None:
        sender_account = self.account_generator.create_account()
        receiver_account = self.account_generator.create_account()
        transaction = self.database_gateway.create_transaction(
            self.datetime_service.now(),
            sending_account=sender_account.id,
            receiving_account=receiver_account.id,
            amount_sent=Decimal(1),
            amount_received=Decimal(1),
            purpose="test purpose",
        )
        assert list(
            self.database_gateway.get_transactions().where_account_is_receiver(
                receiver_account.id
            )
        ) == [transaction]

    def test_created_transactions_shows_up_in_all_transactions(
        self,
    ) -> None:
        sender_account = self.account_generator.create_account()
        receiver_account = self.account_generator.create_account()
        transaction = self.database_gateway.create_transaction(
            self.datetime_service.now(),
            sending_account=sender_account.id,
            receiving_account=receiver_account.id,
            amount_sent=Decimal(1),
            amount_received=Decimal(1),
            purpose="test purpose",
        )
        assert list(self.database_gateway.get_transactions()) == [transaction]

    def test_transactions_from_social_accounting_can_be_filtered(
        self,
    ) -> None:
        receiver_account = self.account_generator.create_account()
        transaction = self.database_gateway.create_transaction(
            self.datetime_service.now(),
            sending_account=self.social_accounting.account,
            receiving_account=receiver_account.id,
            amount_sent=Decimal(1),
            amount_received=Decimal(1),
            purpose="test purpose",
        )
        assert list(
            self.database_gateway.get_transactions().where_sender_is_social_accounting()
        ) == [transaction]

    def test_transactions_not_from_social_accounting_dont_show_up_when_filtering_for_transactions_from_social_accounting(
        self,
    ) -> None:
        sender_account = self.account_generator.create_account()
        receiver_account = self.account_generator.create_account()
        self.database_gateway.create_transaction(
            self.datetime_service.now(),
            sending_account=sender_account.id,
            receiving_account=receiver_account.id,
            amount_sent=Decimal(1),
            amount_received=Decimal(1),
            purpose="test purpose",
        )
        assert (
            not self.database_gateway.get_transactions().where_sender_is_social_accounting()
        )

    def test_that_transactions_can_be_ordered_by_transaction_date(
        self,
    ) -> None:
        sender_account = self.account_generator.create_account()
        receiver_account = self.account_generator.create_account()
        first_transaction = self.database_gateway.create_transaction(
            datetime(2000, 1, 1),
            sending_account=sender_account.id,
            receiving_account=receiver_account.id,
            amount_sent=Decimal(1),
            amount_received=Decimal(1),
            purpose="test purpose",
        )
        second_transaction = self.database_gateway.create_transaction(
            datetime(2000, 1, 2),
            sending_account=sender_account.id,
            receiving_account=receiver_account.id,
            amount_sent=Decimal(1),
            amount_received=Decimal(1),
            purpose="test purpose",
        )
        assert list(
            self.database_gateway.get_transactions().ordered_by_transaction_date()
        ) == [first_transaction, second_transaction]
        assert list(
            self.database_gateway.get_transactions().ordered_by_transaction_date(
                descending=True
            )
        ) == [second_transaction, first_transaction]

    def test_created_transactions_show_up_in_all_sent_received_by_account(self) -> None:
        sender_account = self.account_generator.create_account()
        receiver_account = self.account_generator.create_account()
        transaction = self.database_gateway.create_transaction(
            self.datetime_service.now(),
            sending_account=sender_account.id,
            receiving_account=receiver_account.id,
            amount_sent=Decimal(1),
            amount_received=Decimal(1),
            purpose="test purpose",
        )
        assert list(
            self.database_gateway.get_transactions().where_account_is_sender(
                sender_account.id
            )
        ) == [transaction]


class TestWhereAccountIsSenderOrReceiver(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.account_generator = self.injector.get(AccountGenerator)
        self.database_gateway = self.injector.get(DatabaseGatewayImpl)
        self.datetime_service: FakeDatetimeService = self.injector.get(
            FakeDatetimeService
        )

    def test_transactions_are_presented_in_result_when_receiver_matches_account_id(
        self,
    ) -> None:
        sender_account = self.account_generator.create_account()
        receiver_account = self.account_generator.create_account()
        transaction = self.create_transaction(
            sender=sender_account.id, receiver=receiver_account.id
        )
        assert list(
            self.database_gateway.get_transactions().where_account_is_sender_or_receiver(
                receiver_account.id
            )
        ) == [transaction]

    def test_transactions_are_presented_in_result_when_sender_matches_account_id(
        self,
    ) -> None:
        sender_account = self.account_generator.create_account()
        receiver_account = self.account_generator.create_account()
        transaction = self.create_transaction(
            sender=sender_account.id, receiver=receiver_account.id
        )
        assert list(
            self.database_gateway.get_transactions().where_account_is_sender_or_receiver(
                sender_account.id
            )
        ) == [transaction]

    def create_transaction(self, *, sender: UUID, receiver: UUID) -> Transaction:
        return self.database_gateway.create_transaction(
            self.datetime_service.now(),
            sending_account=sender,
            receiving_account=receiver,
            amount_sent=Decimal(1),
            amount_received=Decimal(1),
            purpose="test purpose",
        )


class ThatWereASaleForPlanResultTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.database_gateway = self.injector.get(DatabaseGatewayImpl)
        self.plan_generator = self.injector.get(PlanGenerator)
        self.purchase_generator = self.injector.get(PurchaseGenerator)
        self.control_thresholds = self.injector.get(ControlThresholdsTestImpl)
        self.control_thresholds.set_allowed_overdraw_of_member_account(1000000)

    def test_that_without_any_transactions_in_db_nothing_is_returned(
        self,
    ) -> None:
        assert not self.database_gateway.get_transactions().that_were_a_sale_for_plan()

    def test_with_approved_plan_but_without_any_sales_dont_return_any_transactions(
        self,
    ) -> None:
        self.plan_generator.create_plan()
        assert not self.database_gateway.get_transactions().that_were_a_sale_for_plan()

    def test_with_approved_plan_that_has_a_consumer_purchase_that_we_find_some_transactions(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan()
        self.purchase_generator.create_purchase_by_member(plan=plan.id)
        assert self.database_gateway.get_transactions().that_were_a_sale_for_plan()

    def test_with_approved_plan_that_has_a_fixed_means_purchase_that_we_find_some_transactions(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan()
        self.purchase_generator.create_fixed_means_purchase(plan=plan.id)
        assert self.database_gateway.get_transactions().that_were_a_sale_for_plan()

    def test_dont_show_find_transactions_for_newly_approved_plan_when_there_are_company_purchases_for_other_plans(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan()
        other_plan = self.plan_generator.create_plan()
        self.purchase_generator.create_fixed_means_purchase(plan=other_plan.id)
        assert not self.database_gateway.get_transactions().that_were_a_sale_for_plan(
            plan.id
        )

    def test_dont_show_find_transactions_for_newly_approved_plan_when_there_are_consumer_purchase_for_other_plans(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan()
        other_plan = self.plan_generator.create_plan()
        self.purchase_generator.create_purchase_by_member(plan=other_plan.id)
        assert not self.database_gateway.get_transactions().that_were_a_sale_for_plan(
            plan.id
        )
