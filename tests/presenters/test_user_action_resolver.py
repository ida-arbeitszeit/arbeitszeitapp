from unittest import TestCase

from arbeitszeit.user_action import UserAction
from arbeitszeit_web.user_action import UserActionResolverImpl


class UserActionResolverTests(TestCase):
    def test_user_action_resolver(self) -> None:
        resolver = UserActionResolverImpl()
        action = 1
        resolver.resolve_user_action_reference(action)
