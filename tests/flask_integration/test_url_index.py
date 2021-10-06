from project.url_index import CompanyUrlIndex, MemberUrlIndex
from tests.data_generators import PlanGenerator

from .view import ViewTestCase


class CompanyUrlIndexTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url_index = CompanyUrlIndex()
        self.plan_generator = self.injector.get(PlanGenerator)
        self.login_company()

    def test_plan_summary_url_for_existing_plan_leads_to_functional_url(self) -> None:
        plan = self.plan_generator.create_plan()
        url = self.url_index.get_plan_summary_url(plan.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class MemberUrlIndexTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url_index = MemberUrlIndex()
        self.plan_generator = self.injector.get(PlanGenerator)
        self.login_member()

    def test_plan_summary_url_for_existing_plan_leads_to_functional_url(self) -> None:
        plan = self.plan_generator.create_plan()
        url = self.url_index.get_plan_summary_url(plan.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
