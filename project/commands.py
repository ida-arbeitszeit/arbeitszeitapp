from arbeitszeit.use_cases import (
    CalculatePlanExpirationAndCheckIfExpired,
    SynchronizedPlanActivation,
)
from project.database import with_injection
from project.database.repositories import PlanRepository


@with_injection
def activate_database_plans(
    synchronized_plan_activation: SynchronizedPlanActivation,
    calculate_expiration: CalculatePlanExpirationAndCheckIfExpired,
    plan_repository: PlanRepository,
):
    """
    run once per day on the production server at time stored in DatetimeService().time_of_plan_activation.
    """
    all_active_plans = plan_repository.all_active_plans()
    for plan in all_active_plans:
        calculate_expiration(plan)

    synchronized_plan_activation()

    all_active_plans = plan_repository.all_active_plans()
    for plan in all_active_plans:
        calculate_expiration(plan)
