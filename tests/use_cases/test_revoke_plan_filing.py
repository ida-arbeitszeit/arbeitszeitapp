from datetime import timedelta
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from arbeitszeit.records import ProductionCosts
from arbeitszeit.use_cases.get_draft_details import DraftDetailsSuccess, GetDraftDetails
from arbeitszeit.use_cases.revoke_plan_filing import RevokePlanFilingUseCase
from arbeitszeit.use_cases.show_my_plans import ShowMyPlansRequest, ShowMyPlansUseCase
from tests.use_cases.base_test_case import BaseTestCase

rejection_reason = RevokePlanFilingUseCase.Response.RejectionReason


class PlanGetsRevokedTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(RevokePlanFilingUseCase)
        self.show_my_plans = self.injector.get(ShowMyPlansUseCase)

    def test_use_case_is_unsuccessful_if_requesting_company_does_not_exist(
        self,
    ) -> None:
        response = self.use_case.revoke_plan_filing(
            self.create_request(requester=uuid4())
        )
        assert response.is_rejected
        assert response.rejection_reason == rejection_reason.requester_not_found

    def test_use_case_is_unsuccessful_if_plan_does_not_exist(self) -> None:
        response = self.use_case.revoke_plan_filing(self.create_request(plan=uuid4()))
        assert response.is_rejected
        assert response.rejection_reason == rejection_reason.plan_not_found

    def test_use_case_is_unsuccessful_if_requester_is_not_planner_of_plan(self) -> None:
        response = self.use_case.revoke_plan_filing(self.create_request())
        assert response.is_rejected
        assert response.rejection_reason == rejection_reason.requester_is_not_planner

    def test_use_case_is_unsuccessful_if_plan_is_approved_and_not_expired(self) -> None:
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(approved=True, planner=planner).id
        response = self.use_case.revoke_plan_filing(
            self.create_request(plan=plan, requester=planner)
        )
        assert response.is_rejected
        assert response.rejection_reason == rejection_reason.plan_is_active

    def test_use_case_is_unsuccessful_if_plan_is_expired(self) -> None:
        self.datetime_service.freeze_time(self.datetime_service.now())
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(
            approved=True, planner=planner, timeframe=1
        ).id
        self.datetime_service.advance_time(dt=timedelta(days=2))
        response = self.use_case.revoke_plan_filing(
            self.create_request(plan=plan, requester=planner)
        )
        assert response.is_rejected
        assert response.rejection_reason == rejection_reason.plan_is_expired

    def test_no_draft_id_is_in_response_if_use_case_is_unsuccessful(
        self,
    ) -> None:
        response = self.use_case.revoke_plan_filing(
            self.create_request(requester=uuid4())
        )
        assert response.plan_draft is None

    def test_revoking_plan_succeeds_if_requester_is_planner_and_plan_is_neither_approved_nor_expired(
        self,
    ) -> None:
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(approved=False, planner=planner).id
        response = self.use_case.revoke_plan_filing(
            self.create_request(plan=plan, requester=planner)
        )
        assert not response.is_rejected

    def test_draft_id_is_in_response_if_revoking_plan_succeeds(self) -> None:
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(approved=False, planner=planner).id
        response = self.use_case.revoke_plan_filing(
            self.create_request(plan=plan, requester=planner)
        )
        assert response.plan_draft is not None

    def test_after_revoking_successfully_the_plan_does_not_show_in_companys_plans_anymore(
        self,
    ) -> None:
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(approved=False, planner=planner).id
        assert self.plan_is_a_plan_of_company(company=planner, plan=plan)
        self.use_case.revoke_plan_filing(
            self.create_request(plan=plan, requester=planner)
        )
        assert not self.plan_is_a_plan_of_company(company=planner, plan=plan)

    def create_request(
        self, requester: Optional[UUID] = None, plan: Optional[UUID] = None
    ) -> RevokePlanFilingUseCase.Request:
        if requester is None:
            requester = self.company_generator.create_company()
        if plan is None:
            plan = self.plan_generator.create_plan().id
        return RevokePlanFilingUseCase.Request(requester=requester, plan=plan)

    def plan_is_a_plan_of_company(self, company: UUID, plan: UUID) -> bool:
        use_case_request = ShowMyPlansRequest(company_id=company)
        response = self.show_my_plans.show_company_plans(request=use_case_request)
        company_plans = (
            response.active_plans + response.expired_plans + response.non_active_plans
        )
        for p in company_plans:
            if p.id == plan:
                return True
        return False


class DraftGetsCreatedTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(RevokePlanFilingUseCase)
        self.show_my_plans = self.injector.get(ShowMyPlansUseCase)
        self.get_draft_details = self.injector.get(GetDraftDetails)

    def test_after_revoking_the_planner_has_one_draft(
        self,
    ) -> None:
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(approved=False, planner=planner).id
        assert not self.drafts_of_company(company=planner)
        self.use_case.revoke_plan_filing(
            self.create_request(plan=plan, requester=planner)
        )
        assert len(self.drafts_of_company(company=planner)) == 1

    def test_after_revoking_the_planner_has_one_draft_with_correct_id(
        self,
    ) -> None:
        planner = self.company_generator.create_company()
        plan = self.plan_generator.create_plan(approved=False, planner=planner).id
        assert not self.drafts_of_company(company=planner)
        response = self.use_case.revoke_plan_filing(
            self.create_request(plan=plan, requester=planner)
        )
        drafts = self.drafts_of_company(company=planner)
        assert len(drafts) == 1
        assert drafts[0] == response.plan_draft

    def test_after_revoking_the_planner_has_two_drafts_if_it_had_one_before(
        self,
    ) -> None:
        planner = self.company_generator.create_company()
        self.plan_generator.draft_plan(planner=planner)
        plan_to_revoke = self.plan_generator.create_plan(
            approved=False, planner=planner
        ).id
        self.use_case.revoke_plan_filing(
            self.create_request(plan=plan_to_revoke, requester=planner)
        )
        assert len(self.drafts_of_company(company=planner)) == 2

    def test_after_revoking_the_plan_the_planner_has_a_draft_with_the_revoked_plan_attributes(
        self,
    ) -> None:
        revoked_plan_name = "Product XYZ"
        revoked_plan_planner = self.company_generator.create_company()
        revoked_plan_description = "Some description\nMore description"
        revoked_plan_costs = ProductionCosts(Decimal(1), Decimal(2), Decimal(3))
        revoked_plan_unit = "1 piece"
        revoked_plan_amount = 6
        revoked_plan_timeframe = 365
        revoked_plan_is_public = True
        plan = self.plan_generator.create_plan(
            approved=False,
            planner=revoked_plan_planner,
            product_name=revoked_plan_name,
            description=revoked_plan_description,
            costs=revoked_plan_costs,
            production_unit=revoked_plan_unit,
            amount=revoked_plan_amount,
            timeframe=revoked_plan_timeframe,
            is_public_service=revoked_plan_is_public,
        ).id
        response = self.use_case.revoke_plan_filing(
            self.create_request(plan=plan, requester=revoked_plan_planner)
        )

        new_plan_draft = response.plan_draft
        assert new_plan_draft
        new_draft_details = self.details_of_plan_draft(plan_draft=new_plan_draft)
        assert revoked_plan_name == new_draft_details.product_name
        assert revoked_plan_planner == new_draft_details.planner_id
        assert revoked_plan_description == new_draft_details.description
        assert revoked_plan_costs.labour_cost == new_draft_details.labour_cost
        assert revoked_plan_costs.resource_cost == new_draft_details.resources_cost
        assert revoked_plan_costs.means_cost == new_draft_details.means_cost
        assert revoked_plan_unit == new_draft_details.production_unit
        assert revoked_plan_amount == new_draft_details.amount
        assert revoked_plan_timeframe == new_draft_details.timeframe
        assert revoked_plan_is_public == new_draft_details.is_public_service

    def create_request(
        self, requester: Optional[UUID] = None, plan: Optional[UUID] = None
    ) -> RevokePlanFilingUseCase.Request:
        if requester is None:
            requester = self.company_generator.create_company()
        if plan is None:
            plan = self.plan_generator.create_plan().id
        return RevokePlanFilingUseCase.Request(requester=requester, plan=plan)

    def drafts_of_company(self, company: UUID) -> list[UUID]:
        use_case_request = ShowMyPlansRequest(company_id=company)
        response = self.show_my_plans.show_company_plans(request=use_case_request)
        return [draft.id for draft in response.drafts]

    def details_of_plan_draft(self, plan_draft: UUID) -> DraftDetailsSuccess:
        draft_details = self.get_draft_details(draft_id=plan_draft)
        assert isinstance(draft_details, DraftDetailsSuccess)
        return draft_details
