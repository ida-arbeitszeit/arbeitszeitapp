from arbeitszeit.use_cases import (
    CalculatePlanExpirationAndCheckIfExpired,
    SynchronizedPlanActivation,
)
from project.database.repositories import PlanRepository
from project.dependency_injection import with_injection


@with_injection
def activate_database_plans(
    synchronized_plan_activation: SynchronizedPlanActivation,
    calculate_expiration: CalculatePlanExpirationAndCheckIfExpired,
    plan_repository: PlanRepository,
):
    """
    run once per day on the production server at time stored in DatetimeService().time_of_synchronized_plan_activation.
    """
    calculate_expiration()
    synchronized_plan_activation()
    calculate_expiration()
