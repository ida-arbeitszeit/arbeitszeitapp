from arbeitszeit_web.session import Session
from arbeitszeit_web.www.controllers.list_pending_work_invites_controller import (
    ListPendingWorkInvitesController,
)
from tests.www.base_test_case import BaseTestCase


class ListPendingInvitesControllerTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.controller = self.injector.get(ListPendingWorkInvitesController)

    def test_company_id_of_logged_in_company_is_passed_to_use_case_request(self):
        company_id = self.company_generator.create_company()
        session = self.injector.get(Session)
        session.login_company(company=company_id)
        request = self.controller.create_use_case_request()
        assert request.company == company_id
