from decimal import Decimal
from uuid import UUID

import pytest

from arbeitszeit.entities import ProductionCosts
from arbeitszeit.use_cases import CreatePlan, PlanProposal
from tests.data_generators import CompanyGenerator, PlanGenerator

from .dependency_injection import injection_test
from .repositories import PlanRepository


@injection_test
def test_that_create_plan_creates_a_plan(
    plan_repository: PlanRepository,
    create_plan: CreatePlan,
    company_generator: CompanyGenerator,
):
    planner = company_generator.create_company()
    proposal = PlanProposal(
        costs=ProductionCosts(
            Decimal(1),
            Decimal(1),
            Decimal(1),
        ),
        product_name="testproduct",
        production_unit="kg",
        production_amount=10,
        description="test description",
        is_public_service=False,
        timeframe_in_days=7,
    )

    assert not len(plan_repository)
    create_plan(planner.id, proposal, None)
    assert len(plan_repository) == 1


@injection_test
def test_that_new_plan_has_same_uuid_as_old_plan(
    create_plan: CreatePlan,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
):
    old_plan = plan_generator.create_plan()
    planner = company_generator.create_company()
    proposal = PlanProposal(
        costs=ProductionCosts(
            Decimal(1),
            Decimal(1),
            Decimal(1),
        ),
        product_name="testproduct",
        production_unit="kg",
        production_amount=10,
        description="test description",
        is_public_service=False,
        timeframe_in_days=7,
    )

    response = create_plan(planner.id, proposal, old_plan.id)
    assert response.plan_id == old_plan.id


@injection_test
def test_that_product_name_of_plan_proposel_has_replaced_the_product_name_of_old_plan(
    create_plan: CreatePlan,
    company_generator: CompanyGenerator,
    plan_generator: PlanGenerator,
    plan_repository: PlanRepository,
):
    old_plan = plan_generator.create_plan(product_name="Old product name")
    planner = company_generator.create_company()
    proposal = PlanProposal(
        costs=ProductionCosts(
            Decimal(1),
            Decimal(1),
            Decimal(1),
        ),
        product_name="New product name",
        production_unit="kg",
        production_amount=10,
        description="test description",
        is_public_service=False,
        timeframe_in_days=7,
    )

    response = create_plan(planner.id, proposal, old_plan.id)
    assert len(plan_repository.plans) == 1
    assert plan_repository.plans[response.plan_id].prd_name == "New product name"


@injection_test
def test_that_error_is_raised_if_nonexisting_plan_should_be_renewed(
    create_plan: CreatePlan,
    company_generator: CompanyGenerator,
):
    non_existing_plan_id = UUID("b811238d-eeb3-478d-acba-e10e43e38eb9")
    planner = company_generator.create_company()
    proposal = PlanProposal(
        costs=ProductionCosts(
            Decimal(1),
            Decimal(1),
            Decimal(1),
        ),
        product_name="New product name",
        production_unit="kg",
        production_amount=10,
        description="test description",
        is_public_service=False,
        timeframe_in_days=7,
    )
    with pytest.raises(AssertionError, match="Plan not found"):
        create_plan(planner.id, proposal, non_existing_plan_id)
