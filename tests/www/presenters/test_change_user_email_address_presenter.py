from arbeitszeit.interactors import change_user_email_address
from arbeitszeit_web.www.presenters.change_user_email_address_presenter import (
    ChangeUserEmailAddressPresenter,
)
from tests.www.base_test_case import BaseTestCase


class ChangeUserEmailAddressPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(ChangeUserEmailAddressPresenter)

    def test_that_view_model_contains_redirect_url_to_account_details_when_response_is_not_rejected(
        self,
    ) -> None:
        response = self.create_response(is_rejected=False)
        view_model = self.presenter.render_response(response)
        assert view_model.redirect_url == self.url_index.get_user_account_details_url()

    def test_that_view_model_contains_no_redirect_url_when_response_is_rejected(
        self,
    ) -> None:
        response = self.create_response(is_rejected=True)
        view_model = self.presenter.render_response(response)
        assert view_model.redirect_url is None

    def test_that_a_warning_is_displayed_when_response_is_rejected(self) -> None:
        response = self.create_response(is_rejected=True)
        assert not self.notifier.warnings
        self.presenter.render_response(response)
        assert self.notifier.warnings

    def test_that_no_warning_is_displayed_when_response_is_not_rejected(self) -> None:
        response = self.create_response(is_rejected=False)
        assert not self.notifier.warnings
        self.presenter.render_response(response)
        assert not self.notifier.warnings

    def test_that_no_info_is_displayed_when_response_is_rejected(self) -> None:
        response = self.create_response(is_rejected=True)
        assert not self.notifier.infos
        self.presenter.render_response(response)
        assert not self.notifier.infos

    def test_that_an_info_is_displayed_when_response_is_not_rejected(self) -> None:
        response = self.create_response(is_rejected=False)
        assert not self.notifier.infos
        self.presenter.render_response(response)
        assert self.notifier.infos

    def create_response(self, is_rejected: bool) -> change_user_email_address.Response:
        return change_user_email_address.Response(is_rejected=is_rejected)
