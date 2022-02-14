from unittest import TestCase
from uuid import uuid4

from arbeitszeit_web.check_for_unread_message import CheckForUnreadMessagesController
from tests.session import FakeSession


class CheckForUnreadMessagesControllerTests(TestCase):
    def test_that_correct_user_is_returned(self) -> None:
        expected_user = uuid4()
        session = FakeSession()
        session.set_current_user_id(expected_user)
        controller = CheckForUnreadMessagesController(session)
        use_case_request = controller.create_use_case_request()
        self.assertEqual(
            use_case_request.user,
            expected_user,
        )
