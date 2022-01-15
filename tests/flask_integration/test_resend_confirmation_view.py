from project.extensions import mail
from project.token import FlaskTokenService

from .flask import ViewTestCase


class UnauthenticatedMemberTests(ViewTestCase):
    def setUp(self):
        super().setUp()
        self.url = "/member/resend"

    def test_unauthenticated_users_get_redirected(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)


class AuthenticatedButUnconfirmedMemberTests(ViewTestCase):
    def setUp(self):
        super().setUp()
        self.url = "/member/resend"
        self.member, _, self.email = self.login_member()

    def test_authenticated_and_unconfirmed_users_get_redirected_and_mail_gets_send(
        self,
    ):
        response = self.client.get(self.url)
        member_token = FlaskTokenService().generate_token(self.email)
        with mail.record_messages() as outbox:
            response = self.client.get(
                self.url,
            )
            self.assertEqual(response.status_code, 302)
            assert len(outbox) == 1
            assert outbox[0].sender == "test_sender@cp.org"
            assert outbox[0].recipients[0] == self.email
            assert outbox[0].subject == "Bitte bestätige dein Konto"
            assert member_token in outbox[0].html
