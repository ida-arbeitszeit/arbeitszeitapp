from datetime import datetime
from decimal import Decimal
from uuid import UUID

from arbeitszeit.entities import SocialAccounting
from arbeitszeit_flask import models
from arbeitszeit_flask.database.repositories import TransactionRepository
from tests.data_generators import AccountGenerator, PlanGenerator
from tests.datetime_service import FakeDatetimeService

from .flask import FlaskTestCase


class TransactionRepositoryTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.account_generator = self.injector.get(AccountGenerator)
        self.repository: TransactionRepository = self.injector.get(
            TransactionRepository
        )
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
        transaction = self.repository.create_transaction(
            datetime.now(),
            sending_account=sender_account.id,
            receiving_account=receiver_account.id,
            amount_sent=Decimal(1),
            amount_received=Decimal(1),
            purpose="test purpose",
        )
        assert list(
            self.repository.get_transactions().where_account_is_receiver(
                receiver_account.id
            )
        ) == [transaction]

    def test_created_transactions_shows_up_in_all_transactions(
        self,
    ) -> None:
        sender_account = self.account_generator.create_account()
        receiver_account = self.account_generator.create_account()
        transaction = self.repository.create_transaction(
            datetime.now(),
            sending_account=sender_account.id,
            receiving_account=receiver_account.id,
            amount_sent=Decimal(1),
            amount_received=Decimal(1),
            purpose="test purpose",
        )
        assert list(self.repository.get_transactions()) == [transaction]

    def test_transactions_from_social_accounting_can_be_filtered(
        self,
    ) -> None:
        receiver_account = self.account_generator.create_account()
        transaction = self.repository.create_transaction(
            datetime.now(),
            sending_account=self.social_accounting.account.id,
            receiving_account=receiver_account.id,
            amount_sent=Decimal(1),
            amount_received=Decimal(1),
            purpose="test purpose",
        )
        assert list(
            self.repository.get_transactions().where_sender_is_social_accounting()
        ) == [transaction]

    def test_transactions_not_from_social_accounting_dont_show_up_when_filtering_for_transactions_from_social_accounting(
        self,
    ) -> None:
        sender_account = self.account_generator.create_account()
        receiver_account = self.account_generator.create_account()
        self.repository.create_transaction(
            datetime.now(),
            sending_account=sender_account.id,
            receiving_account=receiver_account.id,
            amount_sent=Decimal(1),
            amount_received=Decimal(1),
            purpose="test purpose",
        )
        assert (
            not self.repository.get_transactions().where_sender_is_social_accounting()
        )

    def test_that_transactions_can_be_ordered_by_transaction_date(
        self,
    ) -> None:
        sender_account = self.account_generator.create_account()
        receiver_account = self.account_generator.create_account()
        first_transaction = self.repository.create_transaction(
            datetime(2000, 1, 1),
            sending_account=sender_account.id,
            receiving_account=receiver_account.id,
            amount_sent=Decimal(1),
            amount_received=Decimal(1),
            purpose="test purpose",
        )
        second_transaction = self.repository.create_transaction(
            datetime(2000, 1, 2),
            sending_account=sender_account.id,
            receiving_account=receiver_account.id,
            amount_sent=Decimal(1),
            amount_received=Decimal(1),
            purpose="test purpose",
        )
        assert list(
            self.repository.get_transactions().ordered_by_transaction_date()
        ) == [first_transaction, second_transaction]
        assert list(
            self.repository.get_transactions().ordered_by_transaction_date(
                descending=True
            )
        ) == [second_transaction, first_transaction]

    def test_created_transactions_show_up_in_all_sent_received_by_account(self) -> None:
        sender_account = self.account_generator.create_account()
        receiver_account = self.account_generator.create_account()
        transaction = self.repository.create_transaction(
            datetime.now(),
            sending_account=sender_account.id,
            receiving_account=receiver_account.id,
            amount_sent=Decimal(1),
            amount_received=Decimal(1),
            purpose="test purpose",
        )
        assert list(
            self.repository.get_transactions().where_account_is_sender(
                sender_account.id
            )
        ) == [transaction]

    def test_correct_sales_balance_of_plan_gets_returned_after_one_transaction(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan()
        sender_account = self.account_generator.create_account()
        receiver_account = models.Account.query.filter(
            models.Account.id.in_(
                models.Company.query.filter(models.Company.id == str(plan.planner))
                .with_entities(models.Company.prd_account)
                .subquery()
                .select()
            ),
        ).first()
        account_balance_before_transaction = self.repository.get_sales_balance_of_plan(
            plan
        )
        self.repository.create_transaction(
            self.datetime_service.now(),
            sending_account=sender_account.id,
            receiving_account=UUID(receiver_account.id),
            amount_sent=Decimal(12),
            amount_received=Decimal(10),
            purpose=f"test {plan.id} test",
        )
        assert self.repository.get_sales_balance_of_plan(
            plan
        ) == account_balance_before_transaction + Decimal(10)

    def test_correct_sales_balance_of_plan_gets_returned_after_two_transactions(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan()
        sender_account_1 = self.account_generator.create_account()
        sender_account_2 = self.account_generator.create_account()
        receiver_account = models.Account.query.filter(
            models.Account.id.in_(
                models.Company.query.filter(models.Company.id == str(plan.planner))
                .with_entities(models.Company.prd_account)
                .subquery()
                .select()
            ),
        ).first()
        sales_balance_before_transactions = self.repository.get_sales_balance_of_plan(
            plan
        )
        self.repository.create_transaction(
            datetime.now(),
            sending_account=sender_account_1.id,
            receiving_account=UUID(receiver_account.id),
            amount_sent=Decimal(12),
            amount_received=Decimal(10),
            purpose=f"test {plan.id} test",
        )
        self.repository.create_transaction(
            datetime.now(),
            sending_account=sender_account_2.id,
            receiving_account=UUID(receiver_account.id),
            amount_sent=Decimal(12),
            amount_received=Decimal(15),
            purpose=f"test2 {plan.id} test2",
        )
        assert self.repository.get_sales_balance_of_plan(
            plan
        ) == sales_balance_before_transactions + Decimal(25)
