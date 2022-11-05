from tests.data_generators import PlanGenerator

from .flask import ViewTestCase


class AccountantTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.plan_generator = self.injector.get(PlanGenerator)
        self.login_accountant()

    def test_that_user_gets_redirected(self) -> None:
        plan = self.plan_generator.create_plan()
        response = self.client.post(f"/accountant/plans/{plan.id}/approve")
        assert response.status_code == 302
