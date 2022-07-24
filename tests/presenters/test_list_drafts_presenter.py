from datetime import datetime
from unittest import TestCase
from uuid import uuid4

from arbeitszeit.use_cases.list_drafts_of_company import ListDraftsResponse, ListedDraft
from arbeitszeit_web.list_drafts_of_company import ListDraftsPresenter

from .dependency_injection import get_dependency_injector
from .url_index import DraftUrlIndexImpl


class PresenterTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.presenter = self.injector.get(ListDraftsPresenter)
        self.draft_url_index = self.injector.get(DraftUrlIndexImpl)

    def test(self) -> None:
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
            view_model.results.rows[0].details_url,
            self.draft_url_index.get_draft_summary_url(draft_id),
        )
