from uuid import uuid4

import pytest

from arbeitszeit.entities import AccountTypes
from project.database.repositories import AccountRepository, MemberRepository
from project.error import MemberNotFound

from .dependency_injection import injection_test


@injection_test
def test_that_users_can_be_converted_from_and_to_orm_objects(
    member_repository: MemberRepository, account_repository: AccountRepository
):
    account = account_repository.create_account(AccountTypes.member)
    expected_member = member_repository.create_member(
        "member@cp.org", "karl", "password", account
    )
    converted_member = member_repository.object_from_orm(
        member_repository.object_to_orm(
            expected_member,
        )
    )
    assert converted_member == expected_member


@injection_test
def test_that_members_cannot_be_retrieved_when_db_is_empty(
    member_repository: MemberRepository,
):
    with pytest.raises(MemberNotFound):
        member_repository.get_member_by_id(uuid4())


@injection_test
def test_cannot_find_member_by_email_before_it_was_added(
    member_repository: MemberRepository,
    account_repository: AccountRepository,
):
    assert not member_repository.has_member_with_email("member@cp.org")
    account = account_repository.create_account(AccountTypes.member)
    member_repository.create_member("member@cp.org", "karl", "password", account)
    assert member_repository.has_member_with_email("member@cp.org")
