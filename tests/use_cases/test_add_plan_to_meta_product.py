from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from arbeitszeit.entities import ProductionCosts
from arbeitszeit.use_cases import AddPlanToMetaProduct, AddPlanToMetaProductRequest
from tests.data_generators import MetaProductGenerator, PlanGenerator

from .dependency_injection import injection_test


@injection_test
def test_error_is_raised_when_plan_does_not_exist(
    add_plan: AddPlanToMetaProduct, meta_product_generator: MetaProductGenerator
):
    meta_product = meta_product_generator.create_meta_product()
    request = AddPlanToMetaProductRequest(
        plan_id=uuid4(), meta_product_id=meta_product.id
    )
    response = add_plan(request)
    assert response.is_rejected
    assert response.rejection_reason == response.RejectionReason.plan_not_found


@injection_test
def test_error_is_raised_when_meta_product_does_not_exist(
    add_plan: AddPlanToMetaProduct, plan_generator: PlanGenerator
):
    plan = plan_generator.create_plan()
    request = AddPlanToMetaProductRequest(plan_id=plan.id, meta_product_id=uuid4())
    response = add_plan(request)
    assert response.is_rejected
    assert response.rejection_reason == response.RejectionReason.meta_product_not_found


@injection_test
def test_error_is_raised_when_plan_is_not_active(
    add_plan: AddPlanToMetaProduct,
    meta_product_generator: MetaProductGenerator,
    plan_generator: PlanGenerator,
):
    meta_product = meta_product_generator.create_meta_product()
    plan = plan_generator.create_plan(activation_date=None)
    request = AddPlanToMetaProductRequest(
        plan_id=plan.id, meta_product_id=meta_product.id
    )
    response = add_plan(request)
    assert response.is_rejected
    assert response.rejection_reason == response.RejectionReason.plan_inactive


@injection_test
def test_error_is_raised_when_plan_is_already_associated_to_some_meta_product(
    add_plan: AddPlanToMetaProduct,
    meta_product_generator: MetaProductGenerator,
    plan_generator: PlanGenerator,
):
    meta_product1 = meta_product_generator.create_meta_product()
    meta_product2 = meta_product_generator.create_meta_product()
    plan = plan_generator.create_plan(
        activation_date=datetime.now(), meta_product=meta_product1
    )
    request = AddPlanToMetaProductRequest(
        plan_id=plan.id, meta_product_id=meta_product2.id
    )
    response = add_plan(request)
    assert response.is_rejected
    assert response.rejection_reason == response.RejectionReason.plan_has_meta_product


@injection_test
def test_error_is_raised_when_plan_is_already_in_the_list_of_associated_plans(
    add_plan: AddPlanToMetaProduct,
    meta_product_generator: MetaProductGenerator,
    plan_generator: PlanGenerator,
):
    plan = plan_generator.create_plan(activation_date=datetime.now())
    meta_product = meta_product_generator.create_meta_product(plans=[plan])
    request = AddPlanToMetaProductRequest(
        plan_id=plan.id, meta_product_id=meta_product.id
    )
    response = add_plan(request)
    assert response.is_rejected
    assert (
        response.rejection_reason
        == response.RejectionReason.plan_already_part_of_meta_product
    )


@injection_test
def test_error_is_raised_when_plan_is_public_plan(
    add_plan: AddPlanToMetaProduct,
    meta_product_generator: MetaProductGenerator,
    plan_generator: PlanGenerator,
):
    plan = plan_generator.create_plan(
        activation_date=datetime.now(), is_public_service=True
    )
    meta_product = meta_product_generator.create_meta_product()
    request = AddPlanToMetaProductRequest(
        plan_id=plan.id, meta_product_id=meta_product.id
    )
    response = add_plan(request)
    assert response.is_rejected
    assert response.rejection_reason == response.RejectionReason.plan_is_public_service


@injection_test
def test_possible_to_add_plan_to_meta_product(
    add_plan: AddPlanToMetaProduct,
    meta_product_generator: MetaProductGenerator,
    plan_generator: PlanGenerator,
):
    meta_product = meta_product_generator.create_meta_product()
    plan = plan_generator.create_plan(activation_date=datetime.now())
    request = AddPlanToMetaProductRequest(
        plan_id=plan.id, meta_product_id=meta_product.id
    )
    response = add_plan(request)
    assert not response.is_rejected


@injection_test
def test_meta_product_is_added_to_plan(
    add_plan: AddPlanToMetaProduct,
    meta_product_generator: MetaProductGenerator,
    plan_generator: PlanGenerator,
):
    meta_product = meta_product_generator.create_meta_product()
    plan = plan_generator.create_plan(activation_date=datetime.now())
    request = AddPlanToMetaProductRequest(
        plan_id=plan.id, meta_product_id=meta_product.id
    )
    add_plan(request)
    assert plan.meta_product == meta_product


@injection_test
def test_plan_is_added_to_meta_product(
    add_plan: AddPlanToMetaProduct,
    meta_product_generator: MetaProductGenerator,
    plan_generator: PlanGenerator,
):
    meta_product = meta_product_generator.create_meta_product()
    plan = plan_generator.create_plan(activation_date=datetime.now())
    request = AddPlanToMetaProductRequest(
        plan_id=plan.id, meta_product_id=meta_product.id
    )
    add_plan(request)
    assert meta_product.plans[0] == plan


@injection_test
def test_two_cooperating_plans_have_same_prices(
    add_plan: AddPlanToMetaProduct,
    meta_product_generator: MetaProductGenerator,
    plan_generator: PlanGenerator,
):
    meta_product = meta_product_generator.create_meta_product()
    plan1 = plan_generator.create_plan(
        activation_date=datetime.now(),
        costs=ProductionCosts(Decimal(10), Decimal(20), Decimal(30)),
    )
    plan2 = plan_generator.create_plan(
        activation_date=datetime.now(),
        costs=ProductionCosts(Decimal(1), Decimal(2), Decimal(3)),
    )
    request1 = AddPlanToMetaProductRequest(
        plan_id=plan1.id, meta_product_id=meta_product.id
    )
    request2 = AddPlanToMetaProductRequest(
        plan_id=plan2.id, meta_product_id=meta_product.id
    )
    add_plan(request1)
    add_plan(request2)
    assert plan1.price_per_unit == plan2.price_per_unit


@injection_test
def test_price_of_cooperating_plans_is_correctly_calculated(
    add_plan: AddPlanToMetaProduct,
    meta_product_generator: MetaProductGenerator,
    plan_generator: PlanGenerator,
):
    meta_product = meta_product_generator.create_meta_product()
    plan1 = plan_generator.create_plan(
        activation_date=datetime.now(),
        costs=ProductionCosts(Decimal(10), Decimal(5), Decimal(5)),
        amount=10,
    )
    plan2 = plan_generator.create_plan(
        activation_date=datetime.now(),
        costs=ProductionCosts(Decimal(5), Decimal(3), Decimal(2)),
        amount=10,
    )
    request1 = AddPlanToMetaProductRequest(
        plan_id=plan1.id, meta_product_id=meta_product.id
    )
    request2 = AddPlanToMetaProductRequest(
        plan_id=plan2.id, meta_product_id=meta_product.id
    )
    add_plan(request1)
    add_plan(request2)
    # In total costs of 30h and 20 units -> price should be 1.5h per unit
    assert plan1.price_per_unit == plan2.price_per_unit == Decimal("1.5")
