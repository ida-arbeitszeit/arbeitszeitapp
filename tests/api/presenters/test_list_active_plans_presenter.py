from arbeitszeit_web.api_presenters.plans import list_plans_presenter
from tests.api.helper import (
    DecimalImpl,
    FieldTypes,
    NamespaceImpl,
    NestedImpl,
    StringImpl,
)
from tests.api.presenters.base_test_case import BaseTestCase
from tests.presenters.data_generators import QueriedPlanGenerator


class TestGetPresenter(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.queried_plan_generator = self.injector.get(QueriedPlanGenerator)
        self.namespace = NamespaceImpl("test name", "test description")
        self.expected_top_level = "results"
        self.expected_2nd_level = [
            "plan_id",
            "company_name",
            "company_id",
            "product_name",
            "description",
            "price_per_unit",
        ]

    def test_no_models_are_registered_in_namespace_by_default(self):
        assert not self.namespace.models

    def test_two_models_get_registered_in_namespace_when_presenter_is_initiated(self):
        self.presenter_decorator
        assert len(self.namespace.models) == 2
        assert "Plan" in self.namespace.models.keys()
        assert "PlanList" in self.namespace.models.keys()

    def test_top_level_has_correct_name(self):
        fields = self.presenter_decorator.model.keys()
        assert len(fields) == 1
        assert self.expected_top_level in fields

    def test_top_level_has_correct_type(self):
        m = self.presenter_decorator.model
        assert isinstance(m[self.expected_top_level], NestedImpl)

    def test_second_level_has_correct_names(self):
        fields = self.presenter_decorator.model[self.expected_top_level].model
        assert len(fields) == 6
        for expected in self.expected_2nd_level:
            assert expected in fields

    def test_second_level_has_correct_types(self):
        second_level = self.presenter_decorator.model[self.expected_top_level].model
        expected_types = [
            StringImpl,
            StringImpl,
            StringImpl,
            StringImpl,
            StringImpl,
            DecimalImpl,
        ]
        for count, expected in enumerate(self.expected_2nd_level):
            assert second_level[expected] == expected_types[count]

    def test_function_gets_marshalled(self):
        assert self.marshalled_response.has_been_marshalled

    @property
    def presenter_decorator(self) -> list_plans_presenter:
        presenter_decorator = list_plans_presenter(
            namespace=self.namespace, fields=FieldTypes()
        )
        return presenter_decorator

    @property
    def marshalled_response(self):
        use_case_response = self.queried_plan_generator.get_response(
            [self.queried_plan_generator.get_plan()]
        )
        response = self.presenter_decorator(lambda: use_case_response)
        return response
