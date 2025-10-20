from parameterized import param, parameterized

from .base_test_case import ViewTestCase


class AuthenticatedMemberTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.member = self.login_member()
        self.url = "/company/signup"

    def test_authenticated_member_gets_200_when_accessing_company_page(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_user_type_in_session_is_set_to_none_when_member_accesses_company_page(
        self,
    ) -> None:
        with self.client.session_transaction() as session:
            self.assertEqual(session["user_type"], "member")
        self.client.get(self.url)
        with self.client.session_transaction() as session:
            self.assertIsNone(session["user_type"])


class UnauthenticatedAndUnconfirmedCompanyTests(ViewTestCase):
    def setUp(self):
        super().setUp()
        self.url = "/company/signup"

    def test_unauthenticated_and_unconfirmed_company_gets_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_correct_posting_is_possible_and_redirects_company(self):
        response = self.client.post(
            self.url,
            data=dict(
                email="test@cp.org",
                name="test name",
                password="test_password",
                repeat_password="test_password",
            ),
        )
        self.assertEqual(response.status_code, 302)

    def test_correct_posting_makes_that_confirmations_mail_is_sent_to_company(self):
        company_email = "test2@cp.org"
        with self.email_service().record_messages() as outbox:
            response = self.client.post(
                self.url,
                data=dict(
                    email=company_email,
                    name="test name",
                    password="test_password",
                    repeat_password="test_password",
                ),
            )
            self.assertEqual(response.status_code, 302)
            assert len(outbox) == 1
            assert outbox[0].sender == "test_sender@cp.org"
            assert outbox[0].recipients[0] == company_email

    @parameterized.expand(
        [
            param(
                dict(
                    email="test@cp.org",
                    name="test name",
                    password="test_password",
                    repeat_password="not_same_password",
                )
            ),
            param(
                dict(
                    email="test@cp.org",
                    name="test name",
                    password="short",
                    repeat_password="short",
                )
            ),
            param(
                dict(
                    email="test@cp.org",
                    name="",
                    password="test_password",
                    repeat_password="test_password",
                )
            ),
            param(
                dict(
                    email="invalid_email",
                    name="test name",
                    password="test_password",
                    repeat_password="test_password",
                )
            ),
            param(
                dict(
                    email="invalid_email@",
                    name="test name",
                    password="test_password",
                    repeat_password="test_password",
                )
            ),
            param(
                dict(
                    email="invalid_email@cp",
                    name="test name",
                    password="test_password",
                    repeat_password="test_password",
                )
            ),
        ]
    )
    def test_invalid_form_posting_with_incorrect_form_does_not_redirect_company(
        self, invalid_form_data: dict
    ):
        response = self.client.post(self.url, data=invalid_form_data)
        self.assertEqual(response.status_code, 400)
