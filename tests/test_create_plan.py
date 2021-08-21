from decimal import Decimal

from arbeitszeit.entities import ProductionCosts
from arbeitszeit.use_cases import CreatePlan, PlanProposal
from tests.data_generators import CompanyGenerator
from tests.dependency_injection import injection_test
from tests.repositories import PlanRepository


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
    create_plan(planner.id, proposal)
    assert len(plan_repository) == 1
