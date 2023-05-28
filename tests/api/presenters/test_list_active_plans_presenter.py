from arbeitszeit_web.api_presenters.interfaces import (
    JsonBoolean,
    JsonDatetime,
    JsonDecimal,
    JsonInteger,
    JsonObject,
    JsonString,
)
from arbeitszeit_web.api_presenters.query_plans_api_presenter import (
    QueryPlansApiPresenter,
)
from tests.api.presenters.base_test_case import BaseTestCase
from tests.presenters.data_generators import QueriedPlanGenerator


class TestViewModelCreation(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(QueryPlansApiPresenter)
        self.queried_plan_generator = self.injector.get(QueriedPlanGenerator)

    def test_presenter_shows_limit_as_None_when_no_limit_was_requested(self):
        use_case_response = self.queried_plan_generator.get_response(
            requested_limit=None, requested_offset=10
        )
        view_model = self.presenter.create_view_model(use_case_response)
        self.assertIsNone(view_model.limit)

    def test_presenter_shows_offset_as_None_when_no_offset_was_requested(self):
        use_case_response = self.queried_plan_generator.get_response(
            requested_offset=None, requested_limit=10
        )
        view_model = self.presenter.create_view_model(use_case_response)
        self.assertIsNone(view_model.offset)

    def test_view_model_shows_requested_offset(self):
        use_case_response = self.queried_plan_generator.get_response(
            queried_plans=[], requested_offset=5, requested_limit=10
        )
        view_model = self.presenter.create_view_model(use_case_response)
        self.assertEqual(view_model.offset, 5)

    def test_view_model_shows_requested_limit(self):
        use_case_response = self.queried_plan_generator.get_response(
            queried_plans=[], requested_offset=5, requested_limit=10
        )
        view_model = self.presenter.create_view_model(use_case_response)
        self.assertEqual(view_model.limit, 10)

    def test_view_model_shows_same_total_results_as_use_case(self):
        use_case_response = self.queried_plan_generator.get_response(
            total_results=12, requested_offset=5, requested_limit=10
        )
        view_model = self.presenter.create_view_model(use_case_response)
        self.assertEqual(view_model.total_results, 12)

    def test_view_model_has_no_results_if_use_case_response_has_no_queried_plan(self):
        use_case_response = self.queried_plan_generator.get_response(
            queried_plans=[], requested_offset=0, requested_limit=10
        )
        view_model = self.presenter.create_view_model(use_case_response)
        self.assertEqual(len(view_model.results), 0)

    def test_view_model_has_one_result_if_use_case_response_has_one_queried_plan(self):
        plan = self.queried_plan_generator.get_plan()
        use_case_response = self.queried_plan_generator.get_response(
            queried_plans=[plan], requested_offset=0, requested_limit=10
        )
        view_model = self.presenter.create_view_model(use_case_response)
        self.assertEqual(len(view_model.results), 1)


class TestSchema(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.queried_plan_generator = self.injector.get(QueriedPlanGenerator)
        self.presenter = QueryPlansApiPresenter()

    def test_schema_top_level(self) -> None:
        schema = self.presenter.get_schema()
        assert isinstance(schema, JsonObject)
        assert not schema.as_list
        assert schema.name == "PlanList"

    def test_schema_top_level_members(self) -> None:
        schema = self.presenter.get_schema()
        assert isinstance(schema, JsonObject)
        assert isinstance(schema.members["results"], JsonObject)

    def test_schema_top_level_members_field_types_are_correct(self) -> None:
        top_level_schema = self.presenter.get_schema()
        assert isinstance(top_level_schema, JsonObject)

        field_expectations = [
            ("results", JsonObject),
            ("total_results", JsonInteger),
            ("offset", JsonInteger),
            ("limit", JsonInteger),
        ]

        assert len(top_level_schema.members) == len(field_expectations)

        for field_name, expected_type in field_expectations:
            assert isinstance(top_level_schema.members[field_name], expected_type)

    def test_results_is_dictionary(self) -> None:
        schema = self.presenter.get_schema()
        assert isinstance(schema, JsonObject)
        results_schema = schema.members["results"]
        assert isinstance(results_schema, JsonObject)

    def test_results_is_dictionary_as_list(self) -> None:
        schema = self.presenter.get_schema()
        assert isinstance(schema, JsonObject)
        results_schema = schema.members["results"]
        assert isinstance(results_schema, JsonObject)
        assert results_schema.as_list

    def test_results_has_correct_schema_name(self) -> None:
        schema = self.presenter.get_schema()
        assert isinstance(schema, JsonObject)
        results_schema = schema.members["results"]
        assert isinstance(results_schema, JsonObject)
        assert results_schema.name == "Plan"

    def test_results_members_field_types_are_correct(self) -> None:
        schema = self.presenter.get_schema()
        assert isinstance(schema, JsonObject)
        results_schema = schema.members["results"]
        assert isinstance(results_schema, JsonObject)

        field_expectations = [
            ("plan_id", JsonString),
            ("company_name", JsonString),
            ("company_id", JsonString),
            ("product_name", JsonString),
            ("description", JsonString),
            ("is_public_service", JsonBoolean),
            ("is_available", JsonBoolean),
            ("is_cooperating", JsonBoolean),
            ("price_per_unit", JsonDecimal),
            ("activation_date", JsonDatetime),
        ]

        assert len(results_schema.members) == len(field_expectations)

        for field_name, expected_type in field_expectations:
            assert isinstance(results_schema.members[field_name], expected_type)
