from uuid import uuid4

from arbeitszeit.use_cases.create_plan_draft import RejectionReason, Response
from arbeitszeit_web.www.presenters.create_draft_presenter import CreateDraftPresenter
from tests.www.base_test_case import BaseTestCase


class PresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(CreateDraftPresenter)

    def test_on_successful_draft_creation_redirect_to_my_drafts_page(self) -> None:
        draft_id = uuid4()
        response = Response(draft_id=draft_id, rejection_reason=None)
        view_model = self.presenter.present_plan_creation(response)
        self.assertEqual(
            self.url_index.get_my_plan_drafts_url(), view_model.redirect_url
        )

    def test_on_failed_plan_creation_dont_redirect(self) -> None:
        response = Response(
            draft_id=None,
            rejection_reason=RejectionReason.planner_does_not_exist,
        )
        view_model = self.presenter.present_plan_creation(response)
        self.assertIsNone(view_model.redirect_url)

    def test_on_successful_creation_show_message(self) -> None:
        draft_id = uuid4()
        response = Response(draft_id=draft_id, rejection_reason=None)
        self.presenter.present_plan_creation(response)
        self.assertTrue(self.notifier.infos)

    def test_on_successful_creation_show_proper_message_text(self) -> None:
        draft_id = uuid4()
        response = Response(draft_id=draft_id, rejection_reason=None)
        self.presenter.present_plan_creation(response)
        self.assertEqual(
            self.notifier.infos[0],
            self.translator.gettext("Plan draft successfully created"),
        )
