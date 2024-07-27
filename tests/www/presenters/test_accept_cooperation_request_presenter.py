from parameterized import parameterized

from arbeitszeit.use_cases.accept_cooperation import AcceptCooperationResponse
from arbeitszeit_web.www.presenters.accept_cooperation_request_presenter import (
    AcceptCooperationRequestPresenter,
)
from tests.www.base_test_case import BaseTestCase


class ShowMyCooperationsPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(AcceptCooperationRequestPresenter)

    def test_successfull_accept_request_response_is_presented_correctly(self) -> None:
        self.presenter.render_response(AcceptCooperationResponse(rejection_reason=None))
        assert len(self.notifier.infos) == 1
        assert not self.notifier.warnings
        assert self.notifier.infos[0] == self.translator.gettext(
            "Cooperation request has been accepted."
        )
        assert not self.notifier.warnings

    def test_failed_accept_request_response_is_presented_correctly(self) -> None:
        self.presenter.render_response(
            AcceptCooperationResponse(
                rejection_reason=AcceptCooperationResponse.RejectionReason.plan_not_found
            )
        )
        assert len(self.notifier.warnings) == 1
        assert not self.notifier.infos
        assert self.notifier.warnings[0] == self.translator.gettext(
            "Plan or cooperation not found."
        )

    @parameterized.expand(
        [(reason,) for reason in AcceptCooperationResponse.RejectionReason] + [(None,)]
    )
    def test_that_user_gets_redirected_to_my_cooperations_view(
        self, rejection_reason: AcceptCooperationResponse.RejectionReason | None
    ) -> None:
        response = self.presenter.render_response(
            AcceptCooperationResponse(rejection_reason=rejection_reason)
        )
        assert response.redirection_url == self.url_index.get_my_cooperations_url()
