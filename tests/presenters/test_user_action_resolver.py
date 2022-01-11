from unittest import TestCase
from uuid import uuid4

from arbeitszeit.user_action import UserAction, UserActionType
from arbeitszeit_web.user_action import UserActionResolverImpl
from tests.user_action import FakeUserAction


class UserActionResolverTests(TestCase):
    def test_user_action_resolver(self) -> None:
        resolver = UserActionResolverImpl()
        action = FakeUserAction(
            action_type=UserActionType.answer_invite,
            reference=uuid4(),
        )
        resolver.resolve_user_action_reference(action)
