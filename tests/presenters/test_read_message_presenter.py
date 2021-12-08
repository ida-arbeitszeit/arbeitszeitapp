from typing import Dict
from unittest import TestCase

from arbeitszeit.use_cases import ReadMessageSuccess
from arbeitszeit.user_action import UserAction
from arbeitszeit_web.read_message import ReadMessagePresenter


class ReadMessagePresenterTests(TestCase):
    def setUp(self) -> None:
        self.action_link_resolver = UserActionResolver()
        self.presenter = ReadMessagePresenter(self.action_link_resolver)
        self.use_case_response = ReadMessageSuccess(
            message_title="test title",
            message_content="message content",
            sender_remarks=None,
            user_action=None,
        )

    def test_correct_message_title_from_use_case_is_propagated_to_view_model(
        self,
    ) -> None:
        self.use_case_response.message_title = "test title"
        view_model = self.presenter.present(self.use_case_response)
        self.assertEqual(view_model.title, "test title")

    def test_correct_message_content_is_shown_in_view_model(self) -> None:
        self.use_case_response.message_content = "test content"
        view_model = self.presenter.present(self.use_case_response)
        self.assertEqual(view_model.content, "test content")

    def test_dont_show_action_link_when_no_user_action_is_provided(self) -> None:
        self.use_case_response.user_action = None
        view_model = self.presenter.present(self.use_case_response)
        self.assertFalse(view_model.show_action_link)

    def test_show_action_link_when_user_action_is_provided(self) -> None:
        self.use_case_response.user_action = UserAction.answer_invite
        view_model = self.presenter.present(self.use_case_response)
        self.assertTrue(view_model.show_action_link)

    def test_that_for_worker_invite_action_the_proper_action_link_is_rendered(
        self,
    ) -> None:
        self.use_case_response.user_action = UserAction.answer_invite
        view_model = self.presenter.present(self.use_case_response)
        self.assertEqual(view_model.action_link_reference, "answer invite action")

    def test_that_for_anser_cooperation_request_the_proper_action_link_is_rendered(
        self,
    ) -> None:
        self.use_case_response.user_action = UserAction.answer_cooperation_request
        view_model = self.presenter.present(self.use_case_response)
        self.assertEqual(view_model.action_link_reference, "answer cooperation request")

    def test_that_action_link_label_for_invite_action_is_rendered_properly(
        self,
    ) -> None:
        self.use_case_response.user_action = UserAction.answer_invite
        view_model = self.presenter.present(self.use_case_response)
        self.assertEqual(view_model.action_link_label, "answer invite name")

    def test_that_action_link_label_for_answer_cooperation_request_is_rendered_properly(
        self,
    ) -> None:
        self.use_case_response.user_action = UserAction.answer_cooperation_request
        view_model = self.presenter.present(self.use_case_response)
        self.assertEqual(
            view_model.action_link_label, "answer cooperation request name"
        )


class UserActionResolver:
    def resolve_user_action_reference(self, action: UserAction) -> str:
        action_to_reference: Dict[UserAction, str] = {
            UserAction.answer_invite: "answer invite action",
            UserAction.answer_cooperation_request: "answer cooperation request",
        }
        return action_to_reference[action]

    def resolve_user_action_name(self, action: UserAction) -> str:
        action_to_name: Dict[UserAction, str] = {
            UserAction.answer_invite: "answer invite name",
            UserAction.answer_cooperation_request: "answer cooperation request name",
        }
        return action_to_name[action]
