from uuid import uuid4

from tests.data_generators import MemberGenerator, MessageGenerator

from .flask import ViewTestCase


class MemberViewTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.message_generator = self.injector.get(MessageGenerator)
        self.member_generator = self.injector.get(MemberGenerator)
        self.member, _ = self.login_member()

    def test_get_200_when_message_exists(self) -> None:
        message = self.message_generator.create_message(addressee=self.member)
        url = f"/member/messages/{message.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_get_404_when_message_does_not_exist(self) -> None:
        response = self.client.get(f"/member/messages/{uuid4()}")
        self.assertEqual(response.status_code, 404)

    def test_message_content_is_shown_in_response_data(self) -> None:
        expected_content = "test content 123"
        message = self.message_generator.create_message(
            addressee=self.member, content=expected_content
        )
        url = f"/member/messages/{message.id}"
        response = self.client.get(url)
        self.assertIn(expected_content, response.get_data(as_text=True))

    def test_get_404_when_message_is_not_addressed_to_current_user(self) -> None:
        other_user = self.member_generator.create_member()
        message = self.message_generator.create_message(addressee=other_user)
        url = f"/member/messages/{message.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class CompanyViewTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.message_generator = self.injector.get(MessageGenerator)
        self.company, _ = self.login_company()

    def test_get_200_when_message_exists(self) -> None:
        message = self.message_generator.create_message(addressee=self.company)
        url = f"/company/messages/{message.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
