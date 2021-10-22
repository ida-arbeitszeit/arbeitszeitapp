from unittest import TestCase
from uuid import uuid4

from arbeitszeit.use_cases import CheckForUnreadMessages, CheckForUnreadMessagesRequest

from .dependency_injection import get_dependency_injector


class CheckForUnreadMessagesTests(TestCase):
    def test_non_existing_users_are_not_considered_to_have_unread_messages(
        self,
    ) -> None:
        injector = get_dependency_injector()
        check_for_unread_messages = injector.get(CheckForUnreadMessages)
        response = check_for_unread_messages(
            CheckForUnreadMessagesRequest(
                user=uuid4(),
            )
        )
        self.assertFalse(response.has_unread_messages)
