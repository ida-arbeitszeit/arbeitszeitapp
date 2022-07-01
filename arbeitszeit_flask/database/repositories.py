from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Iterable, Iterator, List, Optional, Union
from uuid import UUID, uuid4

from flask_sqlalchemy import SQLAlchemy
from injector import inject
from sqlalchemy import and_, desc, func
from werkzeug.security import check_password_hash, generate_password_hash

from arbeitszeit import entities, repositories
from arbeitszeit.decimal import decimal_sum
from arbeitszeit_flask import models
from arbeitszeit_flask.models import (
    Account,
    AccountTypes,
    Company,
    CompanyWorkInvite,
    Cooperation,
    Member,
    Plan,
    PlanDraft,
    Purchase,
    SocialAccounting,
    Transaction,
)


@inject
@dataclass
class CompanyWorkerRepository(repositories.CompanyWorkerRepository):
    member_repository: MemberRepository
    company_repository: CompanyRepository

    def add_worker_to_company(
        self, company: entities.Company, worker: entities.Member
    ) -> None:
        company_orm = self.company_repository.object_to_orm(company)
        worker_orm = self.member_repository.object_to_orm(worker)
        if worker_orm not in company_orm.workers:
            company_orm.workers.append(worker_orm)

    def get_company_workers(self, company: entities.Company) -> List[entities.Member]:
        company_orm = self.company_repository.object_to_orm(company)
        return [
            self.member_repository.object_from_orm(member)
            for member in company_orm.workers
        ]

    def get_member_workplaces(self, member: UUID) -> List[entities.Company]:
        member_orm = Member.query.filter_by(id=str(member)).first()
        if member_orm is None:
            return []
        workplaces_orm = member_orm.workplaces.all()
        return [
            self.company_repository.object_from_orm(workplace_orm)
            for workplace_orm in workplaces_orm
        ]


@dataclass
class UserAddressBookImpl:
    db: SQLAlchemy

    def get_user_email_address(self, user: UUID) -> Optional[str]:
        user_orm = (
            self.db.session.query(models.User)
            .join(models.Member, isouter=True)
            .join(models.Company, isouter=True)
            .filter((models.Member.id == str(user)) | (models.Company.id == str(user)))
            .first()
        )
        if user_orm:
            return user_orm.email
        else:
            return None


@inject
@dataclass
class MemberRepository(repositories.MemberRepository):
    account_repository: AccountRepository
    db: SQLAlchemy

    def get_by_id(self, id: UUID) -> Optional[entities.Member]:
        orm_object = Member.query.filter_by(id=str(id)).first()
        if orm_object is None:
            return None
        return self.object_from_orm(orm_object)

    def validate_credentials(self, email: str, password: str) -> Optional[UUID]:
        if (
            member := self.db.session.query(Member)
            .join(models.User)
            .filter(models.User.email == email)
            .first()
        ):
            if check_password_hash(member.user.password, password):
                return UUID(member.id)
        return None

    def get_member_orm_by_mail(self, email: str) -> Member:
        member_orm = (
            self.db.session.query(models.Member)
            .join(models.User)
            .filter(models.User.email == email)
            .first()
        )
        assert member_orm
        return member_orm

    def object_from_orm(self, orm_object: Member) -> entities.Member:
        member_account = self.account_repository.object_from_orm(orm_object.account)
        return entities.Member(
            id=UUID(orm_object.id),
            name=orm_object.name,
            account=member_account,
            email=orm_object.user.email,
            registered_on=orm_object.registered_on,
            confirmed_on=orm_object.confirmed_on,
        )

    def object_to_orm(self, member: entities.Member) -> Member:
        return Member.query.get(str(member.id))

    def create_member(
        self,
        email: str,
        name: str,
        password: str,
        account: entities.Account,
        registered_on: datetime,
    ) -> entities.Member:
        orm_account = self.account_repository.object_to_orm(account)
        user_orm = self._get_or_create_user(email, password)
        orm_member = Member(
            id=str(uuid4()),
            user=user_orm,
            name=name,
            account=orm_account,
            registered_on=registered_on,
            confirmed_on=None,
        )
        orm_account.account_owner_member = orm_member.id
        self.db.session.add(orm_member)
        return self.object_from_orm(orm_member)

    def has_member_with_email(self, email: str) -> bool:
        return bool(
            self.db.session.query(models.Member)
            .join(models.User)
            .filter(models.User.email == email)
            .count()
        )

    def count_registered_members(self) -> int:
        return int(self.db.session.query(func.count(Member.id)).one()[0])

    def get_all_members(self) -> Iterator[entities.Member]:
        return (self.object_from_orm(member) for member in Member.query.all())

    def _get_or_create_user(self, email: str, password: str) -> models.User:
        return self.db.session.query(models.User).filter(
            and_(
                models.User.email == email,
                models.User.member == None,
            )
        ).first() or models.User(
            email=email,
            password=generate_password_hash(password, method="sha256"),
        )


@inject
@dataclass
class CompanyRepository(repositories.CompanyRepository):
    account_repository: AccountRepository
    db: SQLAlchemy

    def object_to_orm(self, company: entities.Company) -> Company:
        return Company.query.get(str(company.id))

    def object_from_orm(self, company_orm: Company) -> entities.Company:
        return entities.Company(
            id=UUID(company_orm.id),
            email=company_orm.user.email,
            name=company_orm.name,
            means_account=self.account_repository.object_from_orm(
                self._get_means_account(company_orm)
            ),
            raw_material_account=self.account_repository.object_from_orm(
                self._get_resources_account(company_orm)
            ),
            work_account=self.account_repository.object_from_orm(
                self._get_labour_account(company_orm)
            ),
            product_account=self.account_repository.object_from_orm(
                self._get_products_account(company_orm)
            ),
            registered_on=company_orm.registered_on,
            confirmed_on=company_orm.confirmed_on,
        )

    def _get_means_account(self, company: Company) -> Account:
        account = company.accounts.filter_by(account_type="p").first()
        assert account
        return account

    def _get_resources_account(self, company: Company) -> Account:
        account = company.accounts.filter_by(account_type="r").first()
        assert account
        return account

    def _get_labour_account(self, company: Company) -> Account:
        account = company.accounts.filter_by(account_type="a").first()
        assert account
        return account

    def _get_products_account(self, company: Company) -> Account:
        account = company.accounts.filter_by(account_type="prd").first()
        assert account
        return account

    def get_company_orm_by_mail(self, email: str) -> Company:
        company_orm = (
            self.db.session.query(models.Company)
            .join(models.User)
            .filter(models.User.email == email)
            .first()
        )
        assert company_orm
        return company_orm

    def get_by_id(self, id: UUID) -> Optional[entities.Company]:
        company_orm = Company.query.filter_by(id=str(id)).first()
        if company_orm is None:
            return None
        else:
            return self.object_from_orm(company_orm)

    def create_company(
        self,
        email: str,
        name: str,
        password: str,
        means_account: entities.Account,
        labour_account: entities.Account,
        resource_account: entities.Account,
        products_account: entities.Account,
        registered_on: datetime,
    ) -> entities.Company:
        user_orm = self._get_or_create_user(email, password)
        company = Company(
            id=str(uuid4()),
            name=name,
            registered_on=registered_on,
            confirmed_on=None,
            user=user_orm,
        )
        self.db.session.add(company)
        for account in [
            means_account,
            labour_account,
            resource_account,
            products_account,
        ]:
            account_orm = self.account_repository.object_to_orm(account)
            account_orm.account_owner_company = company.id
        return self.object_from_orm(company)

    def has_company_with_email(self, email: str) -> bool:
        return bool(
            self.db.session.query(models.Company)
            .join(models.User)
            .filter(models.User.email == email)
            .first()
        )

    def count_registered_companies(self) -> int:
        return int(self.db.session.query(func.count(Company.id)).one()[0])

    def query_companies_by_name(self, query: str) -> Iterator[entities.Company]:
        return (
            self.object_from_orm(company)
            for company in Company.query.filter(
                Company.name.ilike("%" + query + "%")
            ).all()
        )

    def query_companies_by_email(self, query: str) -> Iterator[entities.Company]:
        companies = (
            self.db.session.query(models.Company)
            .join(models.User)
            .filter(models.User.email.ilike("%" + query + "%"))
        )
        return (self.object_from_orm(company) for company in companies)

    def get_all_companies(self) -> Iterator[entities.Company]:
        return (self.object_from_orm(company) for company in Company.query.all())

    def validate_credentials(self, email_address: str, password: str) -> Optional[UUID]:
        if (
            company := self.db.session.query(models.Company)
            .join(models.User)
            .filter(models.User.email == email_address)
            .first()
        ):
            if check_password_hash(company.user.password, password):
                return UUID(company.id)
        return None

    def _get_or_create_user(self, email: str, password: str) -> models.User:
        return self.db.session.query(models.User).filter(
            and_(
                models.User.email == email,
                models.User.company == None,
            )
        ).first() or models.User(
            email=email,
            password=generate_password_hash(password, method="sha256"),
        )


@inject
@dataclass
class AccountRepository(repositories.AccountRepository):
    db: SQLAlchemy

    def object_from_orm(self, account_orm: Account) -> entities.Account:
        assert account_orm
        return entities.Account(
            id=UUID(account_orm.id),
            account_type=self._transform_account_type(account_orm.account_type),
        )

    def _transform_account_type(
        self, orm_account_type: AccountTypes
    ) -> entities.AccountTypes:
        if orm_account_type == AccountTypes.p:
            return entities.AccountTypes.p
        elif orm_account_type == AccountTypes.r:
            return entities.AccountTypes.r
        elif orm_account_type == AccountTypes.a:
            return entities.AccountTypes.a
        elif orm_account_type == AccountTypes.prd:
            return entities.AccountTypes.prd
        elif orm_account_type == AccountTypes.member:
            return entities.AccountTypes.member
        else:
            return entities.AccountTypes.accounting

    def object_to_orm(self, account: entities.Account) -> Account:
        account_orm = Account.query.filter_by(id=str(account.id)).first()
        assert account_orm
        return account_orm

    def create_account(self, account_type: entities.AccountTypes) -> entities.Account:
        account = Account(id=str(uuid4()), account_type=account_type.value)
        self.db.session.add(account)
        return self.object_from_orm(account)

    def get_account_balance(self, account: entities.Account) -> Decimal:
        account_orm = self.object_to_orm(account)
        received = set(account_orm.transactions_received)
        sent = set(account_orm.transactions_sent)
        intersection = received & sent
        received -= intersection
        sent -= intersection
        return decimal_sum(t.amount_received for t in received) - decimal_sum(
            t.amount_sent for t in sent
        )

    def get_by_id(self, id: UUID) -> entities.Account:
        return self.object_from_orm(Account.query.get(str(id)))


@inject
@dataclass
class AccountOwnerRepository(repositories.AccountOwnerRepository):
    account_repository: AccountRepository
    member_repository: MemberRepository
    company_repository: CompanyRepository
    social_accounting_repository: AccountingRepository

    def get_account_owner(
        self, account: entities.Account
    ) -> Union[entities.Member, entities.Company, entities.SocialAccounting]:
        account_owner: Union[
            entities.Member, entities.Company, entities.SocialAccounting
        ]
        account_orm = self.account_repository.object_to_orm(account)
        if account_orm.account_owner_member:
            account_owner = self.member_repository.object_from_orm(account_orm.member)
        elif account_orm.account_owner_company:
            account_owner = self.company_repository.object_from_orm(account_orm.company)
        elif account_orm.account_owner_social_accounting:
            account_owner = self.social_accounting_repository.object_from_orm(
                account_orm.social_accounting
            )

        assert account_owner
        return account_owner


@inject
@dataclass
class AccountingRepository:
    account_repository: AccountRepository
    db: SQLAlchemy

    def object_from_orm(
        self, accounting_orm: SocialAccounting
    ) -> entities.SocialAccounting:
        accounting_account_orm = accounting_orm.account
        accounting_account = self.account_repository.object_from_orm(
            accounting_account_orm
        )
        return entities.SocialAccounting(
            account=accounting_account,
            id=UUID(accounting_orm.id),
        )

    def get_or_create_social_accounting(self) -> entities.SocialAccounting:
        return self.object_from_orm(self.get_or_create_social_accounting_orm())

    def get_or_create_social_accounting_orm(self) -> SocialAccounting:
        social_accounting = SocialAccounting.query.first()
        if not social_accounting:
            social_accounting = SocialAccounting(
                id=str(uuid4()),
            )
            account = self.account_repository.create_account(
                entities.AccountTypes.accounting
            )
            social_accounting.account = self.account_repository.object_to_orm(account)
            self.db.session.add(social_accounting, account)
        return social_accounting

    def get_by_id(self, id: UUID) -> Optional[entities.SocialAccounting]:
        accounting_orm = SocialAccounting.query.filter_by(id=str(id)).first()
        if accounting_orm is None:
            return None
        return self.object_from_orm(accounting_orm)


@inject
@dataclass
class PurchaseRepository(repositories.PurchaseRepository):
    member_repository: MemberRepository
    company_repository: CompanyRepository
    db: SQLAlchemy

    def object_to_orm(self, purchase: entities.Purchase) -> Purchase:
        return Purchase(
            purchase_date=purchase.purchase_date,
            plan_id=str(purchase.plan),
            type_member=purchase.is_buyer_a_member,
            company=str(purchase.buyer) if not purchase.is_buyer_a_member else None,
            member=str(purchase.buyer) if purchase.is_buyer_a_member else None,
            price_per_unit=float(purchase.price_per_unit),
            amount=purchase.amount,
            purpose=purchase.purpose.value,
        )

    def object_from_orm(self, purchase: Purchase) -> entities.Purchase:
        return entities.Purchase(
            purchase_date=purchase.purchase_date,
            plan=UUID(purchase.plan_id),
            buyer=UUID(purchase.member)
            if purchase.type_member
            else UUID(purchase.company),
            is_buyer_a_member=purchase.type_member,
            price_per_unit=Decimal(purchase.price_per_unit),
            amount=purchase.amount,
            purpose=purchase.purpose,
        )

    def create_purchase_by_company(
        self,
        purchase_date: datetime,
        plan: UUID,
        buyer: UUID,
        price_per_unit: Decimal,
        amount: int,
        purpose: entities.PurposesOfPurchases,
    ) -> entities.Purchase:
        purchase = entities.Purchase(
            purchase_date=purchase_date,
            plan=plan,
            buyer=buyer,
            is_buyer_a_member=False,
            price_per_unit=price_per_unit,
            amount=amount,
            purpose=purpose,
        )
        purchase_orm = self.object_to_orm(purchase)
        self.db.session.add(purchase_orm)
        return purchase

    def create_purchase_by_member(
        self,
        purchase_date: datetime,
        plan: UUID,
        buyer: UUID,
        price_per_unit: Decimal,
        amount: int,
    ) -> entities.Purchase:
        purchase = entities.Purchase(
            purchase_date=purchase_date,
            plan=plan,
            buyer=buyer,
            is_buyer_a_member=True,
            price_per_unit=price_per_unit,
            amount=amount,
            purpose=entities.PurposesOfPurchases.consumption,
        )
        purchase_orm = self.object_to_orm(purchase)
        self.db.session.add(purchase_orm)
        return purchase

    def get_purchases_descending_by_date(
        self, user: Union[entities.Member, entities.Company]
    ) -> Iterator[entities.Purchase]:
        user_orm: Union[Member, Company]
        if isinstance(user, entities.Company):
            user_orm = self.company_repository.object_to_orm(user)
        else:
            user_orm = self.member_repository.object_to_orm(user)
        return (
            self.object_from_orm(purchase)
            for purchase in user_orm.purchases.order_by(desc("purchase_date")).all()
        )


@inject
@dataclass
class PlanRepository(repositories.PlanRepository):
    company_repository: CompanyRepository
    db: SQLAlchemy

    def object_from_orm(self, plan: Plan) -> entities.Plan:
        production_costs = entities.ProductionCosts(
            labour_cost=plan.costs_a,
            resource_cost=plan.costs_r,
            means_cost=plan.costs_p,
        )
        planner = self.company_repository.get_by_id(UUID(plan.planner))
        assert planner is not None
        return entities.Plan(
            id=UUID(plan.id),
            plan_creation_date=plan.plan_creation_date,
            planner=planner,
            production_costs=production_costs,
            prd_name=plan.prd_name,
            prd_unit=plan.prd_unit,
            prd_amount=plan.prd_amount,
            description=plan.description,
            timeframe=int(plan.timeframe),
            is_public_service=plan.is_public_service,
            approval_date=plan.approval_date,
            approval_reason=plan.approval_reason,
            is_active=plan.is_active,
            expired=plan.expired,
            expiration_date=plan.expiration_date,
            activation_date=plan.activation_date,
            active_days=plan.active_days,
            payout_count=plan.payout_count,
            requested_cooperation=UUID(plan.requested_cooperation)
            if plan.requested_cooperation
            else None,
            cooperation=UUID(plan.cooperation) if plan.cooperation else None,
            is_available=plan.is_available,
            hidden_by_user=plan.hidden_by_user,
        )

    def object_to_orm(self, plan: entities.Plan) -> Plan:
        return Plan.query.get(str(plan.id))

    def get_plan_by_id(self, id: UUID) -> Optional[entities.Plan]:
        plan_orm = Plan.query.filter_by(id=str(id)).first()
        if plan_orm is None:
            return None
        else:
            return self.object_from_orm(plan_orm)

    def _create_plan_from_draft(
        self,
        plan: entities.PlanDraft,
    ) -> Plan:
        costs = plan.production_costs
        plan = Plan(
            id=plan.id,
            plan_creation_date=plan.creation_date,
            planner=self.company_repository.object_to_orm(plan.planner).id,
            costs_p=costs.means_cost,
            costs_r=costs.resource_cost,
            costs_a=costs.labour_cost,
            prd_name=plan.product_name,
            prd_unit=plan.unit_of_distribution,
            prd_amount=plan.amount_produced,
            description=plan.description,
            timeframe=plan.timeframe,
            is_public_service=plan.is_public_service,
            is_active=False,
            activation_date=None,
            expiration_date=None,
            active_days=None,
            payout_count=0,
            is_available=True,
        )
        self.db.session.add(plan)
        return plan

    def set_plan_approval_date(
        self, draft: entities.PlanDraft, approval_timestamp: datetime
    ) -> entities.Plan:
        plan_orm = self._create_plan_from_draft(draft)
        plan_orm.approval_reason = "approved"
        plan_orm.approval_date = approval_timestamp
        return self.object_from_orm(plan_orm)

    def activate_plan(self, plan: entities.Plan, activation_date: datetime) -> None:
        plan.is_active = True
        plan.activation_date = activation_date

        plan_orm = self.object_to_orm(plan)
        plan_orm.is_active = True
        plan_orm.activation_date = activation_date

    def set_plan_as_expired(self, plan: entities.Plan) -> None:
        plan.expired = True
        plan.is_active = False

        plan_orm = self.object_to_orm(plan)
        plan_orm.expired = True
        plan_orm.is_active = False

    def set_expiration_date(
        self, plan: entities.Plan, expiration_date: datetime
    ) -> None:
        plan.expiration_date = expiration_date

        plan_orm = self.object_to_orm(plan)
        plan_orm.expiration_date = expiration_date

    def set_active_days(self, plan: entities.Plan, full_active_days: int) -> None:
        plan.active_days = full_active_days

        plan_orm = self.object_to_orm(plan)
        plan_orm.active_days = full_active_days

    def increase_payout_count_by_one(self, plan: entities.Plan) -> None:
        plan.payout_count += 1

        plan_orm = self.object_to_orm(plan)
        plan_orm.payout_count += 1

    def get_active_plans(self) -> Iterator[entities.Plan]:
        return (
            self.object_from_orm(plan_orm)
            for plan_orm in Plan.query.filter_by(is_active=True).all()
        )

    def get_three_latest_active_plans_ordered_by_activation_date(
        self,
    ) -> Iterator[entities.Plan]:
        return (
            self.object_from_orm(plan_orm)
            for plan_orm in Plan.query.filter_by(is_active=True)
            .order_by(Plan.activation_date.desc())
            .limit(3)
        )

    def count_active_plans(self) -> int:
        return int(
            self.db.session.query(func.count(Plan.id))
            .filter_by(is_active=True)
            .one()[0]
        )

    def count_active_public_plans(self) -> int:
        return int(
            self.db.session.query(func.count(Plan.id))
            .filter_by(is_active=True, is_public_service=True)
            .one()[0]
        )

    def avg_timeframe_of_active_plans(self) -> Decimal:
        return Decimal(
            self.db.session.query(func.avg(Plan.timeframe))
            .filter_by(is_active=True)
            .one()[0]
            or 0
        )

    def sum_of_active_planned_work(self) -> Decimal:
        return Decimal(
            self.db.session.query(func.sum(Plan.costs_a))
            .filter_by(is_active=True)
            .one()[0]
            or 0
        )

    def sum_of_active_planned_resources(self) -> Decimal:
        return Decimal(
            self.db.session.query(func.sum(Plan.costs_r))
            .filter_by(is_active=True)
            .one()[0]
            or 0
        )

    def sum_of_active_planned_means(self) -> Decimal:
        return Decimal(
            self.db.session.query(func.sum(Plan.costs_p))
            .filter_by(is_active=True)
            .one()[0]
            or 0
        )

    def all_plans_approved_and_not_expired(self) -> Iterator[entities.Plan]:
        return (
            self.object_from_orm(plan_orm)
            for plan_orm in Plan.query.filter_by(approved=True, expired=False).all()
        )

    def all_productive_plans_approved_active_and_not_expired(
        self,
    ) -> Iterator[entities.Plan]:
        return (
            self.object_from_orm(plan_orm)
            for plan_orm in Plan.query.filter_by(
                is_active=True, expired=False, is_public_service=False
            ).filter(Plan.approval_date != None)
        )

    def all_public_plans_approved_active_and_not_expired(
        self,
    ) -> Iterator[entities.Plan]:
        return (
            self.object_from_orm(plan_orm)
            for plan_orm in Plan.query.filter_by(
                is_active=True,
                expired=False,
                is_public_service=True,
            ).filter(Plan.approval_date != None)
        )

    def all_plans_approved_active_and_not_expired(self) -> Iterator[entities.Plan]:
        return (
            self.object_from_orm(plan_orm)
            for plan_orm in Plan.query.filter_by(
                is_active=True,
                expired=False,
            ).filter(Plan.approval_date != None)
        )

    def hide_plan(self, plan_id: UUID) -> None:
        plan_orm = Plan.query.filter_by(id=str(plan_id)).first()
        assert plan_orm
        plan_orm.hidden_by_user = True

    def query_active_plans_by_product_name(self, query: str) -> Iterator[entities.Plan]:
        return (
            self.object_from_orm(plan)
            for plan in Plan.query.filter(
                Plan.is_active == True, Plan.prd_name.ilike(f"%{query}%")
            ).all()
        )

    def query_active_plans_by_plan_id(self, query: str) -> Iterator[entities.Plan]:
        return (
            self.object_from_orm(plan)
            for plan in Plan.query.filter(
                Plan.is_active == True, Plan.id.contains(query)
            ).all()
        )

    def get_all_plans_for_company_descending(
        self, company_id: UUID
    ) -> Iterator[entities.Plan]:
        return (
            self.object_from_orm(plan_orm)
            for plan_orm in Plan.query.filter(Plan.planner == str(company_id)).order_by(
                Plan.plan_creation_date.desc()
            )
        )

    def get_all_active_plans_for_company(
        self, company_id: UUID
    ) -> Iterator[entities.Plan]:
        return (
            self.object_from_orm(plan_orm)
            for plan_orm in Plan.query.filter(
                Plan.planner == str(company_id), Plan.is_active == True
            )
        )

    def toggle_product_availability(self, plan: entities.Plan) -> None:
        plan.is_available = True if (plan.is_available == False) else False

        plan_orm = self.object_to_orm(plan)
        plan_orm.is_available = True if (plan_orm.is_available == False) else False

    def get_plan_name_and_description(
        self, id: UUID
    ) -> repositories.PlanRepository.NameAndDescription:
        plan = Plan.query.get(str(id))
        name_and_description = repositories.PlanRepository.NameAndDescription(
            name=plan.prd_name, description=plan.description
        )
        return name_and_description

    def __len__(self) -> int:
        return len(Plan.query.all())


@inject
@dataclass
class TransactionRepository(repositories.TransactionRepository):
    account_repository: AccountRepository
    db: SQLAlchemy

    def object_to_orm(self, transaction: entities.Transaction) -> Transaction:
        return Transaction.query.get(str(transaction.id))

    def object_from_orm(self, transaction: Transaction) -> entities.Transaction:
        return entities.Transaction(
            id=UUID(transaction.id),
            date=transaction.date,
            sending_account=self.account_repository.get_by_id(
                transaction.sending_account
            ),
            receiving_account=self.account_repository.get_by_id(
                transaction.receiving_account
            ),
            amount_sent=Decimal(transaction.amount_sent),
            amount_received=Decimal(transaction.amount_received),
            purpose=transaction.purpose,
        )

    def create_transaction(
        self,
        date: datetime,
        sending_account: entities.Account,
        receiving_account: entities.Account,
        amount_sent: Decimal,
        amount_received: Decimal,
        purpose: str,
    ) -> entities.Transaction:
        transaction = Transaction(
            id=str(uuid4()),
            date=date,
            sending_account=str(sending_account.id),
            receiving_account=str(receiving_account.id),
            amount_sent=amount_sent,
            amount_received=amount_received,
            purpose=purpose,
        )
        self.db.session.add(transaction)
        return self.object_from_orm(transaction)

    def all_transactions_sent_by_account(
        self, account: entities.Account
    ) -> List[entities.Transaction]:
        account_orm = self.account_repository.object_to_orm(account)
        return [
            self.object_from_orm(transaction)
            for transaction in account_orm.transactions_sent.all()
        ]

    def all_transactions_received_by_account(
        self, account: entities.Account
    ) -> List[entities.Transaction]:
        account_orm = self.account_repository.object_to_orm(account)
        return [
            self.object_from_orm(transaction)
            for transaction in account_orm.transactions_received.all()
        ]

    def get_sales_balance_of_plan(self, plan: entities.Plan) -> Decimal:
        return Decimal(
            self.db.session.query(func.sum(Transaction.amount_received))
            .filter(
                Transaction.receiving_account == str(plan.planner.product_account.id),
                Transaction.purpose.contains(f"{plan.id}"),
            )
            .one()[0]
            or 0
        )


@inject
@dataclass
class PlanDraftRepository(repositories.PlanDraftRepository):
    db: SQLAlchemy
    company_repository: CompanyRepository

    def create_plan_draft(
        self,
        planner: UUID,
        product_name: str,
        description: str,
        costs: entities.ProductionCosts,
        production_unit: str,
        amount: int,
        timeframe_in_days: int,
        is_public_service: bool,
        creation_timestamp: datetime,
    ) -> entities.PlanDraft:
        orm = PlanDraft(
            id=str(uuid4()),
            plan_creation_date=creation_timestamp,
            planner=str(planner),
            costs_p=costs.means_cost,
            costs_r=costs.resource_cost,
            costs_a=costs.labour_cost,
            prd_name=product_name,
            prd_unit=production_unit,
            prd_amount=amount,
            description=description,
            timeframe=timeframe_in_days,
            is_public_service=is_public_service,
        )
        self.db.session.add(orm)
        return self._object_from_orm(orm)

    def get_by_id(self, id: UUID) -> Optional[entities.PlanDraft]:
        orm = PlanDraft.query.get(str(id))
        if orm is None:
            return None
        else:
            return self._object_from_orm(orm)

    def delete_draft(self, id: UUID) -> None:
        PlanDraft.query.filter_by(id=str(id)).delete()

    def _object_from_orm(self, orm: PlanDraft) -> entities.PlanDraft:
        planner = self.company_repository.get_by_id(orm.planner)
        assert planner is not None
        return entities.PlanDraft(
            id=orm.id,
            creation_date=orm.plan_creation_date,
            planner=planner,
            production_costs=entities.ProductionCosts(
                labour_cost=orm.costs_a,
                resource_cost=orm.costs_r,
                means_cost=orm.costs_p,
            ),
            product_name=orm.prd_name,
            unit_of_distribution=orm.prd_unit,
            amount_produced=orm.prd_amount,
            description=orm.description,
            timeframe=orm.timeframe,
            is_public_service=orm.is_public_service,
        )

    def all_drafts_of_company(self, id: UUID) -> Iterable[entities.PlanDraft]:
        draft_owner = Company.query.filter_by(id=str(id)).first()
        assert draft_owner is not None
        drafts = draft_owner.drafts.all()
        return (self._object_from_orm(draft) for draft in drafts)


@inject
@dataclass
class WorkerInviteRepository(repositories.WorkerInviteRepository):
    db: SQLAlchemy
    company_repository: CompanyRepository
    member_repository: MemberRepository

    def is_worker_invited_to_company(self, company: UUID, worker: UUID) -> bool:
        return (
            CompanyWorkInvite.query.filter_by(
                company=str(company),
                member=str(worker),
            ).count()
            > 0
        )

    def create_company_worker_invite(self, company: UUID, worker: UUID) -> UUID:
        invite = CompanyWorkInvite(
            id=str(uuid4()),
            company=str(company),
            member=str(worker),
        )
        self.db.session.add(invite)
        return invite.id

    def get_companies_worker_is_invited_to(self, member: UUID) -> Iterable[UUID]:
        for invite in CompanyWorkInvite.query.filter_by(member=str(member)):
            yield UUID(invite.company)

    def get_invites_for_worker(
        self, member: UUID
    ) -> Iterable[entities.CompanyWorkInvite]:
        for invite in CompanyWorkInvite.query.filter_by(member=str(member)):
            invite_object = self.get_by_id(invite.id)
            if invite_object is None:
                continue
            yield invite_object

    def get_by_id(self, id: UUID) -> Optional[entities.CompanyWorkInvite]:
        if (
            invite_orm := CompanyWorkInvite.query.filter_by(id=str(id)).first()
        ) is not None:
            company = self.company_repository.get_by_id(UUID(invite_orm.company))
            if company is None:
                return None
            member = self.member_repository.get_by_id(UUID(invite_orm.member))
            if member is None:
                return None
            return entities.CompanyWorkInvite(
                id=id,
                company=company,
                member=member,
            )
        return None

    def delete_invite(self, id: UUID) -> None:
        CompanyWorkInvite.query.filter_by(id=str(id)).delete()


@inject
@dataclass
class CooperationRepository(repositories.CooperationRepository):
    db: SQLAlchemy
    company_repository: CompanyRepository

    def create_cooperation(
        self,
        creation_timestamp: datetime,
        name: str,
        definition: str,
        coordinator: entities.Company,
    ) -> entities.Cooperation:
        cooperation = Cooperation(
            id=str(uuid4()),
            creation_date=creation_timestamp,
            name=name,
            definition=definition,
            coordinator=str(coordinator.id),
        )
        self.db.session.add(cooperation)
        return self.object_from_orm(cooperation)

    def object_from_orm(self, cooperation_orm: Cooperation) -> entities.Cooperation:
        coordinator = self.company_repository.get_by_id(cooperation_orm.coordinator)
        assert coordinator is not None
        return entities.Cooperation(
            id=UUID(cooperation_orm.id),
            creation_date=cooperation_orm.creation_date,
            name=cooperation_orm.name,
            definition=cooperation_orm.definition,
            coordinator=coordinator,
        )

    def get_by_id(self, id: UUID) -> Optional[entities.Cooperation]:
        cooperation_orm = Cooperation.query.filter_by(id=str(id)).first()
        if cooperation_orm is None:
            return None
        return self.object_from_orm(cooperation_orm)

    def get_by_name(self, name: str) -> Iterator[entities.Cooperation]:
        return (
            self.object_from_orm(cooperation)
            for cooperation in Cooperation.query.filter(
                Cooperation.name.ilike(name)
            ).all()
        )

    def get_cooperations_coordinated_by_company(
        self, company_id: UUID
    ) -> Iterator[entities.Cooperation]:
        return (
            self.object_from_orm(cooperation)
            for cooperation in Cooperation.query.filter_by(
                coordinator=str(company_id)
            ).all()
        )

    def get_cooperation_name(self, coop_id: UUID) -> Optional[str]:
        coop_orm = Cooperation.query.filter_by(id=str(coop_id)).first()
        if coop_orm is None:
            return None
        return coop_orm.name

    def get_all_cooperations(self) -> Iterator[entities.Cooperation]:
        return (
            self.object_from_orm(cooperation) for cooperation in Cooperation.query.all()
        )

    def count_cooperations(self) -> int:
        return int(self.db.session.query(func.count(Cooperation.id)).one()[0])


@inject
@dataclass
class PlanCooperationRepository(repositories.PlanCooperationRepository):
    plan_repository: PlanRepository
    cooperation_repository: CooperationRepository

    def get_inbound_requests(self, coordinator_id: UUID) -> Iterator[entities.Plan]:
        for plan in self.plan_repository.get_active_plans():
            if plan.requested_cooperation:
                if plan.requested_cooperation in [
                    coop.id
                    for coop in self.cooperation_repository.get_cooperations_coordinated_by_company(
                        coordinator_id
                    )
                ]:
                    yield plan

    def get_outbound_requests(self, requester_id: UUID) -> Iterator[entities.Plan]:
        plans_of_company = self.plan_repository.get_all_plans_for_company_descending(
            requester_id
        )
        for plan in plans_of_company:
            if plan.requested_cooperation:
                yield plan

    def get_cooperating_plans(self, plan_id: UUID) -> List[entities.Plan]:
        plan_orm = Plan.query.filter_by(id=str(plan_id)).first()
        if plan_orm is None:
            return []
        coop_orm = plan_orm.coop
        if coop_orm is None:
            plan = self.plan_repository.get_plan_by_id(plan_id)
            if plan is None:
                return []
            return [plan]

        else:
            return [
                self.plan_repository.object_from_orm(plan)
                for plan in coop_orm.plans.all()
            ]

    def add_plan_to_cooperation(self, plan_id: UUID, cooperation_id: UUID) -> None:
        plan_orm = Plan.query.filter_by(id=str(plan_id)).first()
        assert plan_orm
        plan_orm.cooperation = str(cooperation_id)

    def remove_plan_from_cooperation(self, plan_id: UUID) -> None:
        plan_orm = Plan.query.filter_by(id=str(plan_id)).first()
        assert plan_orm
        plan_orm.cooperation = None

    def set_requested_cooperation(self, plan_id: UUID, cooperation_id: UUID) -> None:
        plan_orm = Plan.query.filter_by(id=str(plan_id)).first()
        assert plan_orm
        plan_orm.requested_cooperation = str(cooperation_id)

    def set_requested_cooperation_to_none(self, plan_id: UUID) -> None:
        plan_orm = Plan.query.filter_by(id=str(plan_id)).first()
        assert plan_orm
        plan_orm.requested_cooperation = None

    def count_plans_in_cooperation(self, cooperation_id: UUID) -> int:
        count = Plan.query.filter_by(cooperation=str(cooperation_id)).count()
        return count

    def get_plans_in_cooperation(self, cooperation_id: UUID) -> Iterable[entities.Plan]:
        plans = Plan.query.filter_by(cooperation=str(cooperation_id)).all()
        for plan in plans:
            yield self.plan_repository.object_from_orm(plan)


@inject
@dataclass
class AccountantRepository:
    db: SQLAlchemy

    def create_accountant(self, email: str, name: str, password: str) -> UUID:
        user_id = uuid4()
        user_orm = self._get_or_create_user(email, password)
        accountant = models.Accountant(
            id=str(user_id),
            name=name,
            user=user_orm,
        )
        self.db.session.add(accountant)
        return user_id

    def get_by_id(self, id: UUID) -> Optional[entities.Accountant]:
        record = models.Accountant.query.filter_by(id=str(id)).first()
        if record is None:
            return None
        return entities.Accountant(email_address=record.user.email, name=record.name)

    def validate_credentials(self, email: str, password: str) -> Optional[UUID]:
        record = (
            self.db.session.query(models.Accountant)
            .join(models.User)
            .filter(models.User.email == email)
            .first()
        )
        if record is None:
            return None
        if not check_password_hash(record.user.password, password):
            return None
        return UUID(record.id)

    def has_accountant_with_email(self, email: str) -> bool:
        return bool(
            self.db.session.query(models.Accountant)
            .join(models.User)
            .filter(models.User.email == email)
            .first()
        )

    def get_accountant_orm_by_mail(self, email: str) -> Optional[models.Accountant]:
        return (
            self.db.session.query(models.Accountant)
            .join(models.User)
            .filter(models.User.email == email)
            .first()
        )

    def _get_or_create_user(self, email: str, password: str) -> models.User:
        return self.db.session.query(models.User).filter(
            and_(models.User.email == email, models.User.accountant == None)
        ).first() or models.User(
            password=generate_password_hash(password, method="sha256"),
            email=email,
        )
