from arbeitszeit.use_cases import (
    CalculatePlanExpirationAndCheckIfExpired,
    SynchronizedPlanActivation,
)
from project.database import commit_changes
from project.dependency_injection import with_injection


@commit_changes
@with_injection
def activate_database_plans(
    synchronized_plan_activation: SynchronizedPlanActivation,
    calculate_expiration: CalculatePlanExpirationAndCheckIfExpired,
):
    """
    run once per day on the production server at time stored in DatetimeService().hour_of_synchronized_plan_activation.
    """
    calculate_expiration()
    synchronized_plan_activation()
    calculate_expiration()
