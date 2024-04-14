from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from arbeitszeit.records import SocialAccounting, Transaction
from arbeitszeit_flask.database.repositories import DatabaseGatewayImpl
from tests.control_thresholds import ControlThresholdsTestImpl
from tests.data_generators import (
    CompanyGenerator,
    ConsumptionGenerator,
    MemberGenerator,
    PlanGenerator,
)
from tests.datetime_service import FakeDatetimeService

from ..flask import FlaskTestCase


class TransactionRepositoryTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.database_gateway = self.injector.get(DatabaseGatewayImpl)
        self.plan_generator: PlanGenerator = self.injector.get(PlanGenerator)
        self.datetime_service: FakeDatetimeService = self.injector.get(
            FakeDatetimeService
        )
        self.social_accounting: SocialAccounting = self.injector.get(SocialAccounting)

    def test_created_transactions_show_up_in_all_transactions_received_by_account(
        self,
    ) -> None:
        sender_account = self.create_account()
        receiver_account = self.create_account()
        transaction = self.database_gateway.create_transaction(
            self.datetime_service.now(),
            sending_account=sender_account,
            receiving_account=receiver_account,
            amount_sent=Decimal(1),
            amount_received=Decimal(1),
            purpose="test purpose",
        )
        assert list(
            self.database_gateway.get_transactions().where_account_is_receiver(
                receiver_account
            )
        ) == [transaction]

    def test_created_transactions_shows_up_in_all_transactions(
        self,
    ) -> None:
        sender_account = self.create_account()
        receiver_account = self.create_account()
        transaction = self.database_gateway.create_transaction(
            self.datetime_service.now(),
            sending_account=sender_account,
            receiving_account=receiver_account,
            amount_sent=Decimal(1),
            amount_received=Decimal(1),
            purpose="test purpose",
        )
        assert list(self.database_gateway.get_transactions()) == [transaction]

    def test_transactions_from_social_accounting_can_be_filtered(
        self,
    ) -> None:
        receiver_account = self.create_account()
        transaction = self.database_gateway.create_transaction(
            self.datetime_service.now(),
            sending_account=self.social_accounting.account,
            receiving_account=receiver_account,
            amount_sent=Decimal(1),
            amount_received=Decimal(1),
            purpose="test purpose",
        )
        assert list(
            self.database_gateway.get_transactions().where_sender_is_social_accounting()
        ) == [transaction]

    def test_transactions_from_labour_accounts_can_be_filtered(
        self,
    ) -> None:
        labour_sending_account_from_company_one = self.database_gateway.create_account()
        labour_sending_account_from_company_two = self.database_gateway.create_account()
        labour_sending_account_from_company_three = (
            self.database_gateway.create_account()
        )

        worker_receiver_account_one = self.create_account()
        worker_receiver_account_two = self.create_account()
        worker_receiver_account_three = self.create_account()

        transaction_one = self.database_gateway.create_transaction(
            self.datetime_service.now(),
            sending_account=labour_sending_account_from_company_one.id,
            receiving_account=worker_receiver_account_one,
            amount_sent=Decimal(1),
            amount_received=Decimal(1),
            purpose="test purpose 1",
        )

        transaction_two = self.database_gateway.create_transaction(
            self.datetime_service.now(),
            sending_account=labour_sending_account_from_company_two.id,
            receiving_account=worker_receiver_account_two,
            amount_sent=Decimal(2),
            amount_received=Decimal(2),
            purpose="test purpose 2",
        )

        transaction_three = self.database_gateway.create_transaction(
            self.datetime_service.now(),
            sending_account=labour_sending_account_from_company_three.id,
            receiving_account=worker_receiver_account_three,
            amount_sent=Decimal(3),
            amount_received=Decimal(3),
            purpose="test purpose 3",
        )

        all_accounts = self.database_gateway.get_accounts()
        assert list(
            self.database_gateway.get_transactions().where_sender_is_labour_account(
                all_accounts
            )
        ) == [transaction_one, transaction_two, transaction_three]

    def test_transactions_not_from_social_accounting_dont_show_up_when_filtering_for_transactions_from_social_accounting(
        self,
    ) -> None:
        sender_account = self.create_account()
        receiver_account = self.create_account()
        self.database_gateway.create_transaction(
            self.datetime_service.now(),
            sending_account=sender_account,
            receiving_account=receiver_account,
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
        sender_account = self.create_account()
        receiver_account = self.create_account()
        first_transaction = self.database_gateway.create_transaction(
            datetime(2000, 1, 1),
            sending_account=sender_account,
            receiving_account=receiver_account,
            amount_sent=Decimal(1),
            amount_received=Decimal(1),
            purpose="test purpose",
        )
        second_transaction = self.database_gateway.create_transaction(
            datetime(2000, 1, 2),
            sending_account=sender_account,
            receiving_account=receiver_account,
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
        sender_account = self.create_account()
        receiver_account = self.create_account()
        transaction = self.database_gateway.create_transaction(
            self.datetime_service.now(),
            sending_account=sender_account,
            receiving_account=receiver_account,
            amount_sent=Decimal(1),
            amount_received=Decimal(1),
            purpose="test purpose",
        )
        assert list(
            self.database_gateway.get_transactions().where_account_is_sender(
                sender_account
            )
        ) == [transaction]

    def create_account(self) -> UUID:
        return self.database_gateway.create_account().id


class TestWhereAccountIsSenderOrReceiver(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.database_gateway = self.injector.get(DatabaseGatewayImpl)
        self.datetime_service: FakeDatetimeService = self.injector.get(
            FakeDatetimeService
        )

    def test_transactions_are_presented_in_result_when_receiver_matches_account_id(
        self,
    ) -> None:
        sender_account = self.create_account()
        receiver_account = self.create_account()
        transaction = self.create_transaction(
            sender=sender_account, receiver=receiver_account
        )
        assert list(
            self.database_gateway.get_transactions().where_account_is_sender_or_receiver(
                receiver_account
            )
        ) == [transaction]

    def test_transactions_are_presented_in_result_when_sender_matches_account_id(
        self,
    ) -> None:
        sender_account = self.create_account()
        receiver_account = self.create_account()
        transaction = self.create_transaction(
            sender=sender_account, receiver=receiver_account
        )
        assert list(
            self.database_gateway.get_transactions().where_account_is_sender_or_receiver(
                sender_account
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

    def create_account(self) -> UUID:
        return self.database_gateway.create_account().id


class ThatWereASaleForPlanResultTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.database_gateway = self.injector.get(DatabaseGatewayImpl)
        self.plan_generator = self.injector.get(PlanGenerator)
        self.consumption_generator = self.injector.get(ConsumptionGenerator)
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

    def test_with_approved_plan_that_has_a_private_consumption_that_we_find_some_transactions(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan()
        self.consumption_generator.create_private_consumption(plan=plan)
        assert self.database_gateway.get_transactions().that_were_a_sale_for_plan()

    def test_with_approved_plan_that_has_a_fixed_means_consumption_that_we_find_some_transactions(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan()
        self.consumption_generator.create_fixed_means_consumption(plan=plan)
        assert self.database_gateway.get_transactions().that_were_a_sale_for_plan()

    def test_dont_show_find_transactions_for_newly_approved_plan_when_there_are_productive_consumptions_for_other_plans(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan()
        other_plan = self.plan_generator.create_plan()
        self.consumption_generator.create_fixed_means_consumption(plan=other_plan)
        assert not self.database_gateway.get_transactions().that_were_a_sale_for_plan(
            plan
        )

    def test_dont_show_find_transactions_for_newly_approved_plan_when_there_are_private_consumptions_for_other_plans(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan()
        other_plan = self.plan_generator.create_plan()
        self.consumption_generator.create_private_consumption(plan=other_plan)
        assert not self.database_gateway.get_transactions().that_were_a_sale_for_plan(
            plan
        )


class JoinedWithSenderAndReceiverTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.database_gateway = self.injector.get(DatabaseGatewayImpl)
        self.member_generator = self.injector.get(MemberGenerator)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.social_accounting: SocialAccounting = self.injector.get(SocialAccounting)

    def test_that_with_no_transactions_in_db_the_joined_result_set_is_empty(
        self,
    ) -> None:
        assert (
            len(
                self.database_gateway.get_transactions().joined_with_sender_and_receiver()
            )
            == 0
        )

    def test_that_sender_is_correctly_retrieved_for_transaction_from_member_account(
        self,
    ) -> None:
        member = self.member_generator.create_member()
        account = self.database_gateway.get_accounts().owned_by_member(member).first()
        assert account
        self.create_transaction(sender=account.id)
        transactions = self.database_gateway.get_transactions().where_account_is_sender(
            account.id
        )
        _, sender, _ = transactions.joined_with_sender_and_receiver().first()  # type: ignore
        assert sender.id == member

    def test_that_sender_is_correctly_retrieved_for_transaction_from_company_r_account(
        self,
    ) -> None:
        company = self.company_generator.create_company_record()
        self.create_transaction(sender=company.raw_material_account)
        transactions = self.database_gateway.get_transactions().where_account_is_sender(
            company.raw_material_account
        )
        _, sender, _ = transactions.joined_with_sender_and_receiver().first()  # type: ignore
        assert sender == company

    def test_that_sender_is_correctly_retrieved_for_transactions_from_company_p_account(
        self,
    ) -> None:
        company = self.company_generator.create_company_record()
        self.create_transaction(sender=company.means_account)
        transactions = self.database_gateway.get_transactions().where_account_is_sender(
            company.means_account
        )
        _, sender, _ = transactions.joined_with_sender_and_receiver().first()  # type: ignore
        assert sender == company

    def test_that_sender_is_correctly_retrieved_for_transaction_from_company_a_account(
        self,
    ) -> None:
        company = self.company_generator.create_company_record()
        self.create_transaction(sender=company.work_account)
        transactions = self.database_gateway.get_transactions().where_account_is_sender(
            company.work_account
        )
        _, sender, _ = transactions.joined_with_sender_and_receiver().first()  # type: ignore
        assert sender == company

    def test_that_sender_is_correctly_retrieved_for_transactions_from_company_prd_account(
        self,
    ) -> None:
        company = self.company_generator.create_company_record()
        self.create_transaction(sender=company.product_account)
        transactions = self.database_gateway.get_transactions().where_account_is_sender(
            company.product_account
        )
        _, sender, _ = transactions.joined_with_sender_and_receiver().first()  # type: ignore
        assert sender == company

    def test_that_sender_is_correctly_retrieved_for_transactions_from_social_accounting(
        self,
    ) -> None:
        self.create_transaction(sender=self.social_accounting.account)
        transactions = self.database_gateway.get_transactions().where_account_is_sender(
            self.social_accounting.account
        )
        _, sender, _ = transactions.joined_with_sender_and_receiver().first()  # type: ignore
        assert sender == self.social_accounting

    def test_that_receiver_is_correctly_retrieved_for_transaction_to_member_account(
        self,
    ) -> None:
        member = self.member_generator.create_member()
        account = self.database_gateway.get_accounts().owned_by_member(member).first()
        assert account
        self.create_transaction(receiver=account.id)
        transactions = (
            self.database_gateway.get_transactions().where_account_is_receiver(
                account.id
            )
        )
        _, _, receiver = transactions.joined_with_sender_and_receiver().first()  # type: ignore
        assert receiver.id == member

    def test_that_receiver_is_correctly_retrieved_for_transaction_to_company_r_account(
        self,
    ) -> None:
        company = self.company_generator.create_company_record()
        self.create_transaction(receiver=company.raw_material_account)
        transactions = (
            self.database_gateway.get_transactions().where_account_is_receiver(
                company.raw_material_account
            )
        )
        _, _, receiver = transactions.joined_with_sender_and_receiver().first()  # type: ignore
        assert receiver == company

    def test_that_receiver_is_correctly_retrieved_for_transactions_to_company_p_account(
        self,
    ) -> None:
        company = self.company_generator.create_company_record()
        self.create_transaction(receiver=company.means_account)
        transactions = (
            self.database_gateway.get_transactions().where_account_is_receiver(
                company.means_account
            )
        )
        _, _, receiver = transactions.joined_with_sender_and_receiver().first()  # type: ignore
        assert receiver == company

    def test_that_receiver_is_correctly_retrieved_for_transaction_to_company_a_account(
        self,
    ) -> None:
        company = self.company_generator.create_company_record()
        self.create_transaction(receiver=company.work_account)
        transactions = (
            self.database_gateway.get_transactions().where_account_is_receiver(
                company.work_account
            )
        )
        _, _, receiver = transactions.joined_with_sender_and_receiver().first()  # type: ignore
        assert receiver == company

    def test_that_receiver_is_correctly_retrieved_for_transactions_to_company_prd_account(
        self,
    ) -> None:
        company = self.company_generator.create_company_record()
        self.create_transaction(receiver=company.product_account)
        transactions = (
            self.database_gateway.get_transactions().where_account_is_receiver(
                company.product_account
            )
        )
        _, _, receiver = transactions.joined_with_sender_and_receiver().first()  # type: ignore
        assert receiver == company

    def test_that_receiver_is_correctly_retrieved_for_transactions_to_accounting(
        self,
    ) -> None:
        self.create_transaction(receiver=self.social_accounting.account)
        transactions = (
            self.database_gateway.get_transactions().where_account_is_receiver(
                self.social_accounting.account
            )
        )
        _, _, receiver = transactions.joined_with_sender_and_receiver().first()  # type: ignore
        assert receiver == self.social_accounting

    def create_transaction(
        self, sender: Optional[UUID] = None, receiver: Optional[UUID] = None
    ) -> None:
        if sender is None:
            sender = self.create_member_account()
        if receiver is None:
            receiver = self.create_member_account()
        self.database_gateway.create_transaction(
            date=datetime(2000, 1, 1),
            sending_account=sender,
            receiving_account=receiver,
            amount_sent=Decimal(1),
            amount_received=Decimal(1),
            purpose="test purpose",
        )

    def create_member_account(self) -> UUID:
        result = (
            self.database_gateway.get_accounts()
            .owned_by_member(self.member_generator.create_member())
            .first()
        )
        assert result
        return result.id
