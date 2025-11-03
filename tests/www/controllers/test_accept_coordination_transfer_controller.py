from uuid import uuid4

from arbeitszeit_web.www.controllers.accept_coordination_transfer_controller import (
    AcceptCoordinationTransferController,
)
from tests.www.base_test_case import BaseTestCase


class AcceptCoordinationTransferControllerTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.controller = self.injector.get(AcceptCoordinationTransferController)
        self.company = self.company_generator.create_company()
        self.session.login_company(company=self.company)

    def test_transfer_request_id_gets_passed_to_interactor_request(self) -> None:
        expected = uuid4()
        uc_request = self.controller.create_interactor_request(
            transfer_request=expected
        )
        self.assertEqual(expected, uc_request.transfer_request_id)

    def test_current_logged_in_company_gets_passed_to_interactor_request_as_accepting_company(
        self,
    ) -> None:
        uc_request = self.controller.create_interactor_request(transfer_request=uuid4())
        self.assertEqual(self.company, uc_request.accepting_company)
