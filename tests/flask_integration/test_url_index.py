from decimal import Decimal
from uuid import UUID, uuid4

from arbeitszeit.use_cases import InviteWorkerToCompanyUseCase
from arbeitszeit.use_cases.send_accountant_registration_token import (
    SendAccountantRegistrationTokenUseCase,
)
from arbeitszeit_flask.url_index import CompanyUrlIndex, GeneralUrlIndex
from arbeitszeit_web.session import UserRole
from tests.accountant_invitation_presenter import AccountantInvitationPresenterTestImpl
from tests.data_generators import CompanyGenerator, CooperationGenerator, PlanGenerator

from .flask import ViewTestCase


class CompanyUrlIndexTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url_index = CompanyUrlIndex()
        self.plan_generator = self.injector.get(PlanGenerator)
        self.company = self.login_company()
        self.cooperation_generator = self.injector.get(CooperationGenerator)
        self.company_generator = self.injector.get(CompanyGenerator)

    def test_renew_plan_url_for_existing_plan_leads_to_functional_url(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan()
        url = self.url_index.get_renew_plan_url(plan.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_hide_plan_url_for_existing_plan_leads_to_functional_url(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan()
        url = self.url_index.get_hide_plan_url(plan.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)


class PlotUrlIndexTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url_index = GeneralUrlIndex()
        self.company = self.login_company()

    def test_url_for_barplot_for_certificates_returns_png(self) -> None:
        url = self.url_index.get_global_barplot_for_certificates_url(
            certificates_count=Decimal("10"), available_product=Decimal("5")
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "image/png")

    def test_url_for_barplot_for_means_of_productions_returns_png(self) -> None:
        url = self.url_index.get_global_barplot_for_means_of_production_url(
            planned_means=Decimal("10"),
            planned_resources=Decimal("5"),
            planned_work=Decimal("20"),
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "image/png")

    def test_url_for_barplot_for_plans_returns_png(self) -> None:
        url = self.url_index.get_global_barplot_for_plans_url(
            productive_plans=10, public_plans=5
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "image/png")

    def test_url_for_lineplot_for_companies_own_prd_account_returns_png(self) -> None:
        url = self.url_index.get_line_plot_of_company_prd_account(
            company_id=self.company.id
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "image/png")

    def test_url_for_lineplot_for_companies_own_r_account_returns_png(self) -> None:
        url = self.url_index.get_line_plot_of_company_r_account(
            company_id=self.company.id
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "image/png")

    def test_url_for_lineplot_for_companies_own_p_account_returns_png(self) -> None:
        url = self.url_index.get_line_plot_of_company_p_account(
            company_id=self.company.id
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "image/png")

    def test_url_for_lineplot_for_companies_own_a_account_returns_png(self) -> None:
        url = self.url_index.get_line_plot_of_company_a_account(
            company_id=self.company.id
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "image/png")


class GeneralUrlIndexTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.plan_generator = self.injector.get(PlanGenerator)
        self.url_index = self.injector.get(GeneralUrlIndex)
        self.invite_worker_to_company = self.injector.get(InviteWorkerToCompanyUseCase)
        self.cooperation_generator = self.injector.get(CooperationGenerator)
        self.invite_accountant_use_case = self.injector.get(
            SendAccountantRegistrationTokenUseCase
        )
        self.invitation_presenter = self.injector.get(
            AccountantInvitationPresenterTestImpl
        )

    def test_invite_url_for_existing_invite_leads_to_functional_url_for_member(
        self,
    ) -> None:
        member = self.login_member()
        invite_id = self._create_invite(member.id)
        url = self.url_index.get_work_invite_url(invite_id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_plan_company_summary_url_for_existing_plan_leads_to_functional_url(
        self,
    ) -> None:
        self.login_company()
        plan = self.plan_generator.create_plan()
        url = self.url_index.get_plan_summary_url(UserRole.company, plan.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_plan_member_summary_url_for_existing_plan_leads_to_functional_url(
        self,
    ) -> None:
        self.login_member()
        plan = self.plan_generator.create_plan()
        url = self.url_index.get_plan_summary_url(UserRole.member, plan.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_can_create_valid_url_from_valid_token(self) -> None:
        token = self.invite_accountant(email="test@test.test")
        url = self.url_index.get_accountant_invitation_url(token=token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_that_draft_summary_url_leads_to_200_response_for_existing_draft(
        self,
    ) -> None:
        company = self.login_company()
        draft = self.plan_generator.draft_plan(planner=company)
        url = self.url_index.get_draft_summary_url(draft_id=draft.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def invite_accountant(self, email: str) -> str:
        self.invite_accountant_use_case.send_accountant_registration_token(
            request=SendAccountantRegistrationTokenUseCase.Request(email=email)
        )
        return self.invitation_presenter.invitations[-1].token

    def test_coop_summary_url_for_existing_coop_leads_to_functional_url_for_companies(
        self,
    ) -> None:
        self.login_company()
        coop = self.cooperation_generator.create_cooperation()
        url = self.url_index.get_coop_summary_url(UserRole.company, coop.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_coop_summary_url_for_existing_coop_leads_to_functional_url_for_member(
        self,
    ) -> None:
        self.login_member()
        coop = self.cooperation_generator.create_cooperation()
        url = self.url_index.get_coop_summary_url(UserRole.member, coop.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_company_summary_url_for_existing_company_leads_to_functional_url_for_company(
        self,
    ) -> None:
        self.login_company()
        company = self.company_generator.create_company()
        url = self.url_index.get_company_summary_url(
            user_role=UserRole.company, company_id=company.id
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_company_summary_url_for_existing_company_leads_to_functional_url_for_member(
        self,
    ) -> None:
        self.login_member()
        company = self.company_generator.create_company()
        url = self.url_index.get_company_summary_url(
            user_role=UserRole.member, company_id=company.id
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def _create_invite(self, member: UUID) -> UUID:
        company = self.company_generator.create_company()
        response = self.invite_worker_to_company(
            InviteWorkerToCompanyUseCase.Request(
                company=company.id,
                worker=member,
            )
        )
        return response.invite_id

    def test_url_for_payment_of_consumer_product_leads_to_functional_url(self) -> None:
        self.login_member()
        url = self.url_index.get_pay_consumer_product_url(amount=1, plan_id=uuid4())
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_url_for_payment_of_means_of_production_leads_to_functional_url(
        self,
    ) -> None:
        self.login_company()
        url = self.url_index.get_pay_means_of_production_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_url_for_payment_of_means_of_production_with_plan_parameter_leads_to_functional_url(
        self,
    ) -> None:
        self.login_company()
        url = self.url_index.get_pay_means_of_production_url(uuid4())
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_toggle_availability_url_for_existing_plan_leads_to_functional_url(
        self,
    ) -> None:
        self.login_company()
        plan = self.plan_generator.create_plan()
        url = self.url_index.get_toggle_availability_url(plan.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_request_coop_url_leads_to_functional_url(
        self,
    ) -> None:
        self.login_company()
        url = self.url_index.get_request_coop_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_end_coop_url_for_existing_plan_and_cooperation_leads_to_functional_url(
        self,
    ) -> None:
        company = self.login_company()
        plan = self.plan_generator.create_plan()
        coop = self.cooperation_generator.create_cooperation(
            coordinator=company, plans=[plan]
        )
        url = self.url_index.get_end_coop_url(plan.id, coop.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_delete_draft_url_does_not_produce_404(
        self,
    ) -> None:
        self.login_company()
        url = self.url_index.get_delete_draft_url(uuid4())
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 404)

    def test_my_plans_url_leads_to_functional_url(
        self,
    ) -> None:
        self.login_company()
        url = self.url_index.get_my_plans_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_post_request_to_file_plan_url_leads_to_functional_url(
        self,
    ) -> None:
        self.login_company()
        url = self.url_index.get_file_plan_url(uuid4())
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
