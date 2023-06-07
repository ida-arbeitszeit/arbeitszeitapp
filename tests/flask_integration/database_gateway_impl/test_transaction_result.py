from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from arbeitszeit.entities import SocialAccounting, Transaction
from arbeitszeit_flask.database.repositories import DatabaseGatewayImpl
from tests.control_thresholds import ControlThresholdsTestImpl
from tests.data_generators import (
    AccountGenerator,
    CompanyGenerator,
    MemberGenerator,
    PlanGenerator,
    PurchaseGenerator,
)
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
            plan=None,
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
            plan=None,
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
            plan=None,
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
            plan=None,
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
            plan=None,
        )
        second_transaction = self.database_gateway.create_transaction(
            datetime(2000, 1, 2),
            sending_account=sender_account.id,
            receiving_account=receiver_account.id,
            amount_sent=Decimal(1),
            amount_received=Decimal(1),
            plan=None,
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
            plan=None,
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
            plan=None,
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
        member = self.member_generator.create_member_entity()
        self.create_transaction(sender=member.account)
        transactions = self.database_gateway.get_transactions().where_account_is_sender(
            member.account
        )
        _, sender, _ = transactions.joined_with_sender_and_receiver().first()  # type: ignore
        assert sender == member

    def test_that_sender_is_correctly_retrieved_for_transaction_from_company_r_account(
        self,
    ) -> None:
        company = self.company_generator.create_company_entity()
        self.create_transaction(sender=company.raw_material_account)
        transactions = self.database_gateway.get_transactions().where_account_is_sender(
            company.raw_material_account
        )
        _, sender, _ = transactions.joined_with_sender_and_receiver().first()  # type: ignore
        assert sender == company

    def test_that_sender_is_correctly_retrieved_for_transactions_from_company_p_account(
        self,
    ) -> None:
        company = self.company_generator.create_company_entity()
        self.create_transaction(sender=company.means_account)
        transactions = self.database_gateway.get_transactions().where_account_is_sender(
            company.means_account
        )
        _, sender, _ = transactions.joined_with_sender_and_receiver().first()  # type: ignore
        assert sender == company

    def test_that_sender_is_correctly_retrieved_for_transaction_from_company_a_account(
        self,
    ) -> None:
        company = self.company_generator.create_company_entity()
        self.create_transaction(sender=company.work_account)
        transactions = self.database_gateway.get_transactions().where_account_is_sender(
            company.work_account
        )
        _, sender, _ = transactions.joined_with_sender_and_receiver().first()  # type: ignore
        assert sender == company

    def test_that_sender_is_correctly_retrieved_for_transactions_from_company_prd_account(
        self,
    ) -> None:
        company = self.company_generator.create_company_entity()
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
        member = self.member_generator.create_member_entity()
        self.create_transaction(receiver=member.account)
        transactions = (
            self.database_gateway.get_transactions().where_account_is_receiver(
                member.account
            )
        )
        _, _, receiver = transactions.joined_with_sender_and_receiver().first()  # type: ignore
        assert receiver == member

    def test_that_receiver_is_correctly_retrieved_for_transaction_to_company_r_account(
        self,
    ) -> None:
        company = self.company_generator.create_company_entity()
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
        company = self.company_generator.create_company_entity()
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
        company = self.company_generator.create_company_entity()
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
        company = self.company_generator.create_company_entity()
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
            sender = self.create_account()
        if receiver is None:
            receiver = self.create_account()
        self.database_gateway.create_transaction(
            date=datetime(2000, 1, 1),
            sending_account=sender,
            receiving_account=receiver,
            amount_sent=Decimal(1),
            amount_received=Decimal(1),
            plan=None,
        )

    def create_account(self) -> UUID:
        member = self.member_generator.create_member_entity()
        return member.account
