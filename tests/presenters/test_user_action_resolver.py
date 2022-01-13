from unittest import TestCase
from uuid import UUID, uuid4

from arbeitszeit.user_action import UserAction, UserActionType
from arbeitszeit_web.user_action import UserActionResolverImpl


class UserActionResolverTests(TestCase):
    def setUp(self) -> None:
        self.invite_url_resolver = InviteUrlIndexImpl()
        self.resolver = UserActionResolverImpl(self.invite_url_resolver)

    def test_answer_invite_action_name_resolves_properly(self) -> None:
        action = self._get_answer_invite_request_action()
        self.assertEqual(
            self.resolver.resolve_user_action_name(action),
            "Betriebsbeitritt akzeptieren oder ablehnen",
        )

    def test_answer_cooperation_request_name_resolves_properly(self) -> None:
        action = self._get_answer_cooperation_request_action()
        self.assertEqual(
            self.resolver.resolve_user_action_name(action),
            "Kooperationsanfrage akzeptieren oder ablehnen",
        )

    def test_answer_invite_action_url_resolves_to_proper_url(self) -> None:
        action = self._get_answer_invite_request_action()
        self.assertEqual(
            self.resolver.resolve_user_action_reference(action),
            self.invite_url_resolver.get_invite_url(action.reference),
        )

    def _get_answer_cooperation_request_action(self) -> UserAction:
        return UserAction(
            type=UserActionType.answer_cooperation_request, reference=uuid4()
        )

    def _get_answer_invite_request_action(self) -> UserAction:
        return UserAction(
            type=UserActionType.answer_invite,
            reference=uuid4(),
        )


class InviteUrlIndexImpl:
    def get_invite_url(self, invite_id: UUID) -> str:
        return f"url for {invite_id}"
