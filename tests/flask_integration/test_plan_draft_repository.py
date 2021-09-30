from datetime import datetime
from decimal import Decimal
from unittest import TestCase
from uuid import uuid4

import arbeitszeit.repositories
from arbeitszeit.entities import PlanDraft, ProductionCosts
from project.database.repositories import PlanDraftRepository
from tests.data_generators import CompanyGenerator

from .dependency_injection import get_dependency_injector

DEFAULT_COST = ProductionCosts(
    labour_cost=Decimal(1),
    resource_cost=Decimal(1),
    means_cost=Decimal(1),
)


class PlanDraftRepositoryTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.repo = self.injector.get(PlanDraftRepository)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.planner = self.company_generator.create_company()
        self.DEFAULT_CREATE_ARGUMENTS = dict(
            planner=self.planner.id,
            product_name="test product name",
            description="test description",
            costs=DEFAULT_COST,
            production_unit="test unit",
            amount=1,
            timeframe_in_days=1,
            is_public_service=True,
            creation_timestamp=datetime.now(),
        )

    def test_plan_draft_repository(self) -> None:
        draft = self.repo.get_by_id(uuid4())
        assert draft is None

    def test_drafts_can_be_created(self) -> None:
        draft = self.repo.create_plan_draft(**self.DEFAULT_CREATE_ARGUMENTS)
        assert isinstance(draft, PlanDraft)

    def test_created_drafts_can_be_retrieved_by_their_id(self) -> None:
        expected_draft = self.repo.create_plan_draft(**self.DEFAULT_CREATE_ARGUMENTS)
        self.assertEqual(expected_draft, self.repo.get_by_id(expected_draft.id))

    def test_created_draft_has_correct_attributes(self) -> None:
        draft = self.repo.create_plan_draft(**self.DEFAULT_CREATE_ARGUMENTS)
        self.assertEqual(
            draft.product_name, self.DEFAULT_CREATE_ARGUMENTS["product_name"]
        )
        self.assertEqual(draft.planner.id, self.DEFAULT_CREATE_ARGUMENTS["planner"])
        self.assertEqual(draft.production_costs, self.DEFAULT_CREATE_ARGUMENTS["costs"])
        self.assertEqual(
            draft.creation_date, self.DEFAULT_CREATE_ARGUMENTS["creation_timestamp"]
        )
        self.assertEqual(
            draft.unit_of_distribution, self.DEFAULT_CREATE_ARGUMENTS["production_unit"]
        )
        self.assertEqual(draft.amount_produced, self.DEFAULT_CREATE_ARGUMENTS["amount"])
        self.assertEqual(
            draft.description, self.DEFAULT_CREATE_ARGUMENTS["description"]
        )
        self.assertEqual(
            draft.timeframe, self.DEFAULT_CREATE_ARGUMENTS["timeframe_in_days"]
        )
        self.assertEqual(
            draft.is_public_service, self.DEFAULT_CREATE_ARGUMENTS["is_public_service"]
        )

    def test_can_instantiate_a_repository_through_dependency_injection(self) -> None:
        instance = self.injector.get(arbeitszeit.repositories.PlanDraftRepository)
        self.assertIsInstance(instance, PlanDraftRepository)

    def test_deleted_drafts_cannot_be_retrieved_anymore(self) -> None:
        draft = self.repo.create_plan_draft(**self.DEFAULT_CREATE_ARGUMENTS)
        self.repo.delete_draft(draft.id)
        self.assertIsNone(self.repo.get_by_id(draft.id))
