from decimal import Decimal
from uuid import UUID

from arbeitszeit.use_cases import InviteWorkerToCompany, InviteWorkerToCompanyRequest
from arbeitszeit.use_cases.send_accountant_registration_token import (
    SendAccountantRegistrationTokenUseCase,
)
from arbeitszeit_flask.url_index import (
    CompanyUrlIndex,
    FlaskPlotsUrlIndex,
    GeneralUrlIndex,
    MemberUrlIndex,
)
from tests.accountant_invitation_presenter import AccountantInvitationPresenterTestImpl
from tests.data_generators import (
    CompanyGenerator,
    CooperationGenerator,
    MessageGenerator,
    PlanGenerator,
)

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
        self.company_generator = self.injector.get(CompanyGenerator)

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

    def test_toggle_availability_url_for_existing_plan_leads_to_functional_url(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan()
        url = self.url_index.get_toggle_availability_url(plan.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

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

    def test_request_coop_url_leads_to_functional_url(
        self,
    ) -> None:
        url = self.url_index.get_request_coop_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_end_coop_url_for_existing_plan_and_cooperation_leads_to_functional_url(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan()
        coop = self.cooperation_generator.create_cooperation(
            coordinator=self.company, plans=[plan]
        )
        url = self.url_index.get_end_coop_url(plan.id, coop.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_company_summary_url_for_existing_company_leads_to_functional_url(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        url = self.url_index.get_company_summary_url(company.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_list_messages_url_leads_to_functions_address(self) -> None:
        url = self.url_index.get_list_messages_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_pay_means_of_production_url_leads_to_a_view(self) -> None:
        url = self.url_index.get_pay_means_of_production_url()
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
        self.company_generator = self.injector.get(CompanyGenerator)
        self.invite_worker_to_company = self.injector.get(InviteWorkerToCompany)

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

    def test_company_summary_url_for_existing_company_leads_to_functional_url(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        url = self.url_index.get_company_summary_url(company.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_invite_url_for_existing_invite_leads_to_functional_url(self) -> None:
        invite_id = self._create_invite()
        url = self.url_index.get_invite_url(invite_id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_list_messages_url_leads_to_functions_address(self) -> None:
        url = self.url_index.get_list_messages_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def _create_invite(self) -> UUID:
        company = self.company_generator.create_company()
        response = self.invite_worker_to_company(
            InviteWorkerToCompanyRequest(
                company=company.id,
                worker=self.member.id,
            )
        )
        return response.invite_id


class PlotUrlIndexTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url_index = FlaskPlotsUrlIndex()
        self.company, _, self.email = self.login_company()
        self.company = self.confirm_company(company=self.company, email=self.email)

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
        self.url_index = self.injector.get(GeneralUrlIndex)
        self.invite_accountant_use_case = self.injector.get(
            SendAccountantRegistrationTokenUseCase
        )
        self.invitation_presenter = self.injector.get(
            AccountantInvitationPresenterTestImpl
        )

    def test_can_create_valid_url_from_valid_token(self) -> None:
        token = self.invite_accountant(email="test@test.test")
        url = self.url_index.get_accountant_invitation_url(token=token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def invite_accountant(self, email: str) -> str:
        self.invite_accountant_use_case.send_accountant_registration_token(
            request=SendAccountantRegistrationTokenUseCase.Request(email=email)
        )
        return self.invitation_presenter.invitations[-1].token
