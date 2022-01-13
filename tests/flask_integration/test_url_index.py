from project.url_index import CompanyUrlIndex, MemberUrlIndex
from tests.data_generators import CooperationGenerator, MessageGenerator, PlanGenerator

from .flask import ViewTestCase


class CompanyUrlIndexTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url_index = CompanyUrlIndex()
        self.plan_generator = self.injector.get(PlanGenerator)
        self.message_generator = self.injector.get(MessageGenerator)
        self.company, _, self.email = self.login_company()
        self.company = self.confirm_company(company=self.company, email=self.email)
        self.cooperation_generator = self.injector.get(CooperationGenerator)

    def test_plan_summary_url_for_existing_plan_leads_to_functional_url(self) -> None:
        plan = self.plan_generator.create_plan()
        url = self.url_index.get_plan_summary_url(plan.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_message_url_for_existing_message_leads_to_functional_url(self) -> None:
        message = self.message_generator.create_message(addressee=self.company)
        url = self.url_index.get_message_url(message.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_coop_summary_url_for_existing_coop_leads_to_functional_url(self) -> None:
        coop = self.cooperation_generator.create_cooperation()
        url = self.url_index.get_coop_summary_url(coop.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class MemberUrlIndexTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url_index = MemberUrlIndex()
        self.plan_generator = self.injector.get(PlanGenerator)
        self.message_generator = self.injector.get(MessageGenerator)
        self.member, _, self.email = self.login_member()
        self.member = self.confirm_member(member=self.member, email=self.email)
        self.cooperation_generator = self.injector.get(CooperationGenerator)

    def test_plan_summary_url_for_existing_plan_leads_to_functional_url(self) -> None:
        plan = self.plan_generator.create_plan()
        url = self.url_index.get_plan_summary_url(plan.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_message_url_for_existing_message_leads_to_functional_url(self) -> None:
        message = self.message_generator.create_message(addressee=self.member)
        url = self.url_index.get_message_url(message.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_coop_summary_url_for_existing_coop_leads_to_functional_url(self) -> None:
        coop = self.cooperation_generator.create_cooperation()
        url = self.url_index.get_coop_summary_url(coop.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
