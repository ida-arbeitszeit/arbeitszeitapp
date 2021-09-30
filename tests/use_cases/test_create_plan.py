from decimal import Decimal

from arbeitszeit.entities import ProductionCosts
from arbeitszeit.use_cases import CreatePlanDraft, CreatePlanDraftRequest
from tests.data_generators import CompanyGenerator

from .dependency_injection import injection_test
from .repositories import PlanDraftRepository


@injection_test
def test_that_create_plan_creates_a_plan_draft(
    plan_draft_repository: PlanDraftRepository,
    create_plan: CreatePlanDraft,
    company_generator: CompanyGenerator,
):
    planner = company_generator.create_company()
    request = CreatePlanDraftRequest(
        planner=planner.id,
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

    assert not len(plan_draft_repository)
    create_plan(request)
    assert len(plan_draft_repository) == 1
