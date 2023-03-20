from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime
from decimal import Decimal
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Iterable,
    Iterator,
    Optional,
    Tuple,
    TypeVar,
    Union,
)
from uuid import UUID, uuid4

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, and_, case, cast, func, or_, update
from sqlalchemy.dialects.postgresql import INTERVAL
from sqlalchemy.orm import aliased
from sqlalchemy.sql.functions import concat
from typing_extensions import Self
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
    SocialAccounting,
    Transaction,
)

T = TypeVar("T", covariant=True)
FlaskQueryResultT = TypeVar("FlaskQueryResultT", bound="FlaskQueryResult")


class FlaskQueryResult(Generic[T]):
    def __init__(self, query: Any, mapper: Callable[[Any], T], db: SQLAlchemy) -> None:
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

    def _with_modified_query(self, modification: Callable[[Any], Any]) -> Self:
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

    def ordered_by_activation_date(self, ascending: bool = True) -> PlanQueryResult:
        ordering = models.Plan.activation_date
        if not ascending:
            ordering = ordering.desc()
        return self._with_modified_query(lambda query: query.order_by(ordering))

    def ordered_by_planner_name(self, ascending: bool = True) -> PlanQueryResult:
        ordering = models.Company.name
        if not ascending:
            ordering = ordering.desc()
        return self._with_modified_query(
            lambda query: self.query.join(models.Company).order_by(func.lower(ordering))
        )

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

    def that_were_activated_before(self, timestamp: datetime) -> Self:
        return self._with_modified_query(
            lambda query: query.filter(models.Plan.activation_date <= timestamp)
        )

    def that_will_expire_after(self, timestamp: datetime) -> Self:
        expiration_date = (
            func.cast(concat(models.Plan.timeframe, "days"), INTERVAL)
            + models.Plan.activation_date
        )
        return self._with_modified_query(
            lambda query: query.filter(expiration_date > timestamp)
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

    def planned_by(self, *company: UUID) -> PlanQueryResult:
        companies = list(map(str, company))
        return self._with_modified_query(
            lambda query: query.filter(models.Plan.planner.in_(companies))
        )

    def with_id(self, *id_: UUID) -> PlanQueryResult:
        ids = list(map(str, id_))
        return self._with_modified_query(
            lambda query: query.filter(models.Plan.id.in_(ids))
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

    def that_are_part_of_cooperation(self, *cooperation: UUID) -> PlanQueryResult:
        cooperations = list(map(str, cooperation))
        if not cooperation:
            return self._with_modified_query(
                lambda query: query.filter(models.Plan.cooperation != None)
            )
        else:
            return self._with_modified_query(
                lambda query: query.filter(models.Plan.cooperation.in_(cooperations))
            )

    def that_request_cooperation_with_coordinator(
        self, *company: UUID
    ) -> PlanQueryResult:
        companies = list(map(str, company))
        if companies:
            return self._with_modified_query(
                lambda query: query.join(
                    models.Cooperation,
                    models.Plan.requested_cooperation == models.Cooperation.id,
                )
                .join(
                    models.Company, models.Cooperation.coordinator == models.Company.id
                )
                .filter(models.Company.id.in_(companies))
            )
        else:
            return self._with_modified_query(
                lambda query: query.filter(models.Plan.requested_cooperation != None)
            )

    def get_statistics(self) -> entities.PlanningStatistics:
        result = self.query.with_entities(
            func.avg(models.Plan.timeframe).label("duration"),
            func.sum(models.Plan.costs_p).label("costs_p"),
            func.sum(models.Plan.costs_r).label("costs_r"),
            func.sum(models.Plan.costs_a).label("costs_a"),
        ).first()
        return entities.PlanningStatistics(
            average_plan_duration_in_days=result.duration or Decimal(0),
            total_planned_costs=entities.ProductionCosts(
                means_cost=result.costs_p or Decimal(0),
                resource_cost=result.costs_r or Decimal(0),
                labour_cost=result.costs_a or Decimal(0),
            ),
        )

    def where_payout_counts_are_less_then_active_days(
        self, timestamp: datetime
    ) -> PlanQueryResult:
        payout = aliased(models.LabourCertificatesPayout)
        payouts_counted = (
            self.db.session.query(
                func.count("*").label("payout_count"),
                payout.plan_id,
            )
            .group_by(payout.plan_id)
            .subquery()
        )
        days_passed = cast(
            func.extract("day", func.age(timestamp, models.Plan.activation_date)),
            Integer,
        )
        active_days = case(
            (days_passed > models.Plan.timeframe, models.Plan.timeframe),
            else_=days_passed,
        )
        q = self._with_modified_query(
            lambda query: query.join(
                payouts_counted,
                payouts_counted.c.plan_id == models.Plan.id,
                isouter=True,
            ).filter(
                or_(
                    active_days > payouts_counted.c.payout_count,
                    payouts_counted.c.payout_count == None,
                )
            )
        )
        return q

    def that_are_not_hidden(self) -> Self:
        return self._with_modified_query(
            lambda query: query.filter(models.Plan.hidden_by_user == False)
        )

    def update(self) -> PlanUpdate:
        return PlanUpdate(
            query=self.query,
            db=self.db,
        )


@dataclass
class PlanUpdate:
    query: Any
    db: SQLAlchemy
    plan_update_values: Dict[str, Any] = field(default_factory=dict)
    review_update_values: Dict[str, Any] = field(default_factory=dict)

    def perform(self) -> int:
        row_count = 0
        if self.plan_update_values:
            sql_statement = (
                update(models.Plan)
                .where(
                    models.Plan.id.in_(
                        self.query.with_entities(models.Plan.id).scalar_subquery()
                    )
                )
                .values(**self.plan_update_values)
                .execution_options(synchronize_session="fetch")
            )
            result = self.db.session.execute(sql_statement)
            row_count = result.rowcount  # type: ignore
        if self.review_update_values:
            sql_statement = (
                update(models.PlanReview)
                .where(
                    models.PlanReview.plan_id.in_(
                        self.query.with_entities(models.Plan.id).scalar_subquery()
                    )
                )
                .values(**self.review_update_values)
                .execution_options(synchronize_session="fetch")
            )
            result = self.db.session.execute(sql_statement)
            row_count = max(row_count, result.rowcount)  # type: ignore
        return row_count

    def set_cooperation(self, cooperation: Optional[UUID]) -> PlanUpdate:
        return replace(
            self,
            plan_update_values=dict(
                self.plan_update_values,
                cooperation=str(cooperation) if cooperation else None,
            ),
        )

    def set_requested_cooperation(self, cooperation: Optional[UUID]) -> PlanUpdate:
        return replace(
            self,
            plan_update_values=dict(
                self.plan_update_values,
                requested_cooperation=str(cooperation) if cooperation else None,
            ),
        )

    def set_approval_date(self, approval_date: Optional[datetime]) -> PlanUpdate:
        return replace(
            self,
            review_update_values=dict(
                self.review_update_values, approval_date=approval_date
            ),
        )

    def set_activation_timestamp(
        self, activation_timestamp: Optional[datetime]
    ) -> PlanUpdate:
        return replace(
            self,
            plan_update_values=dict(
                self.plan_update_values,
                activation_date=activation_timestamp,
            ),
        )

    def toggle_product_availability(self) -> Self:
        return replace(
            self,
            plan_update_values=dict(
                self.plan_update_values,
                is_available=func.not_(models.Plan.is_available),
            ),
        )

    def hide(self) -> Self:
        return replace(
            self,
            plan_update_values=dict(
                self.plan_update_values,
                hidden_by_user=True,
            ),
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

    def that_are_confirmed(self) -> MemberQueryResult:
        return self._with_modified_query(
            lambda query: query.filter(models.Member.confirmed_on != None)
        )

    def update(self) -> MemberUpdate:
        return MemberUpdate(
            query=self.query,
            db=self.db,
        )


@dataclass
class MemberUpdate:
    query: Any
    db: SQLAlchemy
    member_update_values: Dict[str, Any] = field(default_factory=dict)

    def set_confirmation_timestamp(self, timestamp: datetime) -> MemberUpdate:
        return replace(
            self,
            member_update_values=dict(
                self.member_update_values,
                confirmed_on=timestamp,
            ),
        )

    def perform(self) -> int:
        row_count = 0
        if self.member_update_values:
            sql_statement = (
                update(models.Member)
                .where(
                    models.Member.id.in_(
                        self.query.with_entities(models.Member.id).scalar_subquery()
                    )
                )
                .values(**self.member_update_values)
                .execution_options(synchronize_session="fetch")
            )
            result = self.db.session.execute(sql_statement)
            row_count = result.rowcount  # type: ignore
        return row_count


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

    def add_worker(self, member: UUID) -> int:
        companies_changed = 0
        member = models.Member.query.filter(models.Member.id == str(member)).first()
        assert member
        for company in self.query:
            companies_changed += 1
            company.workers.append(member)
        return companies_changed

    def with_name_containing(self, query: str) -> CompanyQueryResult:
        return self._with_modified_query(
            lambda db_query: db_query.filter(models.Company.name.ilike(f"%{query}%"))
        )

    def with_email_containing(self, query: str) -> CompanyQueryResult:
        return self._with_modified_query(
            lambda db_query: db_query.join(models.User).filter(
                models.User.email.ilike(f"%{query}%")
            )
        )


class TransactionQueryResult(FlaskQueryResult[entities.Transaction]):
    def where_account_is_sender_or_receiver(
        self, *account: UUID
    ) -> TransactionQueryResult:
        accounts = list(map(str, account))
        return self._with_modified_query(
            lambda query: query.filter(
                or_(
                    models.Transaction.receiving_account.in_(accounts),
                    models.Transaction.sending_account.in_(accounts),
                )
            )
        )

    def where_account_is_sender(self, *account: UUID) -> TransactionQueryResult:
        accounts = map(str, account)
        return self._with_modified_query(
            lambda query: query.filter(
                models.Transaction.sending_account.in_(accounts),
            )
        )

    def where_account_is_receiver(self, *account: UUID) -> TransactionQueryResult:
        accounts = map(str, account)
        return self._with_modified_query(
            lambda query: query.filter(
                models.Transaction.receiving_account.in_(accounts),
            )
        )

    def ordered_by_transaction_date(
        self, descending: bool = False
    ) -> TransactionQueryResult:
        ordering = models.Transaction.date
        if descending:
            ordering = ordering.desc()
        return self._with_modified_query(lambda query: self.query.order_by(ordering))

    def where_sender_is_social_accounting(self) -> TransactionQueryResult:
        return self._with_modified_query(
            lambda query: self.query.join(
                models.SocialAccounting,
                models.SocialAccounting.account == models.Transaction.sending_account,
            )
        )


class AccountQueryResult(FlaskQueryResult[entities.Account]):
    def with_id(self, *id_: UUID) -> AccountQueryResult:
        ids = list(map(str, id_))
        return self._with_modified_query(
            lambda query: query.filter(models.Account.id.in_(ids))
        )


class LabourCertificatesPayoutResult(
    FlaskQueryResult[entities.LabourCertificatesPayout]
):
    def for_plan(self, plan: UUID) -> LabourCertificatesPayoutResult:
        return self._with_modified_query(
            lambda query: query.filter(
                models.LabourCertificatesPayout.plan_id == str(plan),
            )
        )


class PayoutFactorResult(FlaskQueryResult[entities.PayoutFactor]):
    def ordered_by_calculation_date(
        self, descending: bool = False
    ) -> PayoutFactorResult:
        ordering = models.PayoutFactor.timestamp
        if descending:
            ordering = ordering.desc()
        return self._with_modified_query(lambda query: query.order_by(ordering))


class CompanyPurchaseResult(FlaskQueryResult[entities.CompanyPurchase]):
    def where_buyer_is_company(self, company: UUID) -> CompanyPurchaseResult:
        transaction = aliased(models.Transaction)
        account = aliased(models.Account)
        buying_company = aliased(models.Company)
        return self._with_modified_query(
            lambda query: query.join(transaction)
            .join(account, transaction.sending_account == account.id)
            .join(
                buying_company,
                or_(
                    account.id == buying_company.p_account,
                    account.id == buying_company.r_account,
                ),
            )
            .filter(buying_company.id == str(company))
        )

    def ordered_by_creation_date(
        self, *, ascending: bool = True
    ) -> CompanyPurchaseResult:
        transaction = aliased(models.Transaction)
        ordering = transaction.date
        if not ascending:
            ordering = ordering.desc()
        return self._with_modified_query(
            lambda query: query.join(transaction).order_by(ordering)
        )

    def with_transaction_and_plan(
        self,
    ) -> FlaskQueryResult[
        Tuple[entities.CompanyPurchase, entities.Transaction, entities.Plan]
    ]:
        def mapper(
            orm,
        ) -> Tuple[entities.CompanyPurchase, entities.Transaction, entities.Plan]:
            purchase_orm, transaction_orm, plan_orm = orm
            return (
                DatabaseGatewayImpl.company_purchase_from_orm(purchase_orm),
                TransactionRepository.object_from_orm(transaction_orm),
                DatabaseGatewayImpl.plan_from_orm(plan_orm),
            )

        transaction = aliased(models.Transaction)
        plan = aliased(models.Plan)
        return FlaskQueryResult(
            db=self.db,
            mapper=mapper,
            query=self.query.join(
                transaction, models.CompanyPurchase.transaction_id == transaction.id
            )
            .join(plan, models.CompanyPurchase.plan_id == plan.id)
            .with_entities(models.CompanyPurchase, transaction, plan),
        )

    def with_transaction(
        self,
    ) -> FlaskQueryResult[Tuple[entities.CompanyPurchase, entities.Transaction]]:
        def mapper(
            orm,
        ) -> Tuple[entities.CompanyPurchase, entities.Transaction]:
            purchase_orm, transaction_orm = orm
            return (
                DatabaseGatewayImpl.company_purchase_from_orm(purchase_orm),
                TransactionRepository.object_from_orm(transaction_orm),
            )

        transaction = aliased(models.Transaction)
        return FlaskQueryResult(
            db=self.db,
            mapper=mapper,
            query=self.query.join(
                transaction, models.CompanyPurchase.transaction_id == transaction.id
            ).with_entities(models.CompanyPurchase, transaction),
        )


class ConsumerPurchaseResult(FlaskQueryResult[entities.ConsumerPurchase]):
    def where_buyer_is_member(self, member: UUID) -> ConsumerPurchaseResult:
        transaction = aliased(models.Transaction)
        account = aliased(models.Account)
        buying_member = aliased(models.Member)
        return self._with_modified_query(
            lambda query: query.join(transaction)
            .join(account, transaction.sending_account == account.id)
            .join(
                buying_member,
                account.id == buying_member.account,
            )
            .filter(buying_member.id == str(member))
        )

    def ordered_by_creation_date(
        self, *, ascending: bool = True
    ) -> ConsumerPurchaseResult:
        transaction = aliased(models.Transaction)
        ordering = transaction.date
        if not ascending:
            ordering = ordering.desc()
        return self._with_modified_query(
            lambda query: query.join(transaction).order_by(ordering)
        )

    def with_transaction_and_plan(
        self,
    ) -> FlaskQueryResult[
        Tuple[entities.ConsumerPurchase, entities.Transaction, entities.Plan]
    ]:
        def mapper(
            orm,
        ) -> Tuple[entities.ConsumerPurchase, entities.Transaction, entities.Plan]:
            purchase_orm, transaction_orm, plan_orm = orm
            return (
                DatabaseGatewayImpl.consumer_purchase_from_orm(purchase_orm),
                TransactionRepository.object_from_orm(transaction_orm),
                DatabaseGatewayImpl.plan_from_orm(plan_orm),
            )

        transaction = aliased(models.Transaction)
        plan = aliased(models.Plan)
        return FlaskQueryResult(
            db=self.db,
            mapper=mapper,
            query=self.query.join(
                transaction, models.ConsumerPurchase.transaction_id == transaction.id
            )
            .join(plan, models.ConsumerPurchase.plan_id == plan.id)
            .with_entities(models.ConsumerPurchase, transaction, plan),
        )


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
        return entities.Member(
            id=UUID(orm_object.id),
            name=orm_object.name,
            account=UUID(orm_object.account),
            email=orm_object.user.email,
            registered_on=orm_object.registered_on,
            confirmed_on=orm_object.confirmed_on,
        )

    def object_to_orm(self, member: entities.Member) -> models.Member:
        return models.Member.query.filter(models.Member.id == str(member.id)).first()

    def create_member(
        self,
        *,
        email: str,
        name: str,
        password: str,
        account: entities.Account,
        registered_on: datetime,
    ) -> entities.Member:
        user_orm = self._get_or_create_user(email, password)
        orm_member = Member(
            id=str(uuid4()),
            user=user_orm,
            name=name,
            account=str(account.id),
            registered_on=registered_on,
            confirmed_on=None,
        )
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


@dataclass
class CompanyRepository(repositories.CompanyRepository):
    db: SQLAlchemy

    def object_to_orm(self, company: entities.Company) -> Company:
        orm = models.Company.query.filter(models.Company.id == str(company.id)).first()
        assert orm
        return orm

    def object_from_orm(self, company_orm: Company) -> entities.Company:
        return entities.Company(
            id=UUID(company_orm.id),
            email=company_orm.user.email,
            name=company_orm.name,
            means_account=UUID(company_orm.p_account),
            raw_material_account=UUID(company_orm.r_account),
            work_account=UUID(company_orm.a_account),
            product_account=UUID(company_orm.prd_account),
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
        company = models.Company(
            id=str(uuid4()),
            name=name,
            registered_on=registered_on,
            confirmed_on=None,
            user=user_orm,
            p_account=str(means_account.id),
            r_account=str(resource_account.id),
            a_account=str(labour_account.id),
            prd_account=str(products_account.id),
        )
        self.db.session.add(company)
        self.db.session.flush()
        return self.object_from_orm(company)

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
        user = models.User.query.filter(
            and_(
                models.User.email == email,
            )
        ).first()
        if not user:
            user = models.User(
                email=email,
                password=generate_password_hash(password, method="sha256"),
            )
            self.db.session.add(user)
        return user

    def _get_means_account(self, company: Company) -> Account:
        account = models.Account.query.get(company.p_account)
        assert account
        return account

    def _get_resources_account(self, company: Company) -> Account:
        account = models.Account.query.get(company.r_account)
        assert account
        return account

    def _get_labour_account(self, company: Company) -> Account:
        account = models.Account.query.get(company.a_account)
        assert account
        return account

    def _get_products_account(self, company: Company) -> Account:
        account = models.Account.query.get(company.prd_account)
        assert account
        return account


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

    def get_account_balance(self, account: UUID) -> Decimal:
        account_orm = models.Account.query.filter(
            models.Account.id == str(account)
        ).first()
        assert account_orm
        received = set(account_orm.transactions_received)
        sent = set(account_orm.transactions_sent)
        intersection = received & sent
        received -= intersection
        sent -= intersection
        return decimal_sum(t.amount_received for t in received) - decimal_sum(
            t.amount_sent for t in sent
        )

    def get_by_id(self, id: UUID) -> entities.Account:
        orm = Account.query.filter(models.Account.id == str(id)).first()
        assert orm
        return self.object_from_orm(orm)

    def get_accounts(self) -> AccountQueryResult:
        return AccountQueryResult(
            db=self.db,
            mapper=self.object_from_orm,
            query=models.Account.query,
        )


@dataclass
class AccountOwnerRepository(repositories.AccountOwnerRepository):
    account_repository: AccountRepository
    member_repository: MemberRepository
    company_repository: CompanyRepository
    social_accounting_repository: AccountingRepository

    def get_account_owner(
        self, account: entities.Account
    ) -> Union[entities.Member, entities.Company, entities.SocialAccounting]:
        account_id = str(account.id)
        account_owner: Union[
            entities.Member, entities.Company, entities.SocialAccounting, None
        ] = (
            self._get_account_owner_company(account_id)
            or self._get_account_owner_member(account_id)
            or self._get_account_owner_social_accounting(account_id)
        )
        assert account_owner
        return account_owner

    def _get_account_owner_member(self, account_id: str) -> Optional[entities.Member]:
        model = models.Member.query.filter(models.Member.account == account_id).first()
        if not model:
            return None
        return self.member_repository.object_from_orm(model)

    def _get_account_owner_social_accounting(
        self, account_id: str
    ) -> Optional[entities.SocialAccounting]:
        model = models.SocialAccounting.query.filter(
            models.SocialAccounting.account == account_id
        ).first()
        if not model:
            return None
        return self.social_accounting_repository.object_from_orm(model)

    def _get_account_owner_company(self, account_id: str) -> Optional[entities.Company]:
        model = models.Company.query.filter(
            or_(
                models.Company.p_account == account_id,
                models.Company.r_account == account_id,
                models.Company.a_account == account_id,
                models.Company.prd_account == account_id,
            )
        ).first()
        if not model:
            return None
        return self.company_repository.object_from_orm(model)


@dataclass
class AccountingRepository:
    account_repository: AccountRepository
    db: SQLAlchemy

    def object_from_orm(
        self, accounting_orm: SocialAccounting
    ) -> entities.SocialAccounting:
        account = self.account_repository.get_by_id(UUID(accounting_orm.account))
        return entities.SocialAccounting(
            account=account,
            id=UUID(accounting_orm.id),
        )

    def get_or_create_social_accounting(self) -> entities.SocialAccounting:
        return self.object_from_orm(self.get_or_create_social_accounting_orm())

    def get_or_create_social_accounting_orm(self) -> SocialAccounting:
        social_accounting = models.SocialAccounting.query.first()
        if not social_accounting:
            social_accounting = SocialAccounting(
                id=str(uuid4()),
            )
            account = self.account_repository.create_account(
                entities.AccountTypes.accounting
            )
            social_accounting.account = str(account.id)
            self.db.session.add(social_accounting)
        return social_accounting

    def get_by_id(self, id: UUID) -> Optional[entities.SocialAccounting]:
        accounting_orm = SocialAccounting.query.filter_by(id=str(id)).first()
        if accounting_orm is None:
            return None
        return self.object_from_orm(accounting_orm)


@dataclass
class TransactionRepository(repositories.TransactionRepository):
    db: SQLAlchemy

    def object_to_orm(self, transaction: entities.Transaction) -> Transaction:
        return Transaction.query.get(str(transaction.id))

    @classmethod
    def object_from_orm(cls, transaction: Transaction) -> entities.Transaction:
        return entities.Transaction(
            id=UUID(transaction.id),
            date=transaction.date,
            sending_account=UUID(transaction.sending_account),
            receiving_account=UUID(transaction.receiving_account),
            amount_sent=Decimal(transaction.amount_sent),
            amount_received=Decimal(transaction.amount_received),
            purpose=transaction.purpose,
        )

    def create_transaction(
        self,
        date: datetime,
        sending_account: UUID,
        receiving_account: UUID,
        amount_sent: Decimal,
        amount_received: Decimal,
        purpose: str,
    ) -> entities.Transaction:
        transaction = Transaction(
            id=str(uuid4()),
            date=date,
            sending_account=str(sending_account),
            receiving_account=str(receiving_account),
            amount_sent=amount_sent,
            amount_received=amount_received,
            purpose=purpose,
        )
        self.db.session.add(transaction)
        self.db.session.flush()
        return self.object_from_orm(transaction)

    def get_transactions(self) -> TransactionQueryResult:
        return TransactionQueryResult(
            query=models.Transaction.query,
            mapper=self.object_from_orm,
            db=self.db,
        )

    def get_sales_balance_of_plan(self, plan: entities.Plan) -> Decimal:
        return Decimal(
            models.Transaction.query.join(
                models.Account,
                models.Transaction.receiving_account == models.Account.id,
            )
            .join(
                models.Company,
                models.Account.id == models.Company.prd_account,
            )
            .filter(models.Company.id == str(plan.planner))
            .with_entities(func.sum(models.Transaction.amount_received))
            .one()[0]
            or 0
        )


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
        orm = models.PlanDraft.query.filter(models.PlanDraft.id == str(id)).first()
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
        return models.Cooperation.query.count()


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


@dataclass
class DatabaseGatewayImpl:
    db: SQLAlchemy

    def get_labour_certificates_payouts(self) -> LabourCertificatesPayoutResult:
        return LabourCertificatesPayoutResult(
            query=models.LabourCertificatesPayout.query,
            mapper=self._labour_certificates_payout_from_orm,
            db=self.db,
        )

    def create_labour_certificates_payout(
        self, transaction: UUID, plan: UUID
    ) -> entities.LabourCertificatesPayout:
        orm = models.LabourCertificatesPayout(
            transaction_id=str(transaction),
            plan_id=str(plan),
        )
        self.db.session.add(orm)
        return self._labour_certificates_payout_from_orm(orm)

    def create_payout_factor(
        self, timestamp: datetime, payout_factor: Decimal
    ) -> entities.PayoutFactor:
        orm = models.PayoutFactor(
            timestamp=timestamp,
            payout_factor=payout_factor,
        )
        self.db.session.add(orm)
        return self._payout_factor_from_orm(orm)

    def get_payout_factors(self) -> PayoutFactorResult:
        return PayoutFactorResult(
            query=models.PayoutFactor.query,
            db=self.db,
            mapper=self._payout_factor_from_orm,
        )

    def _labour_certificates_payout_from_orm(
        self, orm: models.LabourCertificatesPayout
    ) -> entities.LabourCertificatesPayout:
        return entities.LabourCertificatesPayout(
            plan_id=UUID(orm.plan_id),
            transaction_id=UUID(orm.transaction_id),
        )

    def _payout_factor_from_orm(
        self, orm: models.PayoutFactor
    ) -> entities.PayoutFactor:
        return entities.PayoutFactor(
            calculation_date=orm.timestamp,
            value=orm.payout_factor,
        )

    def create_company_purchase(
        self, transaction: UUID, amount: int, plan: UUID
    ) -> entities.CompanyPurchase:
        orm = models.CompanyPurchase(
            plan_id=str(plan),
            transaction_id=str(transaction),
            amount=amount,
        )
        self.db.session.add(orm)
        self.db.session.flush()
        return self.company_purchase_from_orm(orm)

    def get_company_purchases(self) -> CompanyPurchaseResult:
        return CompanyPurchaseResult(
            query=models.CompanyPurchase.query,
            mapper=self.company_purchase_from_orm,
            db=self.db,
        )

    @classmethod
    def company_purchase_from_orm(
        cls, orm: models.CompanyPurchase
    ) -> entities.CompanyPurchase:
        return entities.CompanyPurchase(
            id=uuid4(),
            plan_id=UUID(orm.plan_id),
            transaction_id=UUID(orm.transaction_id),
            amount=orm.amount,
        )

    def create_consumer_purchase(
        self, transaction: UUID, amount: int, plan: UUID
    ) -> entities.ConsumerPurchase:
        orm = models.ConsumerPurchase(
            id=str(uuid4()),
            amount=amount,
            plan_id=str(plan),
            transaction_id=str(transaction),
        )
        self.db.session.add(orm)
        self.db.session.flush()
        return self.consumer_purchase_from_orm(orm)

    def get_consumer_purchases(self) -> ConsumerPurchaseResult:
        return ConsumerPurchaseResult(
            db=self.db,
            query=models.ConsumerPurchase.query,
            mapper=self.consumer_purchase_from_orm,
        )

    @classmethod
    def consumer_purchase_from_orm(
        self, orm: models.ConsumerPurchase
    ) -> entities.ConsumerPurchase:
        return entities.ConsumerPurchase(
            id=UUID(orm.id),
            amount=orm.amount,
            plan_id=UUID(orm.plan_id),
            transaction_id=UUID(orm.transaction_id),
        )

    def get_plans(self) -> PlanQueryResult:
        return PlanQueryResult(
            query=models.Plan.query,
            mapper=self.plan_from_orm,
            db=self.db,
        )

    def create_plan(
        self,
        creation_timestamp: datetime,
        planner: UUID,
        production_costs: entities.ProductionCosts,
        product_name: str,
        distribution_unit: str,
        amount_produced: int,
        product_description: str,
        duration_in_days: int,
        is_public_service: bool,
    ) -> entities.Plan:
        plan = models.Plan(
            id=str(uuid4()),
            plan_creation_date=creation_timestamp,
            planner=str(planner),
            costs_p=production_costs.means_cost,
            costs_r=production_costs.resource_cost,
            costs_a=production_costs.labour_cost,
            prd_name=product_name,
            prd_unit=distribution_unit,
            prd_amount=amount_produced,
            description=product_description,
            timeframe=duration_in_days,
            is_public_service=is_public_service,
        )
        review = models.PlanReview(approval_date=None, plan=plan)
        self.db.session.add(plan)
        self.db.session.add(review)
        return self.plan_from_orm(plan)

    @classmethod
    def plan_from_orm(cls, plan: models.Plan) -> entities.Plan:
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
            activation_date=plan.activation_date,
            requested_cooperation=UUID(plan.requested_cooperation)
            if plan.requested_cooperation
            else None,
            cooperation=UUID(plan.cooperation) if plan.cooperation else None,
            is_available=plan.is_available,
            hidden_by_user=plan.hidden_by_user,
        )
