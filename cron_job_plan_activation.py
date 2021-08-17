from arbeitszeit.use_cases import (
    SynchronizedPlanActivation,
    CalculatePlanExpirationAndCheckIfExpired,
)
from project.database.repositories import PlanRepository
from project.database import with_injection
from project import create_app


@with_injection
def activate_database_plans(
    synchronized_plan_activation: SynchronizedPlanActivation,
    calculate_expiration: CalculatePlanExpirationAndCheckIfExpired,
    plan_repository: PlanRepository,
):
    """
    run once per day at time stored in DatetimeService().time_of_plan_activation.
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
