from arbeitszeit.use_cases import get_member_dashboard
from arbeitszeit.use_cases.get_member_dashboard import GetMemberDashboardUseCase
from arbeitszeit.use_cases.invite_worker_to_company import InviteWorkerToCompanyUseCase
from tests.use_cases.base_test_case import BaseTestCase


class UseCaseTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(GetMemberDashboardUseCase)
        self.invite_worker_to_company = self.injector.get(InviteWorkerToCompanyUseCase)
        self.member = self.member_generator.create_member()

    def test_that_correct_workplace_email_is_shown(self):
        self.company_generator.create_company_record(
            email="companyname@mail.com",
            workers=[self.member],
        )
        request = get_member_dashboard.Request(member=self.member)
        member_info = self.use_case.get_member_dashboard(request)
        assert member_info.workplaces[0].workplace_email == "companyname@mail.com"

    def test_that_correct_workplace_name_is_shown(self):
        self.company_generator.create_company_record(
            name="SomeCompanyNameXY",
            workers=[self.member],
        )
        request = get_member_dashboard.Request(member=self.member)
        member_info = self.use_case.get_member_dashboard(request)
        assert member_info.workplaces[0].workplace_name == "SomeCompanyNameXY"

    def test_that_three_latest_plans_is_empty_if_there_are_no_plans(self):
        request = get_member_dashboard.Request(member=self.member)
        response = self.use_case.get_member_dashboard(request)
        assert not response.three_latest_plans

    def test_three_latest_plans_has_at_least_one_entry_if_there_is_one_active_plan(
        self,
    ):
        self.plan_generator.create_plan()
        request = get_member_dashboard.Request(member=self.member)
        response = self.use_case.get_member_dashboard(request)
        assert response.three_latest_plans

    def test_no_invites_are_shown_when_none_was_sent(self):
        request = get_member_dashboard.Request(member=self.member)
        response = self.use_case.get_member_dashboard(request)
        assert not response.invites

    def test_invites_are_shown_when_worker_was_previously_invited(self):
        inviting_company = self.company_generator.create_company_record()
        self.invite_worker_to_company(
            InviteWorkerToCompanyUseCase.Request(inviting_company.id, self.member)
        )
        request = get_member_dashboard.Request(member=self.member)
        response = self.use_case.get_member_dashboard(request)
        assert response.invites

    def test_show_id_of_company_that_sent_the_invite(self):
        inviting_company = self.company_generator.create_company_record()
        self.invite_worker_to_company(
            InviteWorkerToCompanyUseCase.Request(inviting_company.id, self.member)
        )
        request = get_member_dashboard.Request(member=self.member)
        response = self.use_case.get_member_dashboard(request)
        assert response.invites[0].company_id == inviting_company.id

    def test_show_name_of_company_that_sent_the_invite(self):
        inviting_company = self.company_generator.create_company_record()
        self.invite_worker_to_company(
            InviteWorkerToCompanyUseCase.Request(inviting_company.id, self.member)
        )
        request = get_member_dashboard.Request(member=self.member)
        response = self.use_case.get_member_dashboard(request)
        assert response.invites[0].company_name == inviting_company.name

    def test_show_correct_invite_id(self):
        inviting_company = self.company_generator.create_company_record()
        invite_response = self.invite_worker_to_company(
            InviteWorkerToCompanyUseCase.Request(inviting_company.id, self.member)
        )
        request = get_member_dashboard.Request(member=self.member)
        get_dashboard_response = self.use_case.get_member_dashboard(request)
        assert get_dashboard_response.invites[0].invite_id == invite_response.invite_id
