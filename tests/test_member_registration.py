import pytest

from arbeitszeit.errors import MemberAlreadyExists
from arbeitszeit.use_cases import RegisterMember
from tests.dependency_injection import injection_test
from tests.repositories import AccountRepository


@injection_test
def test_that_registering_a_member_does_create_a_member_account(
    register_member: RegisterMember, account_repository: AccountRepository
) -> None:
    new_member = register_member("karl@cp.org", "Karl", "testpassword")
    assert new_member.account in account_repository


@injection_test
def test_that_cannot_register_user_with_same_email_twice(
    register_member: RegisterMember,
):
    email = "karl@cp.org"
    register_member(email, "karl", "testpassword")
    with pytest.raises(MemberAlreadyExists):
        register_member(email, "friedrich", "other_password")
