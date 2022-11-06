from unittest import TestCase
from uuid import uuid4

from arbeitszeit.use_cases.create_plan_draft import CreatePlanDraftResponse
from arbeitszeit_web.create_draft import CreateDraftPresenter
from tests.presenters.notifier import NotifierTestImpl
from tests.presenters.url_index import UrlIndexTestImpl
from tests.translator import FakeTranslator

from .dependency_injection import get_dependency_injector


class PresenterTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.presenter = self.injector.get(CreateDraftPresenter)
        self.url_index = self.injector.get(UrlIndexTestImpl)
        self.notifier = self.injector.get(NotifierTestImpl)
        self.translator = self.injector.get(FakeTranslator)

    def test_on_successful_draft_creation_redirect_to_my_drafts_page(self) -> None:
        draft_id = uuid4()
        response = CreatePlanDraftResponse(draft_id=draft_id, rejection_reason=None)
        view_model = self.presenter.present_plan_creation(response)
        self.assertEqual(
            self.url_index.get_my_plan_drafts_url(), view_model.redirect_url
        )

    def test_on_failed_plan_creation_dont_redirect(self) -> None:
        response = CreatePlanDraftResponse(
            draft_id=None,
            rejection_reason=CreatePlanDraftResponse.RejectionReason.planner_does_not_exist,
        )
        view_model = self.presenter.present_plan_creation(response)
        self.assertIsNone(view_model.redirect_url)

    def test_on_successful_creation_show_message(self) -> None:
        draft_id = uuid4()
        response = CreatePlanDraftResponse(draft_id=draft_id, rejection_reason=None)
        self.presenter.present_plan_creation(response)
        self.assertTrue(self.notifier.infos)

    def test_on_successful_creation_show_proper_message_text(self) -> None:
        draft_id = uuid4()
        response = CreatePlanDraftResponse(draft_id=draft_id, rejection_reason=None)
        self.presenter.present_plan_creation(response)
        self.assertEqual(
            self.notifier.infos[0],
            self.translator.gettext("Plan draft successfully created"),
        )
