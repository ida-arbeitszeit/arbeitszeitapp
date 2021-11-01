from dataclasses import dataclass
from unittest import TestCase
from uuid import uuid4

from arbeitszeit_web.invite_worker_to_company import InviteWorkerToCompanyController


class InviteWorkerToCompanyControllerTests(TestCase):
    def setUp(self) -> None:
        self.controller = InviteWorkerToCompanyController()

    def test_current_user_is_company_in_use_case_request(self) -> None:
        expected_company_id = uuid4()
        use_case_request = self.controller.import_request_data(
            current_user=expected_company_id,
            form=Form(worker_id=str(uuid4())),
        )
        self.assertEqual(use_case_request.company, expected_company_id)

    def test_raise_value_error_if_user_is_not_logged_in(self) -> None:
        with self.assertRaisesRegex(ValueError, r"User is not logged in"):
            self.controller.import_request_data(
                current_user=None,
                form=Form(worker_id=str(uuid4())),
            )

    def test_raise_value_error_if_worker_id_is_empty_string(self) -> None:
        with self.assertRaisesRegex(ValueError, "worker_id"):
            self.controller.import_request_data(
                current_user=uuid4(),
                form=Form(worker_id=""),
            )

    def test_raise_value_error_if_worker_id_is_not_a_uuid(self) -> None:
        with self.assertRaises(ValueError):
            self.controller.import_request_data(
                current_user=uuid4(),
                form=Form(worker_id="1"),
            )

    def test_use_case_request_contains_specified_worker_id(self) -> None:
        expected_worker_id = uuid4()
        use_case_request = self.controller.import_request_data(
            current_user=uuid4(),
            form=Form(worker_id=str(expected_worker_id)),
        )
        self.assertEqual(use_case_request.worker, expected_worker_id)


@dataclass
class Form:
    worker_id: str

    def get_worker_id(self) -> str:
        return self.worker_id
