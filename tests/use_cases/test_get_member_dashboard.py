from datetime import datetime
from unittest import TestCase

from arbeitszeit.use_cases import GetMemberDashboard
from arbeitszeit.use_cases.invite_worker_to_company import (
    InviteWorkerToCompany,
    InviteWorkerToCompanyRequest,
)
from tests.data_generators import CompanyGenerator, MemberGenerator, PlanGenerator

from .dependency_injection import get_dependency_injector
from .repositories import CompanyWorkerRepository


class UseCaseTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.get_member_dashboard = self.injector.get(GetMemberDashboard)
        self.company_worker_repository = self.injector.get(CompanyWorkerRepository)
        self.member_generator = self.injector.get(MemberGenerator)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.plan_generator = self.injector.get(PlanGenerator)
        self.invite_worker_to_company = self.injector.get(InviteWorkerToCompany)
        self.member = self.member_generator.create_member()

    def test_that_correct_workplace_email_is_shown(self):
        workplace = self.company_generator.create_company(email="companyname@mail.com")
        self.company_worker_repository.add_worker_to_company(workplace, self.member)

        member_info = self.get_member_dashboard(self.member.id)
        self.assertEqual(
            member_info.workplaces[0].workplace_email, "companyname@mail.com"
        )

    def test_that_correct_workplace_name_is_shown(self):
        workplace = self.company_generator.create_company(name="SomeCompanyNameXY")
        self.company_worker_repository.add_worker_to_company(workplace, self.member)

        member_info = self.get_member_dashboard(self.member.id)
        self.assertEqual(member_info.workplaces[0].workplace_name, "SomeCompanyNameXY")

    def test_that_three_latest_plans_is_empty_if_there_are_no_plans(self):
        response = self.get_member_dashboard(self.member.id)
        self.assertFalse(response.three_latest_plans)

    def test_three_latest_plans_has_at_least_one_entry_if_there_is_one_active_plan(
        self,
    ):
        self.plan_generator.create_plan(activation_date=datetime.min)
        response = self.get_member_dashboard(self.member.id)
        self.assertTrue(response.three_latest_plans)

    def test_no_invites_are_shown_when_none_was_sent(self):
        response = self.get_member_dashboard(self.member.id)
        self.assertFalse(response.invites)

    def test_invites_are_shown_when_worker_was_previously_invited(self):
        inviting_company = self.company_generator.create_company()
        self.invite_worker_to_company(
            InviteWorkerToCompanyRequest(inviting_company.id, self.member.id)
        )
        response = self.get_member_dashboard(self.member.id)
        self.assertTrue(response.invites)

    def test_show_which_company_sent_the_invite(self):
        inviting_company = self.company_generator.create_company()
        self.invite_worker_to_company(
            InviteWorkerToCompanyRequest(inviting_company.id, self.member.id)
        )
        response = self.get_member_dashboard(self.member.id)
        self.assertEqual(response.invites[0].company_id, inviting_company.id)

    def test_show_correct_invite_id(self):
        inviting_company = self.company_generator.create_company()
        invite_response = self.invite_worker_to_company(
            InviteWorkerToCompanyRequest(inviting_company.id, self.member.id)
        )
        get_dashboard_response = self.get_member_dashboard(self.member.id)
        self.assertEqual(
            get_dashboard_response.invites[0].invite_id, invite_response.invite_id
        )
