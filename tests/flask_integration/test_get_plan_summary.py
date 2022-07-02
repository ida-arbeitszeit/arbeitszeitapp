from uuid import uuid4

from tests.data_generators import PlanGenerator

from .flask import ViewTestCase


class AuthenticatedMemberTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.plan_generator = self.injector.get(PlanGenerator)
        self.member = self.login_member(confirm_member=True)

    def test_get_404_when_plan_does_not_exist(self) -> None:
        url = f"/member/plan_summary/{uuid4()}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_get_200_when_plan_exists(self) -> None:
        plan = self.plan_generator.create_plan()
        url = f"/member/plan_summary/{plan.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class AuthenticatedCompanyTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.plan_generator = self.injector.get(PlanGenerator)
        self.company, _, self.email = self.login_company()
        self.company = self.confirm_company(company=self.company, email=self.email)

    def test_get_404_when_plan_does_not_exist(self) -> None:
        url = f"/company/plan_summary/{uuid4()}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_get_200_when_plan_exists(self) -> None:
        plan = self.plan_generator.create_plan()
        url = f"/company/plan_summary/{plan.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
