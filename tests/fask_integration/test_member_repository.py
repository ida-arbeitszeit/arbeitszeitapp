from arbeitszeit.entities import AccountTypes
from project.database.repositories import AccountRepository, MemberRepository
from tests.dependency_injection import injection_test


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
