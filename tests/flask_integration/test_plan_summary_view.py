from tests.data_generators import PlanGenerator

from .flask import ViewTestCase


class MemberViewTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.member = self.login_member()

    def test_get_200_when_accessing_view(self) -> None:
        plan_generator = self.injector.get(PlanGenerator)
        plan = plan_generator.create_plan()
        response = self.client.get(f"/member/plan_summary/{plan.id}")
        self.assertEqual(response.status_code, 200)


class CompanyViewTests(ViewTestCase):
    def test_get_200_when_accessing_view(self) -> None:
        self.company = self.login_company()
        plan_generator = self.injector.get(PlanGenerator)
        plan = plan_generator.create_plan()
        response = self.client.get(f"/company/plan_summary/{plan.id}")
        self.assertEqual(response.status_code, 200)
