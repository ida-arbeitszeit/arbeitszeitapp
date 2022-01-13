from arbeitszeit.use_cases import UpdatePlansAndPayout
from project.database import commit_changes
from project.dependency_injection import with_injection


@commit_changes
@with_injection()
def update_and_payout(
    payout: UpdatePlansAndPayout,
):
    """
    run every hour on production server or call manually from CLI `flask payout`.
    """
    payout()
