from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import (
    Any,
    Callable,
    Generic,
    Iterable,
    Iterator,
    List,
    Optional,
    TypeVar,
    Union,
)
from uuid import UUID, uuid4

from flask_sqlalchemy import SQLAlchemy
from injector import inject
from sqlalchemy import and_, func, or_, update
from sqlalchemy.sql.expression import Select
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
    PlanDraft,
    Purchase,
    SocialAccounting,
    Transaction,
)

T = TypeVar("T", covariant=True)
FlaskQueryResultT = TypeVar("FlaskQueryResultT", bound="FlaskQueryResult")


class FlaskQueryResult(Generic[T]):
    def __init__(
        self, query: Select, mapper: Callable[[Any], T], db: SQLAlchemy
    ) -> None:
        self.query = query
        self.mapper = mapper
        self.db = db

    def limit(self: FlaskQueryResultT, n: int) -> FlaskQueryResultT:
        return type(self)(query=self.query.limit(n), mapper=self.mapper, db=self.db)

    def offset(self: FlaskQueryResultT, n: int) -> FlaskQueryResultT:
        return type(self)(query=self.query.offset(n), mapper=self.mapper, db=self.db)

    def first(self) -> Optional[T]:
        element = self.query.first()
        if element is None:
            return None
        return self.mapper(element)

    def _with_modified_query(
        self: FlaskQueryResultT, modification: Callable[[Any], Any]
    ) -> FlaskQueryResultT:
        return type(self)(
            query=modification(self.query), mapper=self.mapper, db=self.db
        )

    def __iter__(self) -> Iterator[T]:
        return (self.mapper(item) for item in self.query)

    def __len__(self) -> int:
        return self.query.count()


class PlanQueryResult(FlaskQueryResult[entities.Plan]):
    def ordered_by_creation_date(self, ascending: bool = True) -> PlanQueryResult:
        ordering = models.Plan.plan_creation_date
        if not ascending:
            ordering = ordering.desc()
        return self._with_modified_query(lambda query: query.order_by(ordering))

    def with_id_containing(self, query: str) -> PlanQueryResult:
        return self._with_modified_query(
            lambda db_query: db_query.filter(models.Plan.id.contains(query))
        )

    def with_product_name_containing(self, query: str) -> PlanQueryResult:
        return self._with_modified_query(
            lambda db_query: db_query.filter(models.Plan.prd_name.ilike(f"%{query}%"))
        )

    def that_are_approved(self) -> PlanQueryResult:
        return self._with_modified_query(
            lambda query: self.query.join(models.PlanReview).filter(
                models.PlanReview.approval_date != None
            )
        )

    def that_are_productive(self) -> PlanQueryResult:
        return self._with_modified_query(
            lambda query: query.filter(models.Plan.is_public_service == False)
        )

    def that_are_public(self) -> PlanQueryResult:
        return self._with_modified_query(
            lambda query: query.filter(models.Plan.is_public_service == True)
        )

    def that_are_cooperating(self) -> PlanQueryResult:
        return self._with_modified_query(
            lambda query: query.filter(models.Plan.cooperation != None)
        )

    def planned_by(self, company: UUID) -> PlanQueryResult:
        return self._with_modified_query(
            lambda query: query.filter(models.Plan.planner == str(company))
        )

    def with_id(self, id_: UUID) -> PlanQueryResult:
        return self._with_modified_query(
            lambda query: query.filter(models.Plan.id == str(id_))
        )

    def without_completed_review(self) -> PlanQueryResult:
        return self._with_modified_query(
            lambda query: self.query.join(models.PlanReview).filter(
                models.PlanReview.approval_date == None
            )
        )

    def with_open_cooperation_request(
        self, *, cooperation: Optional[UUID] = None
    ) -> PlanQueryResult:
        return self._with_modified_query(
            lambda query: query.filter(
                models.Plan.requested_cooperation == str(cooperation)
                if cooperation
                else models.Plan.requested_cooperation != None
            )
        )

    def that_are_in_same_cooperation_as(self, plan: UUID) -> PlanQueryResult:
        return self._with_modified_query(
            lambda query: query.filter(
                or_(
                    models.Plan.id == str(plan),
                    and_(
                        models.Plan.cooperation != None,
                        models.Plan.cooperation.in_(
                            models.Plan.query.filter(
                                models.Plan.id == str(plan)
                            ).with_entities(models.Plan.cooperation)
                        ),
                    ),
                )
            )
        )

    def that_are_active(self) -> PlanQueryResult:
        return self._with_modified_query(
            lambda query: query.filter(models.Plan.is_active == True)
        )

    def that_are_part_of_cooperation(self, cooperation: UUID) -> PlanQueryResult:
        return self._with_modified_query(
            lambda query: query.filter_by(cooperation=str(cooperation))
        )


class MemberQueryResult(FlaskQueryResult[entities.Member]):
    def working_at_company(self, company: UUID) -> MemberQueryResult:
        return self._with_modified_query(
            lambda query: query.filter(models.Member.workplaces.any(id=str(company)))
        )

    def with_id(self, member: UUID) -> MemberQueryResult:
        return self._with_modified_query(
            lambda query: query.filter(models.Member.id == str(member))
        )

    def with_email_address(self, email: str) -> MemberQueryResult:
        return self._with_modified_query(
            lambda query: query.join(models.User).filter(models.User.email == email)
        )

    def set_confirmation_timestamp(self, timestamp: datetime) -> int:
        sql_statement = (
            update(models.Member)
            .where(
                models.Member.id.in_(
                    self.query.with_entities(models.Member.id).scalar_subquery()
                )
            )
            .values(confirmed_on=timestamp)
            .execution_options(synchronize_session="fetch")
        )
        result = self.db.session.execute(sql_statement)
        return result.rowcount

    def that_are_confirmed(self) -> MemberQueryResult:
        return self._with_modified_query(
            lambda query: query.filter(models.Member.confirmed_on != None)
        )


class PurchaseQueryResult(FlaskQueryResult[entities.Purchase]):
    def ordered_by_creation_date(
        self, *, ascending: bool = True
    ) -> PurchaseQueryResult:
        ordering = models.Purchase.purchase_date
        if not ascending:
            ordering = ordering.desc()
        return self._with_modified_query(lambda query: query.order_by(ordering))

    def where_buyer_is_company(
        self, *, company: Optional[UUID] = None
    ) -> PurchaseQueryResult:
        return self._with_modified_query(
            lambda query: self.query.filter(models.Purchase.company == str(company))
            if company
            else self.query.filter(models.Purchase.company != None)
        )

    def where_buyer_is_member(
        self, *, member: Optional[UUID] = None
    ) -> PurchaseQueryResult:
        return self._with_modified_query(
            lambda query: self.query.filter(models.Purchase.member == str(member))
            if member
            else self.query.filter(models.Purchase.member != None)
        )


class CompanyQueryResult(FlaskQueryResult[entities.Company]):
    def with_id(self, id_: UUID) -> CompanyQueryResult:
        return self._with_modified_query(
            lambda query: query.filter(models.Company.id == str(id_))
        )

    def with_email_address(self, email: str) -> CompanyQueryResult:
        return self._with_modified_query(
            lambda query: query.join(models.User).filter(models.User.email == email)
        )

    def that_are_workplace_of_member(self, member: UUID) -> CompanyQueryResult:
        return self._with_modified_query(
            lambda query: query.filter(
                models.Company.workers.any(models.Member.id == str(member))
            )
        )


@inject
@dataclass
class CompanyWorkerRepository:
    member_repository: MemberRepository
    company_repository: CompanyRepository

    def add_worker_to_company(self, company: UUID, worker: UUID) -> None:
        member = models.Member.query.get(str(worker))
        if member is None:
            return
        company = models.Company.query.get(str(company))
        if company is None:
            return
        member.workplaces.append(company)


@dataclass
class UserAddressBookImpl:
    db: SQLAlchemy

    def get_user_email_address(self, user: UUID) -> Optional[str]:
        user_orm = (
            self.db.session.query(models.User)
            .join(models.Member, isouter=True)
            .join(models.Company, isouter=True)
            .join(models.Accountant, isouter=True)
            .filter(
                (models.Member.id == str(user))
                | (models.Company.id == str(user))
                | (models.Accountant.id == str(user))
            )
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
        *,
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

    def get_members(self) -> MemberQueryResult:
        return MemberQueryResult(
            mapper=self.object_from_orm,
            query=Member.query,
            db=self.db,
        )

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

    def get_companies(self) -> CompanyQueryResult:
        return CompanyQueryResult(
            query=Company.query,
            mapper=self.object_from_orm,
            db=self.db,
        )

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

    def confirm_company(self, company: UUID, confirmed_on: datetime) -> None:
        self.db.session.query(models.Company).filter(
            models.Company.id == str(company)
        ).update({models.Company.confirmed_on: confirmed_on})

    def is_company_confirmed(self, company: UUID) -> bool:
        orm = (
            self.db.session.query(models.Company)
            .filter(models.Company.id == str(company))
            .first()
        )
        if orm is None:
            return False
        else:
            return orm.confirmed_on is not None

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

    def get_purchases(self) -> PurchaseQueryResult:
        return PurchaseQueryResult(
            mapper=self.object_from_orm,
            query=models.Purchase.query,
            db=self.db,
        )


@inject
@dataclass
class PlanRepository(repositories.PlanRepository):
    company_repository: CompanyRepository
    db: SQLAlchemy
    draft_repository: PlanDraftRepository

    def get_plans(self) -> PlanQueryResult:
        return PlanQueryResult(
            query=models.Plan.query,
            mapper=self.object_from_orm,
            db=self.db,
        )

    def create_plan_from_draft(self, draft_id: UUID) -> Optional[UUID]:
        draft = self.draft_repository.get_by_id(draft_id)
        if draft is None:
            return None
        plan_orm = self._create_plan_from_draft(draft)
        return UUID(plan_orm.id)

    def object_from_orm(self, plan: models.Plan) -> entities.Plan:
        production_costs = entities.ProductionCosts(
            labour_cost=plan.costs_a,
            resource_cost=plan.costs_r,
            means_cost=plan.costs_p,
        )
        return entities.Plan(
            id=UUID(plan.id),
            plan_creation_date=plan.plan_creation_date,
            planner=UUID(plan.planner),
            production_costs=production_costs,
            prd_name=plan.prd_name,
            prd_unit=plan.prd_unit,
            prd_amount=plan.prd_amount,
            description=plan.description,
            timeframe=int(plan.timeframe),
            is_public_service=plan.is_public_service,
            approval_date=plan.review.approval_date,
            approval_reason=plan.review.approval_reason,
            is_active=plan.is_active,
            expired=plan.expired,
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

    def object_to_orm(self, plan: entities.Plan) -> models.Plan:
        return models.Plan.query.get(str(plan.id))

    def _create_plan_from_draft(
        self,
        plan: entities.PlanDraft,
    ) -> models.Plan:
        costs = plan.production_costs
        plan = models.Plan(
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
            active_days=None,
            payout_count=0,
            is_available=True,
        )
        self.db.session.add(plan)
        plan_review = models.PlanReview(
            approval_date=None, approval_reason=None, plan=plan
        )
        self.db.session.add(plan_review)
        return plan

    def set_plan_approval_date(self, plan: UUID, approval_timestamp: datetime):
        models.PlanReview.query.filter(models.PlanReview.plan_id == str(plan)).update(
            dict(
                approval_reason="approved",
                approval_date=approval_timestamp,
            )
        )

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

    def set_active_days(self, plan: entities.Plan, full_active_days: int) -> None:
        plan.active_days = full_active_days

        plan_orm = self.object_to_orm(plan)
        plan_orm.active_days = full_active_days

    def increase_payout_count_by_one(self, plan: entities.Plan) -> None:
        plan.payout_count += 1

        plan_orm = self.object_to_orm(plan)
        plan_orm.payout_count += 1

    def avg_timeframe_of_active_plans(self) -> Decimal:
        return Decimal(
            self.db.session.query(func.avg(models.Plan.timeframe))
            .filter_by(is_active=True)
            .one()[0]
            or 0
        )

    def sum_of_active_planned_work(self) -> Decimal:
        return Decimal(
            self.db.session.query(func.sum(models.Plan.costs_a))
            .filter_by(is_active=True)
            .one()[0]
            or 0
        )

    def sum_of_active_planned_resources(self) -> Decimal:
        return Decimal(
            self.db.session.query(func.sum(models.Plan.costs_r))
            .filter_by(is_active=True)
            .one()[0]
            or 0
        )

    def sum_of_active_planned_means(self) -> Decimal:
        return Decimal(
            self.db.session.query(func.sum(models.Plan.costs_p))
            .filter_by(is_active=True)
            .one()[0]
            or 0
        )

    def all_plans_approved_and_not_expired(self) -> Iterator[entities.Plan]:
        return (
            self.object_from_orm(plan_orm)
            for plan_orm in models.Plan.query.filter_by(
                approved=True, expired=False
            ).all()
        )

    def hide_plan(self, plan_id: UUID) -> None:
        plan_orm = models.Plan.query.filter_by(id=str(plan_id)).first()
        assert plan_orm
        plan_orm.hidden_by_user = True

    def toggle_product_availability(self, plan: entities.Plan) -> None:
        plan.is_available = True if (plan.is_available == False) else False

        plan_orm = self.object_to_orm(plan)
        plan_orm.is_available = True if (plan_orm.is_available == False) else False

    def get_plan_name_and_description(
        self, id: UUID
    ) -> repositories.PlanRepository.NameAndDescription:
        plan = models.Plan.query.get(str(id))
        name_and_description = repositories.PlanRepository.NameAndDescription(
            name=plan.prd_name, description=plan.description
        )
        return name_and_description

    def get_planner_id(self, plan_id: UUID) -> Optional[UUID]:
        plan = models.Plan.query.get(str(plan_id))
        return UUID(plan.planner) if plan else None

    def __len__(self) -> int:
        return len(models.Plan.query.all())


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
            models.Transaction.query.join(
                models.Account,
                models.Transaction.receiving_account == models.Account.id,
            )
            .filter(models.Account.account_owner_company == str(plan.planner))
            .with_entities(func.sum(models.Transaction.amount_received))
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

    def update_draft(
        self, update: repositories.PlanDraftRepository.UpdateDraft
    ) -> None:
        class UpdateInstructions(dict):
            def update_attribute(self, key, value):
                if value is not None:
                    self[key] = value

        update_instructions = UpdateInstructions()
        update_instructions.update_attribute(
            models.PlanDraft.prd_name, update.product_name
        )
        update_instructions.update_attribute(
            models.PlanDraft.description, update.description
        )
        update_instructions.update_attribute(
            models.PlanDraft.prd_unit, update.unit_of_distribution
        )
        update_instructions.update_attribute(
            models.PlanDraft.costs_p, update.means_cost
        )
        update_instructions.update_attribute(
            models.PlanDraft.costs_a,
            update.labour_cost,
        )
        update_instructions.update_attribute(
            models.PlanDraft.costs_r, update.resource_cost
        )
        update_instructions.update_attribute(
            models.PlanDraft.is_public_service, update.is_public_service
        )
        update_instructions.update_attribute(
            models.PlanDraft.timeframe, update.timeframe
        )
        update_instructions.update_attribute(models.PlanDraft.prd_amount, update.amount)
        if update_instructions:
            self.db.session.query(models.PlanDraft).filter(
                models.PlanDraft.id == str(update.id)
            ).update(update_instructions)

    def get_by_id(self, id: UUID) -> Optional[entities.PlanDraft]:
        orm = PlanDraft.query.get(str(id))
        if orm is None:
            return None
        else:
            return self._object_from_orm(orm)

    def delete_draft(self, id: UUID) -> None:
        PlanDraft.query.filter_by(id=str(id)).delete()

    def _object_from_orm(self, orm: PlanDraft) -> entities.PlanDraft:
        planner = self.company_repository.get_companies().with_id(orm.planner).first()
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
            company = (
                self.company_repository.get_companies()
                .with_id(UUID(invite_orm.company))
                .first()
            )
            if company is None:
                return None
            member = (
                self.member_repository.get_members()
                .with_id(UUID(invite_orm.member))
                .first()
            )
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
        coordinator = (
            self.company_repository.get_companies()
            .with_id(cooperation_orm.coordinator)
            .first()
        )
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
        for plan in self.plan_repository.get_plans().that_are_active():
            if plan.requested_cooperation:
                if plan.requested_cooperation in [
                    coop.id
                    for coop in self.cooperation_repository.get_cooperations_coordinated_by_company(
                        coordinator_id
                    )
                ]:
                    yield plan

    def add_plan_to_cooperation(self, plan_id: UUID, cooperation_id: UUID) -> None:
        plan_orm = models.Plan.query.filter_by(id=str(plan_id)).first()
        assert plan_orm
        plan_orm.cooperation = str(cooperation_id)

    def remove_plan_from_cooperation(self, plan_id: UUID) -> None:
        plan_orm = models.Plan.query.filter_by(id=str(plan_id)).first()
        assert plan_orm
        plan_orm.cooperation = None

    def set_requested_cooperation(self, plan_id: UUID, cooperation_id: UUID) -> None:
        plan_orm = models.Plan.query.filter_by(id=str(plan_id)).first()
        assert plan_orm
        plan_orm.requested_cooperation = str(cooperation_id)

    def set_requested_cooperation_to_none(self, plan_id: UUID) -> None:
        plan_orm = models.Plan.query.filter_by(id=str(plan_id)).first()
        assert plan_orm
        plan_orm.requested_cooperation = None


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
        return entities.Accountant(
            email_address=record.user.email, name=record.name, id=UUID(record.id)
        )

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

    def get_all_accountants(self) -> FlaskQueryResult[entities.Accountant]:
        return FlaskQueryResult(
            query=models.Accountant.query.all(),
            mapper=lambda record: entities.Accountant(
                email_address=record.user.email,
                name=record.name,
                id=UUID(record.id),
            ),
            db=self.db,
        )


@inject
@dataclass
class PayoutFactorRepository:
    db: SQLAlchemy

    def store_payout_factor(self, timestamp: datetime, payout_factor: Decimal) -> None:
        payout_factor = models.PayoutFactor(
            timestamp=timestamp, payout_factor=payout_factor
        )
        self.db.session.add(payout_factor)

    def get_latest_payout_factor(
        self,
    ) -> Optional[entities.PayoutFactor]:
        payout_factor_orm = (
            self.db.session.query(models.PayoutFactor)
            .order_by(models.PayoutFactor.timestamp.desc())
            .first()
        )
        if not payout_factor_orm:
            return None
        return entities.PayoutFactor(
            calculation_date=payout_factor_orm.timestamp,
            value=Decimal(payout_factor_orm.payout_factor),
        )
