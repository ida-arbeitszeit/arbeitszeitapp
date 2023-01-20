from arbeitszeit_web.api_presenters.interfaces import (
    JsonBoolean,
    JsonDatetime,
    JsonDecimal,
    JsonDict,
    JsonString,
)
from arbeitszeit_web.api_presenters.plans import ActivePlansPresenter
from tests.api.presenters.base_test_case import BaseTestCase
from tests.presenters.data_generators import QueriedPlanGenerator


class TestGetPresenter(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.queried_plan_generator = self.injector.get(QueriedPlanGenerator)
        self.presenter = ActivePlansPresenter()

    def test_schema_top_level(self) -> None:
        schema = self.presenter.get_schema()
        assert isinstance(schema, JsonDict)
        assert schema.as_list
        assert schema.schema_name == "PlanList"

    def test_schema_top_level_members(self) -> None:
        schema = self.presenter.get_schema()
        assert isinstance(schema, JsonDict)
        assert isinstance(schema.members["results"], JsonDict)

    def test_schema_second_level(self) -> None:
        top_schema = self.presenter.get_schema()
        assert isinstance(top_schema, JsonDict)
        schema = top_schema.members["results"]
        assert isinstance(schema, JsonDict)

        assert not schema.as_list
        assert schema.schema_name == "Plan"

    def test_schema_second_level_members_field_types_are_correct(self) -> None:
        top_schema = self.presenter.get_schema()
        assert isinstance(top_schema, JsonDict)
        second_level_schema = top_schema.members["results"]
        assert isinstance(second_level_schema, JsonDict)

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

        assert len(second_level_schema.members) == len(field_expectations)

        for field_name, expected_type in field_expectations:
            assert isinstance(second_level_schema.members[field_name], expected_type)
