from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from arbeitszeit.use_cases.get_coordination_transfer_request_details import (
    GetCoordinationTransferRequestDetailsUseCase as UseCase,
)
from arbeitszeit_web.www.presenters.get_coordination_transfer_request_details_presenter import (
    GetCoordinationTransferRequestDetailsPresenter as Presenter,
)
from tests.www.base_test_case import BaseTestCase


class GetDetailsPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(Presenter)
        self.company = uuid4()
        self.session.login_company(company=self.company)

    def test_that_request_date_is_formatted_correctly_in_view_model(self):
        response = self.get_use_case_response(request_date=datetime(2021, 1, 1))
        view_model = self.presenter.present(response)
        self.assertEqual(view_model.request_date, "01.01.2021 00:00")

    def test_that_correct_cooperation_summary_url_is_displayed(
        self,
    ):
        user_role = self.session.get_user_role()
        assert user_role
        cooperation_id = uuid4()
        response = self.get_use_case_response(cooperation_id=cooperation_id)
        expected_cooperation_url = self.url_index.get_coop_summary_url(
            user_role=user_role, coop_id=cooperation_id
        )
        view_model = self.presenter.present(response)
        self.assertEqual(view_model.cooperation_url, expected_cooperation_url)

    def test_that_cooperation_name_is_displayed_in_view_model(self):
        expected_cooperation_name = "Test Cooperation"
        response = self.get_use_case_response(
            cooperation_name=expected_cooperation_name
        )
        view_model = self.presenter.present(response)
        self.assertEqual(view_model.cooperation_name, expected_cooperation_name)

    def test_that_correct_company_summary_url_of_candidate_is_displayed(
        self,
    ):
        user_role = self.session.get_user_role()
        assert user_role
        candidate_id = uuid4()
        expected_candidate_url = self.url_index.get_company_summary_url(
            user_role=user_role, company_id=candidate_id
        )
        response = self.get_use_case_response(candidate_id=candidate_id)
        view_model = self.presenter.present(response)
        self.assertEqual(view_model.candidate_url, expected_candidate_url)

    def test_that_candidate_name_is_displayed_in_view_model(self):
        expected_candidate_name = "Candidate Name"
        response = self.get_use_case_response(candidate_name=expected_candidate_name)
        view_model = self.presenter.present(response)
        self.assertEqual(view_model.candidate_name, expected_candidate_name)

    def test_that_current_user_is_candidate_is_true_if_current_user_is_candidate(self):
        candidate = uuid4()
        self.session.login_company(company=candidate)
        response = self.get_use_case_response(candidate_id=candidate)
        view_model = self.presenter.present(response)
        self.assertTrue(view_model.current_user_is_candidate)

    def test_that_current_user_is_candidate_is_false_if_another_user_is_candidate(self):
        user = uuid4()
        candidate = uuid4()
        self.session.login_company(company=user)
        response = self.get_use_case_response(candidate_id=candidate)
        view_model = self.presenter.present(response)
        self.assertFalse(view_model.current_user_is_candidate)

    def test_that_request_is_pending_is_true_if_request_is_pending(self):
        response = self.get_use_case_response(request_is_pending=True)
        view_model = self.presenter.present(response)
        self.assertTrue(view_model.request_is_pending)

    def test_that_request_is_pending_is_false_if_request_is_not_pending(self):
        response = self.get_use_case_response(request_is_pending=False)
        view_model = self.presenter.present(response)
        self.assertFalse(view_model.request_is_pending)

    def test_that_request_status_reads_pending_if_request_is_pending(self):
        response = self.get_use_case_response(request_is_pending=True)
        view_model = self.presenter.present(response)
        self.assertEqual(view_model.request_status, self.translator.gettext("Pending"))

    def test_that_request_status_reads_closed_if_request_is_not_pending(self):
        response = self.get_use_case_response(request_is_pending=False)
        view_model = self.presenter.present(response)
        self.assertEqual(view_model.request_status, self.translator.gettext("Closed"))

    def get_use_case_response(
        self,
        request_date: datetime = datetime(2021, 1, 1),
        cooperation_id: UUID = uuid4(),
        cooperation_name: str = "Test Cooperation",
        candidate_id: UUID = uuid4(),
        candidate_name: str = "Candidate Name",
        request_is_pending: Optional[bool] = None,
    ) -> UseCase.Response:
        if request_is_pending is None:
            request_is_pending = True
        return UseCase.Response(
            request_date=request_date,
            cooperation_id=cooperation_id,
            cooperation_name=cooperation_name,
            candidate_id=candidate_id,
            candidate_name=candidate_name,
            request_is_pending=request_is_pending,
        )
