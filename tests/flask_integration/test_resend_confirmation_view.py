from arbeitszeit_flask.extensions import mail

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
        self.member = self.login_member(confirm_member=False)

    def test_authenticated_and_unconfirmed_users_get_redirected_and_mail_gets_send(
        self,
    ):
        assert not self.member.confirmed_on
        response = self.client.get(self.url)
        with mail.record_messages() as outbox:
            response = self.client.get(
                self.url,
            )
            self.assertEqual(response.status_code, 302)
            assert len(outbox) == 1


class ConfirmedMemberTests(ViewTestCase):
    def setUp(self):
        super().setUp()
        self.url = "/member/resend"
        self.member = self.login_member(confirm_member=True)

    def test_already_confirmed_member_gets_redirected_and_no_mail_gets_sent(
        self,
    ):
        assert self.member.confirmed_on
        response = self.client.get(self.url)
        with mail.record_messages() as outbox:
            response = self.client.get(
                self.url,
            )
            self.assertEqual(response.status_code, 302)
            assert len(outbox) == 0
