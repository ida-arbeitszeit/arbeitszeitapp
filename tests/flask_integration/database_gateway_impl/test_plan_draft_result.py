from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from parameterized import parameterized

from arbeitszeit.records import PlanDraft, ProductionCosts

from ..flask import FlaskTestCase

DEFAULT_COST = ProductionCosts(
    labour_cost=Decimal(1),
    resource_cost=Decimal(1),
    means_cost=Decimal(1),
)


class PlanDraftRepositoryBaseTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.planner = self.company_generator.create_company_record()

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
        return self.database_gateway.create_plan_draft(
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
        draft = self.database_gateway.get_plan_drafts().with_id(uuid4()).first()
        assert draft is None

    def test_created_drafts_can_be_retrieved_by_their_id(self) -> None:
        expected_draft = self.create_plan_draft()
        self.assertEqual(
            expected_draft,
            self.database_gateway.get_plan_drafts().with_id(expected_draft.id).first(),
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
        self.database_gateway.get_plan_drafts().with_id(draft.id).delete()
        self.assertIsNone(
            self.database_gateway.get_plan_drafts().with_id(draft.id).first()
        )

    def test_that_deletion_of_one_plan_returns_1_if_plan_existed(self) -> None:
        draft = self.create_plan_draft()
        assert self.database_gateway.get_plan_drafts().with_id(draft.id).delete() == 1

    def test_that_deletion_of_non_existing_plan_returns_0(self) -> None:
        assert self.database_gateway.get_plan_drafts().with_id(uuid4()).delete() == 0

    def test_all_drafts_can_be_retrieved(self) -> None:
        expected_draft1 = self.create_plan_draft()
        expected_draft2 = self.create_plan_draft()
        drafts = self.database_gateway.get_plan_drafts().planned_by(self.planner.id)
        self.assertIn(expected_draft1, drafts)
        self.assertIn(expected_draft2, drafts)

    def test_that_nothing_is_returned_when_repo_is_empty_and_querying_all_drafts(
        self,
    ) -> None:
        assert not self.database_gateway.get_plan_drafts().planned_by(self.planner.id)


class JoinedWithPlannerAndEmailAddressTests(PlanDraftRepositoryBaseTests):
    def test_that_no_results_are_returned_if_no_drafts_where_created(self) -> None:
        assert (
            not self.database_gateway.get_plan_drafts().joined_with_planner_and_email_address()
        )

    def test_that_one_result_is_returned_when_there_is_one_plan_draft(self) -> None:
        self.create_plan_draft()
        assert (
            len(
                self.database_gateway.get_plan_drafts().joined_with_planner_and_email_address()
            )
            == 1
        )

    def test_that_the_planner_is_the_company_that_created_the_draft(self) -> None:
        planner = self.company_generator.create_company()
        self.create_plan_draft(planner=planner)
        result = (
            self.database_gateway.get_plan_drafts()
            .joined_with_planner_and_email_address()
            .first()
        )
        assert result
        assert result[1].id == planner

    @parameterized.expand(
        [
            "test@test.test",
            "test2@test2.test",
        ]
    )
    def test_that_email_address_is_the_email_address_of_the_planner(
        self, expected_email_address: str
    ) -> None:
        planner = self.company_generator.create_company(email=expected_email_address)
        self.create_plan_draft(planner=planner)
        result = (
            self.database_gateway.get_plan_drafts()
            .joined_with_planner_and_email_address()
            .first()
        )
        assert result
        assert result[2].address == expected_email_address


class PlanDraftUpdateTests(PlanDraftRepositoryBaseTests):
    def test_can_change_the_product_name(self) -> None:
        self.create_plan_draft()
        expected_product_name = "test product name new"
        self.database_gateway.get_plan_drafts().update().set_product_name(
            expected_product_name
        ).perform()
        changed_draft = self.database_gateway.get_plan_drafts().first()
        assert changed_draft
        assert changed_draft.product_name == expected_product_name

    def test_changing_the_product_name_of_one_draft_does_not_change_the_product_name_of_another(
        self,
    ) -> None:
        draft = self.create_plan_draft()
        expected_product_name = "product_name_of_other_draft"
        other_draft = self.create_plan_draft(product_name=expected_product_name)
        self.database_gateway.get_plan_drafts().with_id(
            draft.id
        ).update().set_product_name("changed product name").perform()
        other_draft = self.database_gateway.get_plan_drafts().with_id(other_draft.id).first()  # type: ignore
        assert other_draft.product_name == expected_product_name

    def test_that_product_name_is_not_changed_without_calling_perform(
        self,
    ) -> None:
        expected_product_name = "test product name new"
        self.create_plan_draft(product_name=expected_product_name)
        self.database_gateway.get_plan_drafts().update().set_product_name(
            "changed product name"
        )
        changed_draft = self.database_gateway.get_plan_drafts().first()
        assert changed_draft
        assert changed_draft.product_name == expected_product_name

    def test_an_update_object_cannot_be_modified_but_instead_new_instances_are_created_when_setting_product_name(
        self,
    ) -> None:
        self.create_plan_draft()
        expected_product_name = "test product name new"
        update = self.database_gateway.get_plan_drafts().update()
        update.set_product_name(expected_product_name)
        update.perform()
        changed_draft = self.database_gateway.get_plan_drafts().first()
        assert changed_draft
        assert changed_draft.product_name != expected_product_name

    def test_that_affected_rows_are_returned(self) -> None:
        update = (
            self.database_gateway.get_plan_drafts().update().set_product_name("bla")
        )
        assert update.perform() == 0
        self.create_plan_draft()
        assert update.perform() == 1

    def test_can_update_amount(self) -> None:
        self.create_plan_draft()
        expected_amount = 1234
        self.database_gateway.get_plan_drafts().update().set_amount(
            expected_amount
        ).perform()
        changed_draft = self.database_gateway.get_plan_drafts().first()
        assert changed_draft
        assert changed_draft.amount_produced == expected_amount

    def test_can_update_description(self) -> None:
        self.create_plan_draft()
        expected_description = "bla bla bla"
        self.database_gateway.get_plan_drafts().update().set_description(
            expected_description
        ).perform()
        changed_draft = self.database_gateway.get_plan_drafts().first()
        assert changed_draft
        assert changed_draft.description == expected_description

    def test_can_update_labour_cost(self) -> None:
        self.create_plan_draft()
        expected_labour_cost = Decimal("1.234")
        self.database_gateway.get_plan_drafts().update().set_labour_cost(
            expected_labour_cost
        ).perform()
        changed_draft = self.database_gateway.get_plan_drafts().first()
        assert changed_draft
        assert changed_draft.production_costs.labour_cost == expected_labour_cost

    def test_can_update_means_cost(self) -> None:
        self.create_plan_draft()
        expected_means_cost = Decimal("1.234")
        self.database_gateway.get_plan_drafts().update().set_means_cost(
            expected_means_cost
        ).perform()
        changed_draft = self.database_gateway.get_plan_drafts().first()
        assert changed_draft
        assert changed_draft.production_costs.means_cost == expected_means_cost

    def test_can_update_resource_cost(self) -> None:
        self.create_plan_draft()
        expected_resource_cost = Decimal("1.234")
        self.database_gateway.get_plan_drafts().update().set_resource_cost(
            expected_resource_cost
        ).perform()
        changed_draft = self.database_gateway.get_plan_drafts().first()
        assert changed_draft
        assert changed_draft.production_costs.resource_cost == expected_resource_cost

    def test_can_update_is_public_service(self) -> None:
        self.create_plan_draft(is_public_service=True)
        expected_is_public_service = False
        self.database_gateway.get_plan_drafts().update().set_is_public_service(
            expected_is_public_service
        ).perform()
        changed_draft = self.database_gateway.get_plan_drafts().first()
        assert changed_draft
        assert changed_draft.is_public_service == expected_is_public_service

    def test_can_update_timeframe(self) -> None:
        self.create_plan_draft()
        expected_timeframe = 43
        self.database_gateway.get_plan_drafts().update().set_timeframe(
            expected_timeframe
        ).perform()
        changed_draft = self.database_gateway.get_plan_drafts().first()
        assert changed_draft
        assert changed_draft.timeframe == expected_timeframe

    def test_can_update_unit_of_distribution(self) -> None:
        self.create_plan_draft()
        expected_unit_of_distribution = "bla unit bla"
        self.database_gateway.get_plan_drafts().update().set_unit_of_distribution(
            expected_unit_of_distribution
        ).perform()
        changed_draft = self.database_gateway.get_plan_drafts().first()
        assert changed_draft
        assert changed_draft.unit_of_distribution == expected_unit_of_distribution
