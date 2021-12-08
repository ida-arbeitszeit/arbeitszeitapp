from unittest import TestCase

from arbeitszeit.user_action import UserAction
from arbeitszeit_web.user_action_resolver import UserActionResolverImpl


class UserActionResolverTests(TestCase):
    def test_that_all_user_actions_can_be_translated_into_labels(self) -> None:
        resolver = UserActionResolverImpl()
        for action in UserAction:
            with self.subTest(f"Test action resolver for {action}"):
                action_label = resolver.resolve_user_action_name(action)
                self.assertIsInstance(action_label, str)

    def test_that_answer_invite_action_is_translated_into_proper_label(self) -> None:
        resolver = UserActionResolverImpl()
        action_label = resolver.resolve_user_action_name(UserAction.answer_invite)
        self.assertEqual(action_label, "Betriebsbeitritt akzeptieren oder ablehnen")

    def test_that_answer_cooperation_request_is_translated_into_proper_label(
        self,
    ) -> None:
        resolver = UserActionResolverImpl()
        action_label = resolver.resolve_user_action_name(
            UserAction.answer_cooperation_request
        )
        self.assertEqual(action_label, "Kooperationsanfrage akzeptieren oder ablehnen")

    def test_that_all_user_actions_can_be_translated_into_references(self) -> None:
        resolver = UserActionResolverImpl()
        for action in UserAction:
            with self.subTest(f"Test action resolver for {action}"):
                action_reference = resolver.resolve_user_action_reference(action)
                self.assertIsInstance(action_reference, str)
