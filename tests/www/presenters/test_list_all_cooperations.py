from typing import Optional
from uuid import UUID, uuid4

from arbeitszeit.use_cases.list_all_cooperations import (
    ListAllCooperationsResponse,
    ListedCooperation,
)
from arbeitszeit_web.www.presenters.list_all_cooperations_presenter import (
    ListAllCooperationsPresenter,
)
from tests.www.base_test_case import BaseTestCase


class ListMessagesPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(ListAllCooperationsPresenter)
        self.session.login_company(company=uuid4())

    def test_view_model_contains_no_cooperation_and_does_not_show_result_when_non_were_provided(
        self,
    ) -> None:
        response = ListAllCooperationsResponse(cooperations=[])
        view_model = self.presenter.present(response)
        self.assertFalse(view_model.show_results)
        self.assertFalse(view_model.cooperations)

    def test_view_model_contains_and_shows_coop_when_one_was_provided(self) -> None:
        response = self._create_response_with_one_cooperation()
        view_model = self.presenter.present(response)
        self.assertTrue(view_model.cooperations)
        self.assertTrue(view_model.show_results)

    def test_name_is_propagated_to_view_model(self) -> None:
        expected_name = "test123"
        view_model = self.presenter.present(
            self._create_response_with_one_cooperation(name=expected_name)
        )
        self.assertEqual(view_model.cooperations[0].name, expected_name)

    def test_plan_count_is_propagated_to_view_model(self) -> None:
        view_model = self.presenter.present(
            self._create_response_with_one_cooperation(plan_count=10)
        )
        self.assertEqual(view_model.cooperations[0].plan_count, "10")

    def test_correct_coop_summary_url_is_displayed_in_view_model(self) -> None:
        coop_id = uuid4()
        expected_url = self.url_index.get_coop_summary_url(coop_id=coop_id)
        view_model = self.presenter.present(
            self._create_response_with_one_cooperation(coop_id=coop_id)
        )
        self.assertEqual(expected_url, view_model.cooperations[0].coop_summary_url)

    def _create_response_with_one_cooperation(
        self,
        coop_id: Optional[UUID] = None,
        name: str = "coop name",
        plan_count: int = 3,
    ) -> ListAllCooperationsResponse:
        if coop_id is None:
            coop_id = uuid4()
        return ListAllCooperationsResponse(
            cooperations=[
                ListedCooperation(
                    id=coop_id,
                    name=name,
                    plan_count=plan_count,
                )
            ]
        )
