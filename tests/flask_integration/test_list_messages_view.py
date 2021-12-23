from tests.data_generators import MessageGenerator

from .flask import ViewTestCase


class LoggedInMemberTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.member, _, self.email = self.login_member()
        self.member = self.confirm_member(member=self.member, email=self.email)
        self.url = "/member/messages"

    def test_member_gets_200_status_when_opening_view(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_message_title_shows_up_in_html_content(self) -> None:
        message_generator = self.injector.get(MessageGenerator)
        message_generator.create_message(addressee=self.member, title="test title")
        response = self.client.get(self.url)
        self.assertIn("test title", response.get_data(as_text=True))


class LoggedInCompanyTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company, _ = self.login_company()
        self.url = "/company/messages"

    def test_company_gets_200_status_when_opening_view(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_message_title_shows_up_in_html_content(self) -> None:
        message_generator = self.injector.get(MessageGenerator)
        message_generator.create_message(addressee=self.company, title="test title")
        response = self.client.get(self.url)
        self.assertIn("test title", response.get_data(as_text=True))
