from arbeitszeit.use_cases import (
    SynchronizedPlanActivation,
    CalculatePlanExpirationAndCheckIfExpired,
)
from project.database.repositories import PlanRepository
from project.database import with_injection, commit_changes
from project import create_app


@with_injection
def activate_database_plans(
    synchronized_plan_activation: SynchronizedPlanActivation,
    calculate_expiration: CalculatePlanExpirationAndCheckIfExpired,
    plan_repository: PlanRepository,
):
    """
    before and after plan activation plan expiration is calculated and updated.
    """
    all_active_plans = plan_repository.all_active_plans()
    for plan in all_active_plans:
        calculate_expiration(plan)

    synchronized_plan_activation()

    all_active_plans = plan_repository.all_active_plans()
    for plan in all_active_plans:
        calculate_expiration(plan)


app = create_app()
with app.app_context():
    activate_database_plans()
