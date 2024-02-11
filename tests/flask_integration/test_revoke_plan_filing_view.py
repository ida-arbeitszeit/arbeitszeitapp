from uuid import uuid4

from .flask import ViewTestCase


class CompanyViewTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.login_company()

    def test_revoke_existing_plan_as_company_results_in_302_status_code(self) -> None:
        plan = self.plan_generator.create_plan(approved=False)
        response = self.client.post(f"/company/plan/revoke/{plan}")
        self.assertEqual(response.status_code, 302)

    def test_revoke_unexisting_plan_as_company_results_in_302_status_code(self) -> None:
        response = self.client.post(f"/company/plan/revoke/{uuid4()}")
        self.assertEqual(response.status_code, 302)
