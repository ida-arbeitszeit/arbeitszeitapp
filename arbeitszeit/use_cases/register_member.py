from dataclasses import dataclass

from injector import inject

from arbeitszeit.entities import AccountTypes, Member
from arbeitszeit.errors import MemberAlreadyExists
from arbeitszeit.repositories import AccountRepository, MemberRepository


@inject
@dataclass
class RegisterMember:
    account_repository: AccountRepository
    member_repository: MemberRepository

    def __call__(self, email: str, name: str, password: str) -> Member:
        if self.member_repository.has_member_with_email(email):
            raise MemberAlreadyExists(
                f"A member with the email address {email} already exists"
            )
        member_account = self.account_repository.create_account(AccountTypes.member)
        return self.member_repository.create_member(
            email, name, password, member_account
        )
