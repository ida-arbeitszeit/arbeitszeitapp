from parameterized import parameterized

from arbeitszeit_web.www.presenters.cancel_cooperation_request_presenter import (
    CancelCooperationRequestPresenter,
)
from tests.www.base_test_case import BaseTestCase


class CancelCooperationRequestPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(CancelCooperationRequestPresenter)

    def test_successfull_cancel_request_response_is_presented_correctly(self) -> None:
        self.presenter.render_response(response=True)
        assert len(self.notifier.infos) == 1
        assert not self.notifier.warnings
        assert self.notifier.infos[0] == self.translator.gettext(
            "Cooperation request has been canceled."
        )

    def test_failed_cancel_request_response_is_presented_correctly(self) -> None:
        self.presenter.render_response(response=False)
        assert len(self.notifier.warnings) == 1
        assert not self.notifier.infos
        assert self.notifier.warnings[0] == self.translator.gettext(
            "Error: Not possible to cancel request."
        )

    @parameterized.expand(
        [
            (True,),
            (False,),
        ]
    )
    def test_that_user_gets_redirected_to_my_cooperations_view(
        self, response: bool
    ) -> None:
        view_model = self.presenter.render_response(response)
        assert view_model.redirection_url == self.url_index.get_my_cooperations_url()
