from unittest import TestCase
from uuid import uuid4

from arbeitszeit_web.read_message import ReadMessageController
from tests.session import FakeSession


class AuthenticatedUserTests(TestCase):
    def setUp(self) -> None:
        self.session = FakeSession()
        self.controller = ReadMessageController(self.session)
        self.expected_user_id = uuid4()
        self.session.set_current_user_id(self.expected_user_id)

    def test_correct_user_id_and_message_id_in_request(self) -> None:
        message_id = uuid4()
        use_case_request = self.controller.process_request_data(message_id)
        self.assertEqual(use_case_request.message_id, message_id)
        self.assertEqual(use_case_request.reader_id, self.expected_user_id)


class AnonymousUserTests(TestCase):
    def setUp(self) -> None:
        self.session = FakeSession()
        self.controller = ReadMessageController(self.session)
        self.session.set_current_user_id(None)

    def test_cannot_generate_use_case_request_for_anonymous_user(self) -> None:
        message_id = uuid4()
        with self.assertRaisesRegex(ValueError, r"not authenticated"):
            self.controller.process_request_data(message_id)
