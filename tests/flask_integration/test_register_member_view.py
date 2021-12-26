from project.extensions import mail

from .flask import ViewTestCase


class UnauthenticatedAndUnconfirmedMemberTests(ViewTestCase):
    def setUp(self):
        super().setUp()
        self.url = "/member/signup"

    def test_unauthenticated_and_unconfirmed_users_get_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_correct_posting_is_possible_and_redirects_user(self):
        response = self.client.post(
            self.url,
            data=dict(email="test@cp.org", name="test name", password="test_password"),
        )
        self.assertEqual(response.status_code, 302)

    def test_correct_posting_makes_that_confirmations_mail_is_sent_to_member(self):
        with mail.record_messages() as outbox:
            response = self.client.post(
                self.url,
                data=dict(
                    email="test2@cp.org", name="test name", password="test_password"
                ),
            )
            self.assertEqual(response.status_code, 302)
            assert len(outbox) == 1
            assert outbox[0].sender == "test_sender@cp.org"
            assert outbox[0].recipients[0] == "test2@cp.org"
            assert outbox[0].subject == "Bitte bestätige dein Konto"
