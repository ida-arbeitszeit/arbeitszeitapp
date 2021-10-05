from uuid import uuid4

from tests.data_generators import CompanyGenerator, MemberGenerator, PlanGenerator

from .dependency_injection import ViewTestCase


class AuthenticatedMemberTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        member_generator = self.injector.get(MemberGenerator)
        self.plan_generator = self.injector.get(PlanGenerator)
        self.member_password = "password123"
        self.current_member = member_generator.create_member(
            password=self.member_password
        )
        self.login()

    def test_get_404_when_plan_does_not_exist(self) -> None:
        url = f"/member/plan_summary/{uuid4()}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_get_200_when_plan_exists(self) -> None:
        plan = self.plan_generator.create_plan()
        url = f"/member/plan_summary/{plan.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def login(self):
        response = self.client.post(
            "/member/login",
            data=dict(
                email=self.current_member.email,
                password=self.member_password,
            ),
            follow_redirects=True,
        )
        assert response.status_code < 400


class AuthenticatedCompanyTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        company_generator = self.injector.get(CompanyGenerator)
        self.plan_generator = self.injector.get(PlanGenerator)
        self.company_password = "password123"
        self.current_company = company_generator.create_company(
            password=self.company_password
        )
        self.login()

    def test_get_404_when_plan_does_not_exist(self) -> None:
        url = f"/company/plan_summary/{uuid4()}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_get_200_when_plan_exists(self) -> None:
        plan = self.plan_generator.create_plan()
        url = f"/company/plan_summary/{plan.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def login(self):
        response = self.client.post(
            "/company/login",
            data=dict(
                email=self.current_company.email,
                password=self.company_password,
            ),
            follow_redirects=True,
        )
        assert response.status_code < 400
