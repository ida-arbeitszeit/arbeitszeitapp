from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from injector import inject

from arbeitszeit.entities import Company, Member, ProductOffer


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
        )


class MemberGenerator:
    def create_member(self) -> Member:
        pass


@inject
@dataclass
class CompanyGenerator:
    id_generator: IdGenerator

    def create_company(self) -> Company:
        return Company(
            id=self.id_generator.get_id(),
            change_credit=lambda amount, purpose: None,
        )


class IdGenerator:
    def __init__(self):
        self.current = 0

    def get_id(self) -> int:
        self.current += 1
        return self.current
