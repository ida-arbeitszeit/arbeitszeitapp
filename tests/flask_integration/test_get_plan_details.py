from uuid import uuid4

from .flask import ViewTestCase


class AuthenticatedMemberTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.member = self.login_member()

    def test_get_404_when_plan_does_not_exist(self) -> None:
        url = f"/member/plan_details/{uuid4()}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_get_200_when_plan_exists(self) -> None:
        plan = self.plan_generator.create_plan()
        url = f"/member/plan_details/{plan}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class AuthenticatedCompanyTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company = self.login_company()

    def test_get_404_when_plan_does_not_exist(self) -> None:
        url = f"/company/plan_details/{uuid4()}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_get_200_when_plan_exists(self) -> None:
        plan = self.plan_generator.create_plan()
        url = f"/company/plan_details/{plan}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class AuthenticatedAccountantTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.accountant = self.login_accountant()

    def test_get_404_when_plan_does_not_exist(self) -> None:
        url = f"/accountant/plan_details/{uuid4()}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_get_200_when_plan_exists(self) -> None:
        plan = self.plan_generator.create_plan()
        url = f"/accountant/plan_details/{plan}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
