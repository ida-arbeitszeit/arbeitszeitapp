from datetime import datetime
from uuid import uuid4

from arbeitszeit.entities import AccountTypes
from arbeitszeit_flask.database.repositories import AccountRepository, MemberRepository
from tests.data_generators import MemberGenerator

from .dependency_injection import injection_test


@injection_test
def test_that_users_can_be_converted_from_and_to_orm_objects(
    member_repository: MemberRepository, account_repository: AccountRepository
):
    account = account_repository.create_account(AccountTypes.member)
    expected_member = member_repository.create_member(
        "member@cp.org", "karl", "password", account, datetime.now()
    )
    converted_member = member_repository.object_from_orm(
        member_repository.object_to_orm(
            expected_member,
        )
    )
    assert converted_member == expected_member


@injection_test
def test_that_member_can_be_retrieved_by_its_id(
    repository: MemberRepository,
    member_generator: MemberGenerator,
):
    expected_member = member_generator.create_member()
    assert repository.get_by_id(expected_member.id) == expected_member


@injection_test
def test_cannot_find_member_by_email_before_it_was_added(
    member_repository: MemberRepository,
    account_repository: AccountRepository,
):
    assert not member_repository.has_member_with_email("member@cp.org")
    account = account_repository.create_account(AccountTypes.member)
    member_repository.create_member(
        "member@cp.org", "karl", "password", account, datetime.now()
    )
    assert member_repository.has_member_with_email("member@cp.org")


@injection_test
def test_member_count_is_0_when_none_were_created(
    repository: MemberRepository,
) -> None:
    assert repository.count_registered_members() == 0


@injection_test
def test_count_one_registered_member_when_one_was_created(
    generator: MemberGenerator,
    repository: MemberRepository,
) -> None:
    generator.create_member()
    assert repository.count_registered_members() == 1


@injection_test
def test_get_by_id_returns_none_when_member_does_not_exist(
    repository: MemberRepository,
) -> None:
    member = repository.get_by_id(uuid4())
    assert member is None


@injection_test
def test_that_all_members_can_be_retrieved(
    repository: MemberRepository,
    member_generator: MemberGenerator,
):
    expected_member1 = member_generator.create_member()
    expected_member2 = member_generator.create_member()
    all_members = list(repository.get_all_members())
    assert expected_member1 in all_members
    assert expected_member2 in all_members


@injection_test
def test_that_number_of_returned_members_is_equal_to_number_of_created_members(
    repository: MemberRepository,
    member_generator: MemberGenerator,
):
    expected_number_of_members = 3
    for i in range(expected_number_of_members):
        member_generator.create_member()
    member_count = len(list(repository.get_all_members()))
    assert member_count == expected_number_of_members
