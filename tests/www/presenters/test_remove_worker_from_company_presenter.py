from parameterized import parameterized

from arbeitszeit.interactors.remove_worker_from_company import (
    Response as InteractorResponse,
)
from arbeitszeit_web.www.presenters import remove_worker_from_company_presenter
from arbeitszeit_web.www.presenters.remove_worker_from_company_presenter import (
    RemoveWorkerFromCompanyPresenter as Presenter,
)
from arbeitszeit_web.www.response import Redirect
from tests.www.base_test_case import BaseTestCase


class TestRemoveWorkerFromCompanyPresenter(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(Presenter)

    def test_correct_redirect_is_returned_on_success(self) -> None:
        response = self.create_response(rejection_reason=None)
        view_model = self.presenter.present(response)
        assert isinstance(view_model, Redirect)
        assert view_model.url == self.url_index.get_invite_worker_to_company_url()

    @parameterized.expand(
        [
            (InteractorResponse.RejectionReason.company_not_found, 404),
            (InteractorResponse.RejectionReason.not_workplace_of_worker, 400),
            (InteractorResponse.RejectionReason.worker_not_found, 404),
        ]
    )
    def test_correct_status_code_is_returned_on_rejection(
        self, rejection_reason: InteractorResponse.RejectionReason, expected_code: int
    ) -> None:
        response = self.create_response(rejection_reason)
        view_model = self.presenter.present(response)
        assert isinstance(view_model, remove_worker_from_company_presenter.ErrorCode)
        assert view_model.code == expected_code

    def test_no_warning_is_displayed_on_success(self) -> None:
        response = self.create_response(rejection_reason=None)
        self.presenter.present(response)
        assert not self.notifier.warnings

    def test_correct_info_is_displayed_on_success(self) -> None:
        response = self.create_response(rejection_reason=None)
        self.presenter.present(response)
        assert len(self.notifier.infos) == 1
        assert self.notifier.infos[0] == self.translator.gettext(
            "Worker successfully removed from company."
        )

    @parameterized.expand(
        [(rejection_reason,) for rejection_reason in InteractorResponse.RejectionReason]
    )
    def test_no_info_is_displayed_on_rejection(
        self, rejection_reason: InteractorResponse.RejectionReason
    ) -> None:
        response = self.create_response(rejection_reason)
        self.presenter.present(response)
        assert not self.notifier.infos

    @parameterized.expand(
        [
            (
                InteractorResponse.RejectionReason.company_not_found,
                "Company not found.",
            ),
            (
                InteractorResponse.RejectionReason.not_workplace_of_worker,
                "Worker is not a member of the company.",
            ),
            (InteractorResponse.RejectionReason.worker_not_found, "Worker not found."),
        ]
    )
    def test_correct_warning_is_displayed_on_rejection(
        self, rejection_reason: InteractorResponse.RejectionReason, message: str
    ) -> None:
        response = self.create_response(rejection_reason)
        self.presenter.present(response)
        assert len(self.notifier.warnings) == 1
        assert self.notifier.warnings[0] == self.translator.gettext(message)

    def create_response(
        self, rejection_reason: InteractorResponse.RejectionReason | None
    ) -> InteractorResponse:
        return InteractorResponse(rejection_reason)
