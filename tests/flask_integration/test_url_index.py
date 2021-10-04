from uuid import uuid4

from project.url_index import CompanyUrlIndex, MemberUrlIndex
from tests.data_generators import CompanyGenerator, MemberGenerator, PlanGenerator

from .dependency_injection import ViewTestCase


class CompanyUrlIndexTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        company_generator = self.injector.get(CompanyGenerator)
        self.user_password = "password123"
        self.current_user = company_generator.create_company(
            password=self.user_password
        )
        self.url_index = CompanyUrlIndex()
        self.plan_generator = self.injector.get(PlanGenerator)
        self.login()

    def test_plan_summary_url_for_existing_plan_leads_to_functional_url(self) -> None:
        plan = self.plan_generator.create_plan()
        url = self.url_index.get_plan_summary_url(plan.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def login(self) -> None:
        response = self.client.post(
            "/company/login",
            data=dict(
                email=self.current_user.email,
                password=self.user_password,
            ),
            follow_redirects=True,
        )
        assert response.status_code < 400


class MemberUrlIndexTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        member_generator = self.injector.get(MemberGenerator)
        self.user_password = "password123"
        self.current_user = member_generator.create_member(password=self.user_password)
        self.url_index = MemberUrlIndex()
        self.plan_generator = self.injector.get(PlanGenerator)
        self.login()

    def test_plan_summary_url_for_existing_plan_leads_to_functional_url(self) -> None:
        plan = self.plan_generator.create_plan()
        url = self.url_index.get_plan_summary_url(plan.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def login(self) -> None:
        response = self.client.post(
            "/member/login",
            data=dict(
                email=self.current_user.email,
                password=self.user_password,
            ),
            follow_redirects=True,
        )
        assert response.status_code < 400
