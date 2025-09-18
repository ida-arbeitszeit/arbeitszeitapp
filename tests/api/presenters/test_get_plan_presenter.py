from arbeitszeit.interactors.get_plan_details import GetPlanDetailsInteractor
from arbeitszeit_web.api.presenters.get_plan_api_presenter import GetPlanApiPresenter
from arbeitszeit_web.api.presenters.interfaces import (
    JsonBoolean,
    JsonDatetime,
    JsonDecimal,
    JsonInteger,
    JsonObject,
    JsonString,
)
from arbeitszeit_web.api.response_errors import NotFound
from tests.api.presenters.base_test_case import BaseTestCase
from tests.www.presenters.data_generators import PlanDetailsGenerator


class TestViewModelCreation(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(GetPlanApiPresenter)
        self.plan_details_generator = self.injector.get(PlanDetailsGenerator)

    def test_not_found_is_raised_if_interactor_response_is_none(self) -> None:
        with self.assertRaises(NotFound) as err:
            self.presenter.create_view_model(None)
        self.assertEqual(err.exception.message, "No plan with such ID.")

    def test_given_plan_details_gets_returned_without_changes_as_view_model(
        self,
    ) -> None:
        expected_plan_details = self.plan_details_generator.create_plan_details()
        interactor_response = GetPlanDetailsInteractor.Response(
            plan_details=expected_plan_details
        )
        view_model = self.presenter.create_view_model(interactor_response)
        self.assertEqual(view_model, expected_plan_details)


class TestSchema(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(GetPlanApiPresenter)
        self.schema = self.presenter.get_schema()

    def test_schema_top_level(self) -> None:
        assert isinstance(self.schema, JsonObject)
        assert self.schema.name == "PlanDetails"

    def test_schema_top_level_members_field_types_are_correct(self) -> None:
        assert isinstance(self.schema, JsonObject)
        field_expectations = [
            ("plan_id", JsonString),
            ("is_active", JsonBoolean),
            ("planner_id", JsonString),
            ("planner_name", JsonString),
            ("product_name", JsonString),
            ("description", JsonString),
            ("timeframe", JsonInteger),
            ("active_days", JsonInteger),
            ("production_unit", JsonString),
            ("amount", JsonInteger),
            ("means_cost", JsonDecimal),
            ("resources_cost", JsonDecimal),
            ("labour_cost", JsonDecimal),
            ("is_public_service", JsonBoolean),
            ("price_per_unit", JsonDecimal),
            ("is_cooperating", JsonBoolean),
            ("cooperation", JsonString),
            ("creation_date", JsonDatetime),
            ("approval_date", JsonDatetime),
            ("expiration_date", JsonDatetime),
        ]
        assert len(self.schema.members) == len(field_expectations)
        for field_name, expected_type in field_expectations:
            assert isinstance(self.schema.members[field_name], expected_type)

    def test_schema_top_level_members_have_correct_required_attribute(self) -> None:
        assert isinstance(self.schema, JsonObject)
        field_expectations = [
            ("plan_id", True),
            ("is_active", True),
            ("planner_id", True),
            ("planner_name", True),
            ("product_name", True),
            ("description", True),
            ("timeframe", True),
            ("active_days", True),
            ("production_unit", True),
            ("amount", True),
            ("means_cost", True),
            ("resources_cost", True),
            ("labour_cost", True),
            ("is_public_service", True),
            ("price_per_unit", True),
            ("is_cooperating", True),
            ("cooperation", False),
            ("creation_date", True),
            ("approval_date", False),
            ("expiration_date", False),
        ]
        assert len(self.schema.members) == len(field_expectations)
        for field_name, is_required in field_expectations:
            assert self.schema.members[field_name].required == is_required
