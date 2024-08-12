from decimal import Decimal

from parameterized import parameterized

from arbeitszeit.records import ProductionCosts
from arbeitszeit.use_cases import preview_private_consumption

from .base_test_case import BaseTestCase


class PreviewPrivateConsumptionTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.use_case = self.injector.get(
            preview_private_consumption.PreviewPrivateConsumptionUseCase
        )

    def test_that_request_without_plan_id_yields_response_without_product_info(
        self,
    ) -> None:
        request = preview_private_consumption.Request()
        response = self.use_case.preview_private_consumption(request)
        assert response.product is None

    @parameterized.expand(
        [
            ("test name",),
            ("other test name",),
        ]
    )
    def test_that_with_plan_id_for_active_plan_supplied_the_product_name_is_included_in_response(
        self, expected_product_name: str
    ) -> None:
        plan = self.plan_generator.create_plan(product_name=expected_product_name)
        request = preview_private_consumption.Request(plan=plan)
        response = self.use_case.preview_private_consumption(request)
        assert response.product and response.product.name == expected_product_name

    @parameterized.expand(
        [
            ("test description",),
            ("other description",),
        ]
    )
    def test_that_with_plan_id_for_active_plan_supplied_the_product_description_is_included_in_response(
        self, expected_product_description: str
    ) -> None:
        plan = self.plan_generator.create_plan(description=expected_product_description)
        request = preview_private_consumption.Request(plan=plan)
        response = self.use_case.preview_private_consumption(request)
        assert (
            response.product
            and response.product.description == expected_product_description
        )

    def test_that_with_amount_unset_there_is_no_total_cost_in_response(self) -> None:
        request = preview_private_consumption.Request(amount=None)
        response = self.use_case.preview_private_consumption(request)
        assert response.total_cost is None

    @parameterized.expand(
        [
            (Decimal(1),),
            (Decimal(5),),
        ]
    )
    def test_that_with_amount_of_1_the_total_cost_is_equal_to_individual_production_cost(
        self, individual_cost: Decimal
    ) -> None:
        plan = self.plan_generator.create_plan(
            costs=ProductionCosts(
                labour_cost=individual_cost,
                means_cost=Decimal(0),
                resource_cost=Decimal(0),
            ),
            amount=1,
        )
        request = preview_private_consumption.Request(amount=1, plan=plan)
        response = self.use_case.preview_private_consumption(request)
        assert response.total_cost == individual_cost

    @parameterized.expand(
        [
            (0,),
            (-1,),
        ]
    )
    def test_that_total_cost_is_only_available_for_positive_amount(
        self, amount: int
    ) -> None:
        plan = self.plan_generator.create_plan()
        request = preview_private_consumption.Request(amount=amount, plan=plan)
        response = self.use_case.preview_private_consumption(request)
        assert response.total_cost is None
