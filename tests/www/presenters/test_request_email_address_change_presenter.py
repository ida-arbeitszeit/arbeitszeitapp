from arbeitszeit.use_cases import request_email_address_change as use_case
from arbeitszeit_web.www.presenters import (
    request_email_address_change_presenter as presenter,
)

from ..base_test_case import BaseTestCase


class RequestEmailAddressChangePresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(presenter.RequestEmailAddressChangePresenter)

    def test_on_success_redirect_to_non_empty_target(self) -> None:
        response = use_case.Response(is_rejected=False)
        view_model = self.presenter.render_response(response)
        assert view_model.redirect_url

    def test_on_success_redirect_logged_in_member_to_account_details_page(self) -> None:
        self.session.login_member(self.member_generator.create_member())
        response = use_case.Response(is_rejected=False)
        view_model = self.presenter.render_response(response)
        assert (
            view_model.redirect_url == self.url_index.get_member_account_details_url()
        )

    def test_on_success_redirect_logged_in_company_to_account_details_page(
        self,
    ) -> None:
        self.session.login_company(self.company_generator.create_company())
        response = use_case.Response(is_rejected=False)
        view_model = self.presenter.render_response(response)
        assert (
            view_model.redirect_url == self.url_index.get_company_account_details_url()
        )

    def test_on_success_redirect_logged_in_accountant_to_account_details_page(
        self,
    ) -> None:
        self.session.login_accountant(self.accountant_generator.create_accountant())
        response = use_case.Response(is_rejected=False)
        view_model = self.presenter.render_response(response)
        assert (
            view_model.redirect_url
            == self.url_index.get_accountant_account_details_url()
        )

    def test_on_failure_dont_redirect_logged_in_member(self) -> None:
        self.session.login_member(self.member_generator.create_member())
        response = use_case.Response(is_rejected=True)
        view_model = self.presenter.render_response(response)
        assert view_model.redirect_url is None

    def test_on_failure_dont_redirect_logged_in_company(
        self,
    ) -> None:
        self.session.login_company(self.company_generator.create_company())
        response = use_case.Response(is_rejected=True)
        view_model = self.presenter.render_response(response)
        assert view_model.redirect_url is None

    def test_on_failure_dont_redirect_logged_in_accountant(
        self,
    ) -> None:
        self.session.login_accountant(self.accountant_generator.create_accountant())
        response = use_case.Response(is_rejected=True)
        view_model = self.presenter.render_response(response)
        assert view_model.redirect_url is None

    def test_on_failure_show_a_warning_that_the_request_was_denied(self) -> None:
        self.session.login_member(self.member_generator.create_member())
        response = use_case.Response(is_rejected=True)
        self.presenter.render_response(response)
        expected_message = self.translator.gettext(
            "Your request for an email address change was rejected."
        )
        assert expected_message in self.notifier.warnings

    def test_on_success_dont_show_a_warning_that_the_request_was_denied(self) -> None:
        self.session.login_member(self.member_generator.create_member())
        response = use_case.Response(is_rejected=False)
        self.presenter.render_response(response)
        expected_message = self.translator.gettext(
            "Your request for an email address change was rejected."
        )
        assert expected_message not in self.notifier.warnings