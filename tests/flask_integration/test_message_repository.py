from typing import Optional
from unittest import TestCase

from hypothesis import given, strategies

from arbeitszeit import repositories as interfaces
from arbeitszeit.user_action import UserAction
from project.database.repositories import MessageRepository
from tests import strategies as custom_strategies
from tests.data_generators import CompanyGenerator, MemberGenerator

from .dependency_injection import get_dependency_injector


class MessageRepositoryTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.repo = self.injector.get(interfaces.MessageRepository)
        self.member = self.injector.get(MemberGenerator).create_member()

    def test_dependency_injection_returns_correct_type(self) -> None:
        repo = self.injector.get(interfaces.MessageRepository)
        self.assertIsInstance(repo, MessageRepository)

    def test_when_creating_a_message_it_can_be_retrieved_later_by_its_id(self) -> None:
        expected_message = self.repo.create_message(
            addressee=self.member,
            title="test title",
            content="test content",
            sender_remarks=None,
            reference=None,
        )
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
        message = self.repo.create_message(
            addressee=self.member,
            title="test title",
            content="test content",
            sender_remarks=None,
            reference=expected_user_action,
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
        message = self.repo.create_message(
            addressee=self.member,
            title=expected_title,
            content="test content",
            sender_remarks=None,
            reference=None,
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
        message = self.repo.create_message(
            addressee=self.member,
            title="test title",
            content=expected_content,
            sender_remarks=None,
            reference=None,
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
        message = self.repo.create_message(
            addressee=self.member,
            title="test title",
            content="test content",
            sender_remarks=expected_sender_remarks,
            reference=None,
        )
        self.assertEqual(
            message.sender_remarks,
            expected_sender_remarks,
        )

    def test_company(self) -> None:
        company = self.injector.get(CompanyGenerator).create_company()
        message = self.repo.create_message(
            addressee=company,
            title="test title",
            content="test content",
            sender_remarks=None,
            reference=None,
        )
        self.assertEqual(message.addressee, company)
