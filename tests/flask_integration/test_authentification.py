from flask import url_for
from parameterized import parameterized

from tests.flask_integration.flask import LogInUser, ViewTestCase


class NextUrlTests(ViewTestCase):
    def test_that_unsafe_target_url_of_unauthenticated_user_is_not_saved_as_next_url_in_session_cookie(
        self,
    ) -> None:
        unsafe_url = "https://google.com"
        self.client.get(unsafe_url)
        with self.client.session_transaction() as session:
            assert session.get("next") is None

    def test_that_safe_but_unknown_target_url_of_unauthenticated_user_is_not_saved_as_next_url_in_session_cookie(
        self,
    ) -> None:
        safe_url = url_for("main_company.dashboard")
        safe_unknown_url = safe_url + "/unknown"
        self.client.get(safe_unknown_url)
        with self.client.session_transaction() as session:
            assert session.get("next") is None

    @parameterized.expand(
        [
            # company page
            (LogInUser.member, "main_company.dashboard", False),
            (LogInUser.accountant, "main_company.dashboard", False),
            # member page
            (LogInUser.company, "main_member.dashboard", False),
            (LogInUser.accountant, "main_member.dashboard", False),
            # accountant page
            (LogInUser.member, "main_accountant.dashboard", False),
            (LogInUser.company, "main_accountant.dashboard", False),
            # user page
            (LogInUser.accountant, "main_user.account_details", False),
            (LogInUser.member, "main_user.account_details", False),
            (LogInUser.company, "main_user.account_details", False),
        ]
    )
    def test_target_urls_are_not_saved_as_next_url_when_wrong_user_tries_to_access_a_page(
        self,
        user: LogInUser,
        route_name: str,
        is_next_url_saved: bool,
    ) -> None:
        self.login_user(user)
        url = url_for(route_name)
        self.client.get(url)
        with self.client.session_transaction() as session:
            assert (session.get("next") is not None) == is_next_url_saved

    @parameterized.expand(
        [
            ("main_company.dashboard",),
            ("main_member.dashboard",),
            ("main_accountant.dashboard",),
            ("main_user.account_details",),
        ]
    )
    def test_that_safe_target_url_of_unauthenticated_user_is_saved_as_next_url(
        self,
        route_name: str,
    ) -> None:
        safe_url = url_for(route_name)
        self.client.get(safe_url)
        with self.client.session_transaction() as session:
            assert session.get("next") == safe_url


class AuthentificationNotificationsTests(ViewTestCase):
    @parameterized.expand(
        [
            ("main_company.dashboard",),
            ("main_member.dashboard",),
            ("main_accountant.dashboard",),
            ("main_user.account_details",),
        ]
    )
    def test_that_unauthenticated_user_is_warned_to_log_in(
        self,
        route_name: str,
    ) -> None:
        response = self.client.get(url_for(route_name), follow_redirects=True)
        assert "Please log in to view this page." in response.text

    @parameterized.expand(
        [
            # company page
            (LogInUser.member, "main_company.dashboard"),
            (LogInUser.accountant, "main_company.dashboard"),
            # member page
            (LogInUser.company, "main_member.dashboard"),
            (LogInUser.accountant, "main_member.dashboard"),
            # accountant page
            (LogInUser.member, "main_accountant.dashboard"),
            (LogInUser.company, "main_accountant.dashboard"),
        ]
    )
    def test_that_wrong_user_is_warned_to_log_in_with_correct_account(
        self,
        user: LogInUser,
        route_name: str,
    ) -> None:
        self.login_user(user)
        response = self.client.get(url_for(route_name), follow_redirects=True)
        assert "You are not logged in with the correct account." in response.text
