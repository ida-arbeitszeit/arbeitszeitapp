from dataclasses import dataclass

from injector import inject

from arbeitszeit.entities import AccountTypes, Company
from arbeitszeit.errors import CompanyAlreadyExists
from arbeitszeit.repositories import AccountRepository, CompanyRepository


@inject
@dataclass
class RegisterCompany:
    company_repository: CompanyRepository
    account_repository: AccountRepository

    def __call__(self, email: str, name: str, password: str) -> Company:
        if self.company_repository.has_company_with_email(email):
            raise CompanyAlreadyExists()
        means_account = self.account_repository.create_account(AccountTypes.p)
        resources_account = self.account_repository.create_account(AccountTypes.r)
        labour_account = self.account_repository.create_account(AccountTypes.a)
        products_account = self.account_repository.create_account(AccountTypes.prd)
        return self.company_repository.create_company(
            email,
            name,
            password,
            means_account,
            labour_account,
            resources_account,
            products_account,
        )
