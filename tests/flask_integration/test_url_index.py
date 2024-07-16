from decimal import Decimal
from uuid import UUID, uuid4

from parameterized import parameterized

from arbeitszeit.records import ConsumptionType
from arbeitszeit.use_cases.invite_worker_to_company import InviteWorkerToCompanyUseCase
from arbeitszeit.use_cases.send_accountant_registration_token import (
    SendAccountantRegistrationTokenUseCase,
)
from arbeitszeit_flask.token import FlaskTokenService
from arbeitszeit_flask.url_index import GeneralUrlIndex
from arbeitszeit_web.session import UserRole
from tests.data_generators import CooperationGenerator, PlanGenerator

from .flask import ViewTestCase


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
        self.token_service = self.injector.get(FlaskTokenService)

    def test_invite_url_for_existing_invite_leads_to_functional_url_for_member(
        self,
    ) -> None:
        member = self.login_member()
        invite_id = self._create_invite(member)
        url = self.url_index.get_work_invite_url(invite_id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    @parameterized.expand([True, False])
    def test_url_for_answering_existing_work_invite_leads_to_functional_url(
        self, is_absolute: bool
    ) -> None:
        member = self.login_member()
        invite_id = self._create_invite(member)
        url = self.url_index.get_answer_company_work_invite_url(
            invite_id=invite_id, is_absolute=is_absolute
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_plan_company_summary_url_for_existing_plan_leads_to_functional_url(
        self,
    ) -> None:
        self.login_company()
        plan = self.plan_generator.create_plan()
        url = self.url_index.get_plan_details_url(UserRole.company, plan)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_plan_member_summary_url_for_existing_plan_leads_to_functional_url(
        self,
    ) -> None:
        self.login_member()
        plan = self.plan_generator.create_plan()
        url = self.url_index.get_plan_details_url(UserRole.member, plan)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_can_create_valid_url_from_valid_token(self) -> None:
        token = self.token_service.generate_token("test text")
        url = self.url_index.get_accountant_invitation_url(token=token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_that_draft_details_url_leads_to_200_response_for_existing_draft(
        self,
    ) -> None:
        company = self.login_company()
        draft = self.plan_generator.draft_plan(planner=company.id)
        url = self.url_index.get_draft_details_url(draft_id=draft)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_coop_summary_url_for_existing_coop_leads_to_functional_url_for_companies(
        self,
    ) -> None:
        self.login_company()
        coop = self.cooperation_generator.create_cooperation()
        url = self.url_index.get_coop_summary_url(coop)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_coop_summary_url_for_existing_coop_leads_to_functional_url_for_member(
        self,
    ) -> None:
        self.login_member()
        coop = self.cooperation_generator.create_cooperation()
        url = self.url_index.get_coop_summary_url(coop)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_coop_summary_url_for_existing_coop_leads_to_functional_url_for_accountant(
        self,
    ) -> None:
        self.login_accountant()
        coop = self.cooperation_generator.create_cooperation()
        url = self.url_index.get_coop_summary_url(coop)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_list_coordinations_url_for_existing_coop_leads_to_functional_url_for_companies(
        self,
    ) -> None:
        self.login_company()
        coop = self.cooperation_generator.create_cooperation()
        url = self.url_index.get_list_of_coordinators_url(coop)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_list_coordinations_url_for_existing_coop_leads_to_functional_url_for_member(
        self,
    ) -> None:
        self.login_member()
        coop = self.cooperation_generator.create_cooperation()
        url = self.url_index.get_list_of_coordinators_url(coop)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_list_coordinations_url_for_existing_coop_leads_to_functional_url_for_accountant(
        self,
    ) -> None:
        self.login_accountant()
        coop = self.cooperation_generator.create_cooperation()
        url = self.url_index.get_list_of_coordinators_url(coop)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_company_summary_url_for_existing_company_leads_to_functional_url_for_company(
        self,
    ) -> None:
        self.login_company()
        company = self.company_generator.create_company_record()
        url = self.url_index.get_company_summary_url(company_id=company.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_company_summary_url_for_existing_company_leads_to_functional_url_for_member(
        self,
    ) -> None:
        self.login_member()
        company = self.company_generator.create_company_record()
        url = self.url_index.get_company_summary_url(company_id=company.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_company_summary_url_for_existing_company_leads_to_functional_url_for_accountant(
        self,
    ) -> None:
        self.login_accountant()
        company = self.company_generator.create_company_record()
        url = self.url_index.get_company_summary_url(company_id=company.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def _create_invite(self, member: UUID) -> UUID:
        company = self.company_generator.create_company_record()
        response = self.invite_worker_to_company(
            InviteWorkerToCompanyUseCase.Request(
                company=company.id,
                worker=member,
            )
        )
        assert response.invite_id
        return response.invite_id

    def test_url_for_registering_private_consumption_leads_to_functional_url_without_parameters(
        self,
    ) -> None:
        self.login_member()
        url = self.url_index.get_register_private_consumption_url(
            amount=None, plan_id=None
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_url_for_registering_private_consumption_leads_to_functional_url_with_parameters(
        self,
    ) -> None:
        self.login_member()
        url = self.url_index.get_register_private_consumption_url(
            amount=1, plan_id=uuid4()
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_url_for_registration_of_productive_consumption_leads_to_functional_url(
        self,
    ) -> None:
        self.login_company()
        url = self.url_index.get_register_productive_consumption_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_url_for_registration_of_productive_consumption_with_plan_parameter_leads_to_functional_url(
        self,
    ) -> None:
        self.login_company()
        url = self.url_index.get_register_productive_consumption_url(uuid4())
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_url_for_registration_of_productive_consumption_with_amount_parameter_leads_to_functional_url(
        self,
    ) -> None:
        self.login_company()
        url = self.url_index.get_register_productive_consumption_url(
            plan_id=uuid4(), amount=3
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_url_for_registration_of_productive_consumption_with_type_of_consumption_parameter_leads_to_functional_url(
        self,
    ) -> None:
        self.login_company()
        url = self.url_index.get_register_productive_consumption_url(
            plan_id=uuid4(),
            amount=3,
            consumption_type=ConsumptionType.means_of_prod,
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

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
        url = self.url_index.get_end_coop_url(plan, coop)
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

    def test_my_plan_drafts_url_leads_to_functional_url(
        self,
    ) -> None:
        self.login_company()
        url = self.url_index.get_my_plan_drafts_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_post_request_to_file_plan_url_leads_to_functional_url(
        self,
    ) -> None:
        self.login_company()
        url = self.url_index.get_file_plan_url(uuid4())
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

    def test_create_draft_url_leads_to_functional_url(
        self,
    ) -> None:
        self.login_company()
        url = self.url_index.get_create_draft_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_query_companies_url_leads_to_functional_url(
        self,
    ) -> None:
        self.login_member()
        url = self.url_index.get_query_companies_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_unconfirmed_member_url_leads_to_function_route(self) -> None:
        self.login_member()
        url = self.url_index.get_unconfirmed_member_url()
        response = self.client.get(url)
        assert response.status_code < 400

    def test_renew_plan_url_for_existing_plan_leads_to_functional_url(
        self,
    ) -> None:
        self.login_company()
        plan = self.plan_generator.create_plan()
        url = self.url_index.get_renew_plan_url(plan)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

    def test_hide_plan_url_for_existing_plan_leads_to_functional_url(
        self,
    ) -> None:
        self.login_company()
        plan = self.plan_generator.create_plan()
        url = self.url_index.get_hide_plan_url(plan)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_request_coordination_transfer_url_for_existing_coop_leads_to_functional_url(
        self,
    ) -> None:
        self.login_company()
        coop = self.cooperation_generator.create_cooperation()
        url = self.url_index.get_request_coordination_transfer_url(coop)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_get_request_to_show_coordination_transfer_request_url_leads_to_functional_url(
        self,
    ) -> None:
        current_user = self.login_company().id
        coop_id = self.cooperation_generator.create_cooperation(
            coordinator=current_user
        )
        transfer_request_id = self.coordination_transfer_request_generator.create_coordination_transfer_request(
            requester=current_user, cooperation=coop_id
        )
        url = self.url_index.get_show_coordination_transfer_request_url(
            transfer_request_id
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_post_request_by_assignated_candidate_to_show_coordination_transfer_request_url_leads_to_functional_url(
        self,
    ) -> None:
        candidate = self.login_company().id
        coordinator = self.company_generator.create_company()
        coop_id = self.cooperation_generator.create_cooperation(coordinator=coordinator)
        transfer_request_id = self.coordination_transfer_request_generator.create_coordination_transfer_request(
            requester=coordinator, cooperation=coop_id, candidate=candidate
        )
        url = self.url_index.get_show_coordination_transfer_request_url(
            transfer_request_id
        )
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

    def test_get_request_to_company_accounts_url_leads_to_functional_url_if_company_exists(
        self,
    ) -> None:
        self.login_company()
        company = self.company_generator.create_company()
        url = self.url_index.get_company_accounts_url(company_id=company)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_company_account_p_leads_to_functional_url_if_company_exists(
        self,
    ) -> None:
        self.login_company()
        company = self.company_generator.create_company()
        url = self.url_index.get_company_account_p_url(company_id=company)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_company_account_r_leads_to_functional_url(
        self,
    ) -> None:
        self.login_company()
        company = self.company_generator.create_company()
        url = self.url_index.get_company_account_r_url(company_id=company)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_company_account_a_leads_to_functional_url(
        self,
    ) -> None:
        self.login_company()
        company = self.company_generator.create_company()
        url = self.url_index.get_company_account_a_url(company_id=company)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_company_account_prd_leads_to_functional_url(
        self,
    ) -> None:
        self.login_company()
        company = self.company_generator.create_company()
        url = self.url_index.get_company_account_prd_url(company_id=company)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_company_transactions_leads_to_functional_url(
        self,
    ) -> None:
        self.login_company()
        company = self.company_generator.create_company()
        url = self.url_index.get_company_transactions_url(company_id=company)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_request_email_change_url_leads_to_functional_url(
        self,
    ) -> None:
        self.login_member()
        url = self.url_index.get_request_change_email_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
