from datetime import datetime
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID, uuid4

from arbeitszeit.entities import PlanDraft, ProductionCosts
from arbeitszeit_flask.database.repositories import PlanDraftRepository
from tests.data_generators import CompanyGenerator
from tests.datetime_service import FakeDatetimeService

from .flask import FlaskTestCase

DEFAULT_COST = ProductionCosts(
    labour_cost=Decimal(1),
    resource_cost=Decimal(1),
    means_cost=Decimal(1),
)


class PlanDraftRepositoryBaseTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.repo = self.injector.get(PlanDraftRepository)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.planner = self.company_generator.create_company_entity()
        self.datetime_service = self.injector.get(FakeDatetimeService)

    def create_plan_draft(
        self,
        product_name: str = "product name",
        planner: Optional[UUID] = None,
        description: str = "test description",
        costs: ProductionCosts = ProductionCosts(Decimal(0), Decimal(0), Decimal(0)),
        production_unit: str = "test unit",
        amount: int = 1,
        duration: int = 1,
        is_public_service: bool = True,
        creation_timestamp: Optional[datetime] = None,
    ) -> PlanDraft:
        if planner is None:
            planner = self.planner.id
        if creation_timestamp is None:
            creation_timestamp = self.datetime_service.now()
        return self.repo.create_plan_draft(
            planner=planner,
            product_name=product_name,
            description=description,
            costs=costs,
            production_unit=production_unit,
            amount=amount,
            timeframe_in_days=duration,
            is_public_service=is_public_service,
            creation_timestamp=creation_timestamp,
        )


class PlanDraftRepositoryTests(PlanDraftRepositoryBaseTests):
    def test_plan_draft_repository(self) -> None:
        draft = self.repo.get_plan_drafts().with_id(uuid4()).first()
        assert draft is None

    def test_created_drafts_can_be_retrieved_by_their_id(self) -> None:
        expected_draft = self.create_plan_draft()
        self.assertEqual(
            expected_draft,
            self.repo.get_plan_drafts().with_id(expected_draft.id).first(),
        )

    def test_created_draft_name_specified_on_creation(self) -> None:
        expected_product_name = "test product name"
        draft = self.create_plan_draft(product_name=expected_product_name)
        assert draft.product_name == expected_product_name

    def test_created_draft_has_planner_that_it_was_created_with(self) -> None:
        expected_planner = self.company_generator.create_company()
        draft = self.create_plan_draft(planner=expected_planner)
        assert draft.planner == expected_planner

    def test_that_created_draft_as_production_costs_specified_on_creation(self) -> None:
        expected_production_costs = ProductionCosts(Decimal(5), Decimal(3), Decimal(1))
        draft = self.create_plan_draft(costs=expected_production_costs)
        assert draft.production_costs == expected_production_costs

    def test_that_created_draft_has_creation_timestamp_it_was_created_with(
        self,
    ) -> None:
        expected_timestamp = datetime(2000, 1, 2)
        draft = self.create_plan_draft(creation_timestamp=expected_timestamp)
        assert draft.creation_date == expected_timestamp

    def test_that_created_draft_has_production_unit_it_was_created_with(self) -> None:
        expected_unit = "test unit 123"
        draft = self.create_plan_draft(production_unit=expected_unit)
        assert draft.unit_of_distribution == expected_unit

    def test_that_created_draft_has_amount_it_was_created_with(self) -> None:
        expected_amount = 4231
        draft = self.create_plan_draft(amount=expected_amount)
        assert draft.amount_produced == expected_amount

    def test_that_created_draft_has_description_it_was_created_with(self) -> None:
        expected_description = "test description 123123"
        draft = self.create_plan_draft(description=expected_description)
        assert draft.description == expected_description

    def test_that_created_draft_has_timeframe_it_was_created_with(self) -> None:
        expected_timeframe = 1231
        draft = self.create_plan_draft(duration=expected_timeframe)
        assert draft.timeframe == expected_timeframe

    def test_that_created_draft_is_public_service_if_it_was_created_as_such(
        self,
    ) -> None:
        draft = self.create_plan_draft(is_public_service=True)
        assert draft.is_public_service

    def test_deleted_drafts_cannot_be_retrieved_anymore(self) -> None:
        draft = self.create_plan_draft()
        self.repo.get_plan_drafts().with_id(draft.id).delete()
        self.assertIsNone(self.repo.get_plan_drafts().with_id(draft.id).first())

    def test_that_deletion_of_one_plan_returns_1_if_plan_existed(self) -> None:
        draft = self.create_plan_draft()
        assert self.repo.get_plan_drafts().with_id(draft.id).delete() == 1

    def test_that_deletion_of_non_existing_plan_returns_0(self) -> None:
        assert self.repo.get_plan_drafts().with_id(uuid4()).delete() == 0

    def test_all_drafts_can_be_retrieved(self) -> None:
        expected_draft1 = self.create_plan_draft()
        expected_draft2 = self.create_plan_draft()
        drafts = self.repo.get_plan_drafts().planned_by(self.planner.id)
        self.assertIn(expected_draft1, drafts)
        self.assertIn(expected_draft2, drafts)

    def test_that_nothing_is_returned_when_repo_is_empty_and_querying_all_drafts(
        self,
    ) -> None:
        assert not self.repo.get_plan_drafts().planned_by(self.planner.id)


class UpdateDraftTests(PlanDraftRepositoryBaseTests):
    def setUp(self) -> None:
        super().setUp()
        self.repo = self.injector.get(PlanDraftRepository)
        self.old_draft = self.create_plan_draft()
        self.other_draft = self.create_plan_draft()

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
        updated_draft = self.repo.get_plan_drafts().with_id(self.old_draft.id).first()
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

    def test_can_update_amount(self) -> None:
        expected_amount = 413
        self.assertUpdate(
            self.repo.UpdateDraft(id=self.old_draft.id, amount=expected_amount),
            "amount_produced",
            expected_amount,
        )

    def test_can_update_costs(self) -> None:
        expected_costs = ProductionCosts(
            labour_cost=Decimal(54),
            means_cost=Decimal(274),
            resource_cost=Decimal(923),
        )
        self.assertUpdate(
            self.repo.UpdateDraft(
                id=self.old_draft.id,
                labour_cost=expected_costs.labour_cost,
                means_cost=expected_costs.means_cost,
                resource_cost=expected_costs.resource_cost,
            ),
            "production_costs",
            expected_costs,
        )

    def test_can_update_is_public_plan(self) -> None:
        self.assertUpdate(
            self.repo.UpdateDraft(id=self.old_draft.id, is_public_service=False),
            "is_public_service",
            False,
        )

    def test_can_update_timeframe(self) -> None:
        self.assertUpdate(
            self.repo.UpdateDraft(id=self.old_draft.id, timeframe=33), "timeframe", 33
        )

    def test_draft_update_only_updates_draft_with_specified_id(self) -> None:
        self.repo.update_draft(
            update=self.repo.UpdateDraft(
                id=self.old_draft.id, product_name="new product name"
            )
        )
        other_draft = self.repo.get_plan_drafts().with_id(self.other_draft.id).first()
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
        updated_draft = self.repo.get_plan_drafts().with_id(self.old_draft.id).first()
        assert updated_draft
        self.assertEqual(getattr(updated_draft, attribute_name), expected_value)
