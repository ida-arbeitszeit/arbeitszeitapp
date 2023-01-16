from arbeitszeit_web.api_presenters.interfaces import JsonDict, JsonString
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

    def test_schema_second_level_members(self) -> None:
        top_schema = self.presenter.get_schema()
        assert isinstance(top_schema, JsonDict)
        schema = top_schema.members["results"]
        assert isinstance(schema, JsonDict)

        assert len(schema.members) == 5
        for name in [
            "plan_id",
            "company_name",
            "company_id",
            "product_name",
            "description",
        ]:
            assert isinstance(schema.members[name], JsonString)
