from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from injector import inject

from arbeitszeit.entities import Account, Company, Member, ProductOffer


@inject
@dataclass
class OfferGenerator:
    id_generator: IdGenerator
    company_generator: CompanyGenerator

    def create_offer(self, *, amount=1, provider=None):
        return ProductOffer(
            id=self.id_generator.get_id(),
            amount_available=amount,
            deactivate_offer_in_db=lambda: None,
            decrease_amount_available=lambda _: None,
            price_per_unit=Decimal(1),
            provider=self.company_generator.create_company()
            if provider is None
            else provider,
            active=True,
        )


class MemberGenerator:
    def create_member(self) -> Member:
        pass


@inject
@dataclass
class CompanyGenerator:
    id_generator: IdGenerator
    account_generator: AccountGenerator

    def create_company(self) -> Company:
        return Company(
            id=self.id_generator.get_id(),
            means_account=self.account_generator.create_account(account_type="p"),
            raw_material_account=self.account_generator.create_account(
                account_type="r"
            ),
            work_account=self.account_generator.create_account(account_type="a"),
            product_account=self.account_generator.create_account(account_type="prd"),
        )


class IdGenerator:
    def __init__(self):
        self.current = 0

    def get_id(self) -> int:
        self.current += 1
        return self.current


@inject
@dataclass
class AccountGenerator:
    id_generator: IdGenerator

    def create_account(self, account_type="p", balance=0) -> Account:
        return Account(
            id=self.id_generator.get_id(),
            account_owner_id=self.id_generator.get_id(),
            account_type=account_type,
            balance=balance,
            change_credit=lambda amount: None,
        )
