from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID, uuid4

from parameterized import parameterized

from arbeitszeit import records
from arbeitszeit.use_cases import create_draft_from_plan as use_case
from arbeitszeit.use_cases import get_draft_details, show_my_plans

from .base_test_case import BaseTestCase


class CreateDraftFromPlanTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(use_case.CreateDraftFromPlanUseCase)
        self.my_plans_use_case = self.injector.get(show_my_plans.ShowMyPlansUseCase)
        self.get_draft_details_use_case = self.injector.get(
            get_draft_details.GetDraftDetails
        )

    def test_creating_draft_from_random_uuids_produces_rejection_response(self) -> None:
        response = self.use_case.create_draft_from_plan(
            request=use_case.Request(
                plan=uuid4(),
                company=uuid4(),
            )
        )
        assert response.is_rejected()

    def test_that_creating_draft_from_existing_plan_for_existing_company_is_not_rejected(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan(approved=True)
        company = self.company_generator.create_company()
        response = self.use_case.create_draft_from_plan(
            request=use_case.Request(
                plan=plan,
                company=company,
            )
        )
        assert not response.is_rejected()

    def test_creating_draft_from_existing_plan_for_non_existing_company_produces_rejection_response(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan(approved=True)
        response = self.use_case.create_draft_from_plan(
            request=use_case.Request(
                plan=plan,
                company=uuid4(),
            )
        )
        assert response.is_rejected()

    def test_that_company_has_an_additional_draft_after_succesful_request(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan(approved=True)
        company = self.company_generator.create_company()
        drafts_before_request = self.count_drafts_for_company(company)
        self.use_case.create_draft_from_plan(
            request=use_case.Request(
                plan=plan,
                company=company,
            )
        )
        drafts_after_request = self.count_drafts_for_company(company)
        assert drafts_after_request == drafts_before_request + 1

    def test_that_creating_draft_from_random_plan_id_for_existing_company_does_not_create_a_new_draft_for_that_company(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        drafts_before_request = self.count_drafts_for_company(company)
        self.use_case.create_draft_from_plan(
            request=use_case.Request(
                plan=uuid4(),
                company=company,
            )
        )
        drafts_after_request = self.count_drafts_for_company(company)
        assert drafts_after_request == drafts_before_request

    @parameterized.expand([("testname1",), ("testname2",)])
    def test_that_newly_created_draft_has_same_product_name_as_pre_existing_plan(
        self, expected_name: str
    ) -> None:
        plan = self.plan_generator.create_plan(
            approved=True, product_name=expected_name
        )
        summary = self.create_draft_and_get_details(plan)
        assert summary.product_name == expected_name

    @parameterized.expand([("description test",), ("test2",)])
    def test_that_newly_created_draft_has_same_description_as_pre_existing_plan(
        self, expected_description: str
    ) -> None:
        plan = self.plan_generator.create_plan(
            approved=True, description=expected_description
        )
        summary = self.create_draft_and_get_details(plan)
        assert summary.description == expected_description

    @parameterized.expand([(Decimal(0),), (Decimal(1),)])
    def test_that_newly_created_draft_has_same_means_cost_as_pre_existing_plan(
        self, expected_cost: Decimal
    ) -> None:
        plan = self.plan_generator.create_plan(
            approved=True,
            costs=records.ProductionCosts(
                means_cost=expected_cost,
                labour_cost=Decimal(0),
                resource_cost=Decimal(0),
            ),
        )
        summary = self.create_draft_and_get_details(plan)
        assert summary.means_cost == expected_cost

    @parameterized.expand([(Decimal(0),), (Decimal(1),)])
    def test_that_newly_created_draft_has_same_labour_cost_as_pre_existing_plan(
        self, expected_cost: Decimal
    ) -> None:
        plan = self.plan_generator.create_plan(
            approved=True,
            costs=records.ProductionCosts(
                labour_cost=expected_cost,
                means_cost=Decimal(0),
                resource_cost=Decimal(0),
            ),
        )
        summary = self.create_draft_and_get_details(plan)
        assert summary.labour_cost == expected_cost

    @parameterized.expand([(Decimal(0),), (Decimal(1),)])
    def test_that_newly_created_draft_has_same_resource_cost_as_pre_existing_plan(
        self, expected_cost: Decimal
    ) -> None:
        plan = self.plan_generator.create_plan(
            approved=True,
            costs=records.ProductionCosts(
                resource_cost=expected_cost,
                means_cost=Decimal(0),
                labour_cost=Decimal(0),
            ),
        )
        summary = self.create_draft_and_get_details(plan)
        assert summary.resources_cost == expected_cost

    @parameterized.expand([("test unit 1",), ("test unit 2",)])
    def test_that_newly_created_draft_has_same_production_unit_as_pre_existing_plan(
        self, expected_unit: str
    ) -> None:
        plan = self.plan_generator.create_plan(
            approved=True, production_unit=expected_unit
        )
        summary = self.create_draft_and_get_details(plan)
        assert summary.production_unit == expected_unit

    @parameterized.expand([(123,), (321,)])
    def test_that_newly_created_draft_has_same_amount_as_pre_existing_plan(
        self, expected_amount: int
    ) -> None:
        plan = self.plan_generator.create_plan(approved=True, amount=expected_amount)
        summary = self.create_draft_and_get_details(plan)
        assert summary.amount == expected_amount

    @parameterized.expand([(123,), (321,)])
    def test_that_newly_created_draft_has_same_timeframe_as_pre_existing_plan(
        self, expected_timeframe: int
    ) -> None:
        plan = self.plan_generator.create_plan(
            approved=True, timeframe=expected_timeframe
        )
        summary = self.create_draft_and_get_details(plan)
        assert summary.timeframe == expected_timeframe

    @parameterized.expand([(True,), (False,)])
    def test_that_newly_created_draft_for_public_plan_if_and_only_if_original_plan_was_also_public(
        self, expected_is_public: bool
    ) -> None:
        plan = self.plan_generator.create_plan(
            approved=True, is_public_service=expected_is_public
        )
        summary = self.create_draft_and_get_details(plan)
        assert summary.is_public_service == expected_is_public

    @parameterized.expand([(datetime(2000, 1, 1),), (datetime(2001, 2, 3),)])
    def test_that_creating_timestamp_of_draft_is_the_time_of_request(
        self, expected_timestamp: datetime
    ) -> None:
        self.datetime_service.freeze_time(expected_timestamp - timedelta(days=1))
        plan = self.plan_generator.create_plan(approved=True)
        self.datetime_service.freeze_time(expected_timestamp)
        company = self.company_generator.create_company()
        response = self.use_case.create_draft_from_plan(
            request=use_case.Request(
                plan=plan,
                company=company,
            )
        )
        assert response.draft
        self.datetime_service.freeze_time(expected_timestamp + timedelta(days=1))
        summary = self.get_draft_details(response.draft)
        assert summary.creation_timestamp == expected_timestamp

    def create_draft_and_get_details(
        self, plan: UUID
    ) -> get_draft_details.DraftDetailsSuccess:
        company = self.company_generator.create_company()
        response = self.use_case.create_draft_from_plan(
            request=use_case.Request(
                plan=plan,
                company=company,
            )
        )
        assert response.draft
        return self.get_draft_details(response.draft)

    def count_drafts_for_company(self, company: UUID) -> int:
        request = show_my_plans.ShowMyPlansRequest(company_id=company)
        response = self.my_plans_use_case.show_company_plans(request)
        return len(response.drafts)

    def get_draft_details(self, draft: UUID) -> get_draft_details.DraftDetailsSuccess:
        response = self.get_draft_details_use_case(draft)
        assert response
        return response
