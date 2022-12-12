from decimal import Decimal
from unittest import TestCase
from uuid import uuid4

from arbeitszeit.use_cases.query_plans import PlanQueryResponse, QueriedPlan
from arbeitszeit_web.api_presenters.fields import Fields
from arbeitszeit_web.api_presenters.list_active_plans_presenter import (
    list_active_plans_presenter_get,
)
from arbeitszeit_web.api_presenters.namespace import Namespace
from tests.api.dependency_injection import get_dependency_injector
from tests.api.fields import NestedListFieldImpl
from tests.datetime_service import FakeDatetimeService

use_case_response = PlanQueryResponse(
    results=[
        QueriedPlan(
            activation_date=FakeDatetimeService().now(),
            company_name="xxx",
            company_id=uuid4(),
            plan_id=uuid4(),
            product_name="xyxy",
            description="vvvc",
            price_per_unit=Decimal("15"),
            is_public_service=False,
            is_available=True,
            is_cooperating=False,
        )
    ]
)


def get_func():
    return use_case_response


injector = get_dependency_injector()
namespace = injector.get(Namespace)
fields = injector.get(Fields)

presenter = list_active_plans_presenter_get(
    namespace=namespace, fields=fields
)


class TestGetPresenter(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.response = presenter(get_func)

    # top level
    def test_top_level_model_has_correct_name(self):
        self.assertEqual(self.response.name, "PlanList")

    def test_top_level_has_one_object(self):
        self.assertEqual(len(self.response.model.keys()), 1)

    def test_top_level_name_is_correct(self):
        expected_name = "results"
        self.assertTrue(self.response.model[expected_name])

    # second level
    def test_second_level_model_has_correct_name(self):
        expected_name = "Plan"
        self.assertEqual(self.response.model["results"].model.name, expected_name)

    def test_second_level_object_is_nested_list(self):
        self.assertIsInstance(self.response.model["results"], NestedListFieldImpl)
