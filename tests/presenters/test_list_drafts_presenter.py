from unittest import TestCase
from uuid import uuid4

from arbeitszeit.use_cases.list_drafts_of_company import ListDraftsResponse, ListedDraft
from arbeitszeit_web.list_drafts_of_company import ListDraftsPresenter
from tests.data_generators import FakeDatetimeService

from .dependency_injection import get_dependency_injector
from .url_index import UrlIndexTestImpl


class PresenterTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.presenter = self.injector.get(ListDraftsPresenter)
        self.url_index = self.injector.get(UrlIndexTestImpl)

    def test_that_correct_details_url_is_shown_for_draft(self) -> None:
        datetime_service = FakeDatetimeService()
        draft_id = uuid4()
        response = ListDraftsResponse(
            results=[
                ListedDraft(
                    id=draft_id,
                    creation_date=datetime_service.now(),
                    product_name="test product name",
                    description="test description",
                )
            ]
        )
        view_model = self.presenter.present(response)
        self.assertEqual(
            view_model.results.rows[0].details_url,
            self.url_index.get_draft_summary_url(draft_id),
        )

    def test_that_correct_delete_url_is_shown_for_draft(self) -> None:
        draft_id = uuid4()
        response = ListDraftsResponse(
            results=[
                ListedDraft(
                    id=draft_id,
                    creation_date=datetime.min,
                    product_name="test product name",
                    description="test description",
                )
            ]
        )
        view_model = self.presenter.present(response)
        self.assertEqual(
            view_model.results.rows[0].delete_url,
            self.url_index.get_delete_draft_url(draft_id),
        )
