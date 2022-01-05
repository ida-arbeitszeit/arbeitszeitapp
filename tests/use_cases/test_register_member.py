from arbeitszeit.entities import AccountTypes
from arbeitszeit.use_cases import (
    RegisterMember,
    RegisterMemberRequest,
    RegisterMemberResponse,
)
from tests.data_generators import MemberGenerator

from .dependency_injection import injection_test
from .repositories import AccountRepository, MemberRepository

DEFAULT = dict(
    email="test@cp.org",
    name="test name",
    password="super safe",
    email_subject="mail confirmation",
    email_html="<p>please confirm</p>",
    email_sender="we@cp.org",
)


@injection_test
def test_that_registering_member_is_possible(
    use_case: RegisterMember,
):
    request = RegisterMemberRequest(**DEFAULT)
    response = use_case(request)
    assert not response.is_rejected


@injection_test
def test_that_registering_a_member_does_create_a_member_account(
    use_case: RegisterMember, account_repository: AccountRepository
) -> None:
    use_case(RegisterMemberRequest(**DEFAULT))
    assert len(account_repository.accounts) == 1
    assert account_repository.accounts[0].account_type == AccountTypes.member


@injection_test
def test_that_correct_member_attributes_are_registered(
    use_case: RegisterMember, member_repo: MemberRepository
):
    request = RegisterMemberRequest(**DEFAULT)
    use_case(request)
    assert len(member_repo.members) == 1
    for member in member_repo.members.values():
        assert member.email == request.email
        assert member.name == request.name
        assert member.registered_on is not None
        assert not member.confirmed


@injection_test
def test_that_correct_error_is_raised_when_user_with_mail_exists(
    use_case: RegisterMember, member_generator: MemberGenerator
):
    member_generator.create_member(email="test@cp.org")
    request = RegisterMemberRequest(**DEFAULT)
    response = use_case(request)
    assert response.is_rejected
    assert (
        response.rejection_reason
        == RegisterMemberResponse.RejectionReason.member_already_exists
    )
