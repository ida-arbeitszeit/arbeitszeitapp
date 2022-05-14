from unittest import TestCase
from uuid import uuid4

from arbeitszeit.user_action import UserAction, UserActionType
from arbeitszeit_web.user_action import UserActionResolverImpl
from tests.translator import FakeTranslator

from .dependency_injection import get_dependency_injector
from .url_index import CoopSummaryUrlIndexTestImpl, InviteUrlIndexImpl


class UserActionResolverTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.invite_url_index = self.injector.get(InviteUrlIndexImpl)
        self.coop_url_index = self.injector.get(CoopSummaryUrlIndexTestImpl)
        self.translator = self.injector.get(FakeTranslator)
        self.action_resolver = self.injector.get(UserActionResolverImpl)

    def test_answer_invite_action_name_resolves_properly(self) -> None:
        action = self._get_answer_invite_request_action()
        self.assertEqual(
            self.action_resolver.resolve_user_action_name(action),
            self.translator.gettext("Accept or decline to join company"),
        )

    def test_answer_cooperation_request_name_resolves_properly(self) -> None:
        action = self._get_answer_cooperation_request_action()
        self.assertEqual(
            self.action_resolver.resolve_user_action_name(action),
            self.translator.gettext("Accept or decline request for cooperation"),
        )

    def test_answer_invite_action_url_resolves_to_proper_url(self) -> None:
        action = self._get_answer_invite_request_action()
        self.assertEqual(
            self.action_resolver.resolve_user_action_reference(action),
            self.invite_url_index.get_invite_url(action.reference),
        )

    def test_answer_cooperation_request_url_resolves_to_proper_url(self) -> None:
        action = self._get_answer_cooperation_request_action()
        self.assertEqual(
            self.action_resolver.resolve_user_action_reference(action),
            self.coop_url_index.get_coop_summary_url(action.reference),
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
