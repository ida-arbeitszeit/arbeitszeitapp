from unittest import TestCase
from uuid import uuid4

from arbeitszeit.use_cases.create_plan_draft import CreatePlanDraftResponse
from arbeitszeit_web.create_draft import CreateDraftPresenter
from tests.presenters.url_index import UrlIndexTestImpl

from .dependency_injection import get_dependency_injector


class PresenterTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.presenter = self.injector.get(CreateDraftPresenter)
        self.url_index = self.injector.get(UrlIndexTestImpl)

    def test_on_successful_draft_creation_redirect_to_draft_detail_page(self) -> None:
        draft_id = uuid4()
        response = CreatePlanDraftResponse(draft_id=draft_id, rejection_reason=None)
        view_model = self.presenter.present_plan_creation(response)
        self.assertEqual(
            self.url_index.get_draft_summary_url(draft_id), view_model.redirect_url
        )

    def test_on_failed_plan_creation_dont_redirect(self) -> None:
        response = CreatePlanDraftResponse(
            draft_id=None,
            rejection_reason=CreatePlanDraftResponse.RejectionReason.planner_does_not_exist,
        )
        view_model = self.presenter.present_plan_creation(response)
        self.assertIsNone(view_model.redirect_url)
