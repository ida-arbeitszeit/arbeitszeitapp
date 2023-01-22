from datetime import datetime
from unittest import TestCase

from arbeitszeit.use_cases import GetMemberDashboard
from arbeitszeit.use_cases.invite_worker_to_company import InviteWorkerToCompanyUseCase
from tests.data_generators import CompanyGenerator, MemberGenerator, PlanGenerator

from .dependency_injection import get_dependency_injector
from .repositories import MemberRepository


class UseCaseTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.get_member_dashboard = self.injector.get(GetMemberDashboard)
        self.member_repository = self.injector.get(MemberRepository)
        self.member_generator = self.injector.get(MemberGenerator)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.plan_generator = self.injector.get(PlanGenerator)
        self.invite_worker_to_company = self.injector.get(InviteWorkerToCompanyUseCase)
        self.member = self.member_generator.create_member_entity()

    def test_that_correct_workplace_email_is_shown(self):
        self.company_generator.create_company_entity(
            email="companyname@mail.com",
            workers=[self.member.id],
        )
        member_info = self.get_member_dashboard(self.member.id)
        self.assertEqual(
            member_info.workplaces[0].workplace_email, "companyname@mail.com"
        )

    def test_that_correct_workplace_name_is_shown(self):
        self.company_generator.create_company_entity(
            name="SomeCompanyNameXY",
            workers=[self.member.id],
        )
        member_info = self.get_member_dashboard(self.member.id)
        self.assertEqual(member_info.workplaces[0].workplace_name, "SomeCompanyNameXY")

    def test_that_three_latest_plans_is_empty_if_there_are_no_plans(self):
        response = self.get_member_dashboard(self.member.id)
        self.assertFalse(response.three_latest_plans)

    def test_three_latest_plans_has_at_least_one_entry_if_there_is_one_active_plan(
        self,
    ):
        self.plan_generator.create_plan()
        response = self.get_member_dashboard(self.member.id)
        self.assertTrue(response.three_latest_plans)

    def test_no_invites_are_shown_when_none_was_sent(self):
        response = self.get_member_dashboard(self.member.id)
        self.assertFalse(response.invites)

    def test_invites_are_shown_when_worker_was_previously_invited(self):
        inviting_company = self.company_generator.create_company_entity()
        self.invite_worker_to_company(
            InviteWorkerToCompanyUseCase.Request(inviting_company.id, self.member.id)
        )
        response = self.get_member_dashboard(self.member.id)
        self.assertTrue(response.invites)

    def test_show_id_of_company_that_sent_the_invite(self):
        inviting_company = self.company_generator.create_company_entity()
        self.invite_worker_to_company(
            InviteWorkerToCompanyUseCase.Request(inviting_company.id, self.member.id)
        )
        response = self.get_member_dashboard(self.member.id)
        self.assertEqual(response.invites[0].company_id, inviting_company.id)

    def test_show_name_of_company_that_sent_the_invite(self):
        inviting_company = self.company_generator.create_company_entity()
        self.invite_worker_to_company(
            InviteWorkerToCompanyUseCase.Request(inviting_company.id, self.member.id)
        )
        response = self.get_member_dashboard(self.member.id)
        self.assertEqual(response.invites[0].company_name, inviting_company.name)

    def test_show_correct_invite_id(self):
        inviting_company = self.company_generator.create_company_entity()
        invite_response = self.invite_worker_to_company(
            InviteWorkerToCompanyUseCase.Request(inviting_company.id, self.member.id)
        )
        get_dashboard_response = self.get_member_dashboard(self.member.id)
        self.assertEqual(
            get_dashboard_response.invites[0].invite_id, invite_response.invite_id
        )
