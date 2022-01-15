from unittest import TestCase
from uuid import uuid4

from arbeitszeit_web.check_for_unread_message import CheckForUnreadMessagesController


class CheckForUnreadMessagesControllerTests(TestCase):
    def test_controller(self) -> None:
        expected_user = uuid4()
        controller = CheckForUnreadMessagesController()
        use_case_request = controller.create_use_case_request(expected_user)
        self.assertEqual(
            use_case_request.user,
            expected_user,
        )
