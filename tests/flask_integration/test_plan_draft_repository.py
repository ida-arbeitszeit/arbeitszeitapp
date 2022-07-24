from datetime import datetime
from decimal import Decimal
from typing import Any
from unittest import TestCase
from uuid import uuid4

import arbeitszeit.repositories
from arbeitszeit.entities import PlanDraft, ProductionCosts
from arbeitszeit_flask.database.repositories import PlanDraftRepository
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

    def test_all_drafts_can_be_retrieved(self) -> None:
        expected_draft1 = self.repo.create_plan_draft(**self.DEFAULT_CREATE_ARGUMENTS)
        expected_draft2 = self.repo.create_plan_draft(**self.DEFAULT_CREATE_ARGUMENTS)
        drafts = self.repo.all_drafts_of_company(self.planner.id)
        self.assertIn(expected_draft1, drafts)
        self.assertIn(expected_draft2, drafts)

    def test_that_nothing_is_returned_when_repo_is_empty_and_querying_all_drafts(
        self,
    ) -> None:
        drafts = self.repo.all_drafts_of_company(self.planner.id)
        self.assertFalse(list(drafts))


class UpdateDraftTests(TestCase):
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
        self.old_draft = self.repo.create_plan_draft(**self.DEFAULT_CREATE_ARGUMENTS)
        self.other_draft = self.repo.create_plan_draft(**self.DEFAULT_CREATE_ARGUMENTS)

    def test_can_update_draft_name(self) -> None:
        self.assertUpdate(
            self.repo.UpdateDraft(
                id=self.old_draft.id, product_name="new product name"
            ),
            "product_name",
            "new product name",
        )

    def test_with_product_name_update_none_the_product_name_does_not_get_updated(
        self,
    ) -> None:
        expected_product_name = self.old_draft.product_name
        self.repo.update_draft(
            update=self.repo.UpdateDraft(
                id=self.old_draft.id,
                product_name=None,
            )
        )
        updated_draft = self.repo.get_by_id(self.old_draft.id)
        assert updated_draft
        self.assertEqual(updated_draft.product_name, expected_product_name)

    def test_can_update_description(self) -> None:
        self.assertUpdate(
            self.repo.UpdateDraft(id=self.old_draft.id, description="new description"),
            "description",
            "new description",
        )

    def test_can_update_unit_of_distribution(self) -> None:
        self.assertUpdate(
            self.repo.UpdateDraft(
                id=self.old_draft.id, unit_of_distribution="new unit"
            ),
            "unit_of_distribution",
            "new unit",
        )

    def test_draft_update_only_updates_draft_with_specified_id(self) -> None:
        self.repo.update_draft(
            update=self.repo.UpdateDraft(
                id=self.old_draft.id, product_name="new product name"
            )
        )
        other_draft = self.repo.get_by_id(self.other_draft.id)
        assert other_draft
        self.assertNotEqual(other_draft.product_name, "new product name")

    def assertUpdate(
        self,
        update: PlanDraftRepository.UpdateDraft,
        attribute_name: str,
        expected_value: Any,
    ) -> None:
        self.repo.update_draft(
            update=update,
        )
        updated_draft = self.repo.get_by_id(self.old_draft.id)
        assert updated_draft
        self.assertEqual(getattr(updated_draft, attribute_name), expected_value)
