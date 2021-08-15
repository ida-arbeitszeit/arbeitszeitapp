import pytest

from arbeitszeit.use_cases import GrantCredit
from tests.dependency_injection import injection_test

from .data_generators import PlanGenerator


@injection_test
def test_that_assertion_error_is_raised_if_plan_has_not_been_approved(
    grant_credit: GrantCredit,
    plan_generator: PlanGenerator,
):
    plan = plan_generator.create_plan(approved=False)
    with pytest.raises(AssertionError):
        grant_credit(plan)
