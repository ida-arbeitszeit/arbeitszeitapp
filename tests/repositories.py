from decimal import Decimal
from typing import Dict, Iterator, List, Union

from injector import inject, singleton

import arbeitszeit.repositories as interfaces
from arbeitszeit.entities import (
    Account,
    AccountTypes,
    Company,
    Member,
    ProductOffer,
    Purchase,
    SocialAccounting,
    Transaction,
)


@singleton
class PurchaseRepository(interfaces.PurchaseRepository):
    @inject
    def __init__(self):
        self.purchases = []

    def add(self, purchase: Purchase):
        self.purchases.append(purchase)

    def get_purchases_descending_by_date(self, user: Union[Member, Company]):
        # order purchases by purchase_date
        self.purchases = sorted(
            self.purchases, key=lambda x: x.purchase_date, reverse=True
        )

        for purchase in self.purchases:
            if purchase.buyer is user:
                yield purchase


@singleton
class TransactionRepository(interfaces.TransactionRepository):
    @inject
    def __init__(self) -> None:
        self.transactions: List[Transaction] = []

    def add(self, transaction: Transaction) -> None:
        self.transactions.append(transaction)

    def all_transactions_sent_by_account(self, account: Account) -> List[Transaction]:
        all_sent = []
        for transaction in self.transactions:
            if transaction.account_from == account:
                all_sent.append(transaction)
        return all_sent

    def all_transactions_received_by_account(
        self, account: Account
    ) -> List[Transaction]:
        all_received = []
        for transaction in self.transactions:
            if transaction.account_to == account:
                all_received.append(transaction)
        return all_received


@singleton
class OfferRepository(interfaces.OfferRepository):
    @inject
    def __init__(self) -> None:
        self.offers: List[ProductOffer] = []

    def all_active_offers(self) -> Iterator[ProductOffer]:
        yield from self.offers

    def query_offers_by_name(self, query: str) -> Iterator[ProductOffer]:
        for offer in self.offers:
            if query in offer.name:
                yield offer

    def query_offers_by_description(self, query: str) -> Iterator[ProductOffer]:
        for offer in self.offers:
            if query in offer.description:
                yield offer

    def add_offer(self, offer: ProductOffer) -> None:
        self.offers.append(offer)


@singleton
class CompanyWorkerRepository(interfaces.CompanyWorkerRepository):
    def add_worker_to_company(self, company: Company, worker: Member) -> None:
        if worker not in company.workers:
            company.workers.append(worker)

    def get_company_workers(self, company: Company) -> List[Member]:
        return company.workers


@singleton
class AccountRepository(interfaces.AccountRepository):
    @inject
    def __init__(self):
        self.accounts = []
        self.latest_id = 0

    def __contains__(self, account: object) -> bool:
        if not isinstance(account, Account):
            return False
        return account in self.accounts

    def add(self, account: Account) -> None:
        assert account not in self
        self.accounts.append(account)

    def create_account(self, account_type: AccountTypes) -> Account:
        account = Account(
            id=self.latest_id,
            balance=Decimal(0),
            account_type=account_type,
            change_credit=lambda _: None,
        )
        self.latest_id += 1
        self.accounts.append(account)
        return account


@singleton
class AccountOwnerRepository(interfaces.AccountOwnerRepository):
    @inject
    def __init__(self):
        self.account_owner = []

    def add(self, owner: Union[Member, Company, SocialAccounting]) -> None:
        self.account_owner.append(owner)

    def get_account_owner(
        self, account: Account
    ) -> Union[Member, Company, SocialAccounting]:
        account_owner: Union[Member, Company, SocialAccounting]
        for owner in self.account_owner:
            if isinstance(owner, Member):
                if account == owner.account:
                    account_owner = owner
            elif isinstance(owner, Company):
                if account in [
                    owner.means_account,
                    owner.raw_material_account,
                    owner.work_account,
                    owner.product_account,
                ]:
                    account_owner = owner
            elif isinstance(owner, SocialAccounting):
                if account == owner.account:
                    account_owner = owner

        return account_owner


@singleton
class MemberRepository(interfaces.MemberRepository):
    @inject
    def __init__(self):
        self.members = []
        self.last_id = 0

    def create_member(
        self, email: str, name: str, password: str, account: Account
    ) -> Member:
        self.last_id += 1
        member = Member(
            id=self.last_id,
            name=name,
            email=email,
            account=account,
        )
        self.members.append(member)
        return member

    def has_member_with_email(self, email: str) -> bool:
        for member in self.members:
            if member.email == email:
                return True
        return False


@singleton
class CompanyRepository(interfaces.CompanyRepository):
    @inject
    def __init__(self) -> None:
        self.previous_id = 0
        self.companies: Dict[str, Company] = {}

    def create_company(
        self,
        email: str,
        name: str,
        password: str,
        means_account: Account,
        labour_account: Account,
        resources_account: Account,
        products_account: Account,
    ) -> Company:
        new_company = Company(
            id=self._get_id(),
            name=name,
            means_account=means_account,
            raw_material_account=resources_account,
            work_account=labour_account,
            product_account=products_account,
            workers=[],
        )
        self.companies[email] = new_company
        return new_company

    def has_company_with_email(self, email: str) -> bool:
        return email in self.companies

    def _get_id(self) -> int:
        self.previous_id += 1
        return self.previous_id
