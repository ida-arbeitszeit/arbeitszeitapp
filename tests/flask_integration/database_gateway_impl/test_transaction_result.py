from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from parameterized import parameterized

from arbeitszeit.records import AccountTypes, SocialAccounting

from ..flask import FlaskTestCase


class TransactionRepositoryTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
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

    def test_transactions_from_labour_accounts_can_be_filtered(
        self,
    ) -> None:
        labour_sending_account_from_company_one = self.create_account()
        labour_sending_account_from_company_two = self.create_account()
        labour_sending_account_from_company_three = self.create_account()
        labour_sending_account_from_company_four = self.create_account()

        worker_receiver_account_one = self.create_account()
        worker_receiver_account_two = self.create_account()
        worker_receiver_account_three = self.create_account()
        worker_receiver_account_four = self.create_account()

        transaction_one = self.database_gateway.create_transaction(
            self.datetime_service.now(),
            sending_account=labour_sending_account_from_company_one,
            receiving_account=worker_receiver_account_one,
            amount_sent=Decimal(1),
            amount_received=Decimal(1),
            purpose="test purpose 1",
        )

        transaction_two = self.database_gateway.create_transaction(
            self.datetime_service.now(),
            sending_account=labour_sending_account_from_company_two,
            receiving_account=worker_receiver_account_two,
            amount_sent=Decimal(2),
            amount_received=Decimal(2),
            purpose="test purpose 2",
        )

        transaction_three = self.database_gateway.create_transaction(
            self.datetime_service.now(),
            sending_account=labour_sending_account_from_company_three,
            receiving_account=worker_receiver_account_three,
            amount_sent=Decimal(3),
            amount_received=Decimal(3),
            purpose="test purpose 3",
        )

        self.database_gateway.create_transaction(
            self.datetime_service.now(),
            sending_account=labour_sending_account_from_company_four,
            receiving_account=worker_receiver_account_four,
            amount_sent=Decimal(4),
            amount_received=Decimal(4),
            purpose="test purpose 4",
        )

        assert list(
            self.database_gateway.get_transactions().where_account_is_sender(
                *[
                    labour_sending_account_from_company_one,
                    labour_sending_account_from_company_two,
                    labour_sending_account_from_company_three,
                ]
            )
        ) == [transaction_one, transaction_two, transaction_three]

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


class JoinedWithReceiverTests(FlaskTestCase):
    def test_that_joined_with_receiver_yields_member(
        self,
    ) -> None:
        member_id = self.member_generator.create_member()
        member = self.database_gateway.get_members().with_id(member_id).first()
        assert member
        self.transaction_generator.create_transaction(receiving_account=member.account)
        transaction_and_receiver = (
            self.database_gateway.get_transactions()
            .where_account_is_receiver(member.account)
            .joined_with_receiver()
            .first()
        )
        assert transaction_and_receiver
        assert transaction_and_receiver[1] == member

    @parameterized.expand(
        [
            (AccountTypes.p,),
            (AccountTypes.r,),
            (AccountTypes.a,),
            (AccountTypes.prd,),
        ]
    )
    def test_that_joined_with_receiver_yields_company(
        self,
        account_type: AccountTypes,
    ) -> None:
        company_id = self.company_generator.create_company()
        company = self.database_gateway.get_companies().with_id(company_id).first()
        assert company
        account = company.get_account_by_type(account_type)
        assert account
        self.transaction_generator.create_transaction(receiving_account=account)
        transaction_and_receiver = (
            self.database_gateway.get_transactions()
            .where_account_is_receiver(account)
            .joined_with_receiver()
            .first()
        )
        assert transaction_and_receiver
        assert transaction_and_receiver[1] == company

    def test_that_joined_with_receiver_yields_social_accounting(
        self,
    ) -> None:
        social_accounting = self.injector.get(SocialAccounting)
        self.transaction_generator.create_transaction(
            receiving_account=social_accounting.account
        )
        transaction_and_receiver = (
            self.database_gateway.get_transactions()
            .where_account_is_receiver(social_accounting.account)
            .joined_with_receiver()
            .first()
        )
        assert transaction_and_receiver
        assert transaction_and_receiver[1] == social_accounting


class JoinedWithSenderAndReceiverTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
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
