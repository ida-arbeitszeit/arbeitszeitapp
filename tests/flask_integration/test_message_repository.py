from typing import Optional, Union
from unittest import TestCase

from hypothesis import given, strategies

from arbeitszeit import repositories as interfaces
from arbeitszeit.entities import Company, Member, Message, SocialAccounting
from arbeitszeit.user_action import UserAction
from project.database.repositories import AccountingRepository, MessageRepository
from tests import strategies as custom_strategies
from tests.data_generators import CompanyGenerator, MemberGenerator

from .dependency_injection import get_dependency_injector


class MessageRepositoryTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.repo: MessageRepository = self.injector.get(interfaces.MessageRepository)
        self.social_accounting_repository = self.injector.get(AccountingRepository)
        self.social_accounting = (
            self.social_accounting_repository.get_or_create_social_accounting()
        )
        self.member_generator = self.injector.get(MemberGenerator)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.addressee = self.member_generator.create_member()
        self.sender = self.member_generator.create_member()

    def test_dependency_injection_returns_correct_type(self) -> None:
        repo = self.injector.get(interfaces.MessageRepository)
        self.assertIsInstance(repo, MessageRepository)

    def test_when_creating_a_message_it_can_be_retrieved_later_by_its_id(self) -> None:
        expected_message = self._create_message()
        self.assertEqual(
            expected_message,
            self.repo.get_by_id(expected_message.id),
        )

    @given(
        expected_user_action=strategies.one_of(
            strategies.none(), custom_strategies.user_actions()
        )
    )
    def test_user_action_is_stored_correctly(
        self,
        expected_user_action: Optional[UserAction],
    ) -> None:
        message = self._create_message(
            user_action=expected_user_action,
        )
        self.assertEqual(
            message.user_action,
            expected_user_action,
        )

    @given(
        expected_title=strategies.text(),
    )
    def test_title_is_stored_correctly(
        self,
        expected_title: str,
    ) -> None:
        message = self._create_message(
            title=expected_title,
        )
        self.assertEqual(
            message.title,
            expected_title,
        )

    @given(
        expected_content=strategies.text(),
    )
    def test_content_is_stored_correctly(
        self,
        expected_content: str,
    ) -> None:
        message = self._create_message(
            content=expected_content,
        )
        self.assertEqual(
            message.content,
            expected_content,
        )

    @given(
        expected_sender_remarks=strategies.one_of(strategies.none(), strategies.text())
    )
    def test_sender_remarks_are_stored_correctly(
        self,
        expected_sender_remarks,
    ) -> None:
        message = self._create_message(
            sender_remarks=expected_sender_remarks,
        )
        self.assertEqual(
            message.sender_remarks,
            expected_sender_remarks,
        )

    def test_as_addressee_is_correctly_stored(self) -> None:
        company = self.company_generator.create_company()
        message = self._create_message(
            addressee=company,
        )
        self.assertEqual(message.addressee, company)

    def test_member_sender_is_stored_correctly(self) -> None:
        sender = self.member_generator.create_member()
        message = self._create_message(
            sender=sender,
        )
        self.assertEqual(message.sender, sender)

    def test_social_accounting_sender_is_stored_correctly(self) -> None:
        message = self._create_message(sender=self.social_accounting)
        self.assertEqual(message.sender, self.social_accounting)

    def test_company_sender_is_stored_correctly(self) -> None:
        sender = self.company_generator.create_company()
        message = self._create_message(sender=sender)
        self.assertEqual(message.sender, sender)

    def test_that_message_can_be_marked_as_read(self) -> None:
        message = self._create_message()
        self.assertFalse(message.is_read)
        self.repo.mark_as_read(message)
        self.assertTrue(message.is_read)

    def test_marking_a_message_as_read_is_persisted(self) -> None:
        message = self._create_message()
        self.repo.mark_as_read(message)
        message_from_db = self.repo.get_by_id(message.id)
        assert message_from_db
        self.assertTrue(message_from_db.is_read)

    def _create_message(
        self,
        sender: Union[None, Company, Member, SocialAccounting] = None,
        addressee: Union[None, Member, Company] = None,
        title: str = "test title",
        content: str = "test content",
        sender_remarks: Optional[str] = None,
        user_action: Optional[UserAction] = None,
    ) -> Message:
        if sender is None:
            sender = self.sender
        if addressee is None:
            addressee = self.addressee
        return self.repo.create_message(
            sender=sender,
            addressee=addressee,
            title=title,
            content=content,
            sender_remarks=sender_remarks,
            reference=user_action,
        )
