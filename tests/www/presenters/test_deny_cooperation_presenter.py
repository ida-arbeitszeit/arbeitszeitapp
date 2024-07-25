from arbeitszeit.use_cases.deny_cooperation import DenyCooperationResponse
from arbeitszeit_web.www.presenters.deny_cooperation_presenter import (
    DenyCooperationPresenter,
)
from tests.www.base_test_case import BaseTestCase


class DenyCooperationPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(DenyCooperationPresenter)

    def test_successfull_deny_request_response_is_presented_correctly(self) -> None:
        self.presenter.render_response(DenyCooperationResponse(rejection_reason=None))
        assert len(self.notifier.infos) == 1
        assert not self.notifier.warnings
        assert self.notifier.infos[0] == self.translator.gettext(
            "Cooperation request has been denied."
        )

    def test_failed_deny_request_response_is_presented_correctly(self) -> None:
        self.presenter.render_response(
            deny_cooperation_response=DenyCooperationResponse(
                rejection_reason=DenyCooperationResponse.RejectionReason.plan_not_found
            )
        )
        assert len(self.notifier.warnings) == 1
        assert not self.notifier.infos
        assert self.notifier.warnings[0] == self.translator.gettext(
            "Plan or cooperation not found."
        )
