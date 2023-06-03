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
)
from uuid import UUID, uuid4

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, and_, case, cast, func, or_, update
from sqlalchemy.dialects.postgresql import INTERVAL
from sqlalchemy.orm import aliased
from sqlalchemy.sql.functions import concat
from typing_extensions import Self

from arbeitszeit import entities, repositories
from arbeitszeit.decimal import decimal_sum
from arbeitszeit_flask import models
from arbeitszeit_flask.models import (
    Account,
    Company,
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
        user = aliased(models.User)
        return self._with_modified_query(
            lambda query: query.join(user).filter(user.email_confirmed_on != None)
        )

    def joined_with_email_address(
        self,
    ) -> FlaskQueryResult[Tuple[entities.Member, entities.EmailAddress]]:
        def mapper(row):
            member_orm, user_orm = row
            return (
                DatabaseGatewayImpl.member_from_orm(member_orm),
                DatabaseGatewayImpl.email_address_from_orm(user_orm),
            )

        user = aliased(models.User)
        return FlaskQueryResult(
            mapper=mapper,
            db=self.db,
            query=self.query.join(user, user.id == models.Member.user_id).with_entities(
                models.Member, user
            ),
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
    user_update_values: Dict[str, Any] = field(default_factory=dict)

    def set_confirmation_timestamp(self, timestamp: datetime) -> MemberUpdate:
        return replace(
            self,
            user_update_values=dict(
                self.user_update_values,
                email_confirmed_on=timestamp,
            ),
        )

    def perform(self) -> int:
        row_count = 0
        if self.user_update_values:
            sql_statement = (
                update(models.User)
                .where(
                    models.User.id.in_(
                        self.query.with_entities(
                            models.Member.user_id
                        ).scalar_subquery()
                    )
                )
                .values(**self.user_update_values)
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

    def that_are_confirmed(self) -> Self:
        user = aliased(models.User)
        return self._with_modified_query(
            lambda query: query.join(user, user.id == models.Company.user_id).filter(
                user.email_confirmed_on != None
            )
        )

    def joined_with_email_address(
        self,
    ) -> FlaskQueryResult[Tuple[entities.Company, entities.EmailAddress]]:
        def mapper(row):
            company_orm, user_orm = row
            return (
                DatabaseGatewayImpl.company_from_orm(company_orm),
                DatabaseGatewayImpl.email_address_from_orm(user_orm),
            )

        user = aliased(models.User)
        return FlaskQueryResult(
            mapper=mapper,
            db=self.db,
            query=self.query.join(
                user, user.id == models.Company.user_id
            ).with_entities(models.Company, user),
        )

    def update(self) -> CompanyUpdate:
        return CompanyUpdate(
            query=self.query,
            db=self.db,
        )


@dataclass
class CompanyUpdate:
    query: Any
    db: SQLAlchemy
    user_update_values: Dict[str, Any] = field(default_factory=dict)

    def set_confirmation_timestamp(self, timestamp: datetime) -> Self:
        return replace(
            self,
            user_update_values=dict(
                self.user_update_values, email_confirmed_on=timestamp
            ),
        )

    def perform(self) -> int:
        row_count = 0
        if self.user_update_values:
            sql_statement = (
                update(models.User)
                .where(
                    models.User.id.in_(
                        self.query.with_entities(
                            models.Company.user_id
                        ).scalar_subquery()
                    )
                )
                .values(**self.user_update_values)
                .execution_options(synchronize_session="fetch")
            )
            result = self.db.session.execute(sql_statement)
            row_count = result.rowcount  # type: ignore
        return row_count


class AccountantResult(FlaskQueryResult[entities.Accountant]):
    def with_email_address(self, email: str) -> Self:
        user = aliased(models.User)
        return self._with_modified_query(
            lambda query: query.join(user).filter(user.email == email)
        )

    def with_id(self, id_: UUID) -> Self:
        return self._with_modified_query(
            lambda query: query.filter(models.Accountant.id == str(id_))
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

    def that_were_a_sale_for_plan(self, *plan: UUID) -> Self:
        plan_ids = [str(p) for p in plan]
        consumer_purchase = aliased(models.ConsumerPurchase)
        company_purchase = aliased(models.CompanyPurchase)
        valid_consumer_purchase = consumer_purchase.query
        valid_company_purchase = company_purchase.query
        if plan:
            valid_company_purchase = valid_company_purchase.filter(
                company_purchase.plan_id.in_(plan_ids)
            )
            valid_consumer_purchase = valid_consumer_purchase.filter(
                consumer_purchase.plan_id.in_(plan_ids)
            )
        return self._with_modified_query(
            lambda query: query.filter(
                or_(
                    models.Transaction.id.in_(
                        valid_consumer_purchase.with_entities(
                            consumer_purchase.transaction_id
                        ).scalar_subquery()
                    ),
                    models.Transaction.id.in_(
                        valid_company_purchase.with_entities(
                            company_purchase.transaction_id
                        ).scalar_subquery()
                    ),
                )
            )
        )

    def joined_with_sender_and_receiver(
        self,
    ) -> FlaskQueryResult[
        Tuple[entities.Transaction, entities.AccountOwner, entities.AccountOwner]
    ]:
        sender_member = aliased(models.Member)
        sender_company = aliased(models.Company)
        sender_social_accounting = aliased(models.SocialAccounting)
        receiver_member = aliased(models.Member)
        receiver_company = aliased(models.Company)
        receiver_social_accounting = aliased(models.SocialAccounting)
        return FlaskQueryResult(
            query=self.query.join(
                sender_member,
                sender_member.account == models.Transaction.sending_account,
                isouter=True,
            )
            .join(
                sender_company,
                or_(
                    sender_company.r_account == models.Transaction.sending_account,
                    sender_company.p_account == models.Transaction.sending_account,
                    sender_company.a_account == models.Transaction.sending_account,
                    sender_company.prd_account == models.Transaction.sending_account,
                ),
                isouter=True,
            )
            .join(
                sender_social_accounting,
                sender_social_accounting.account == models.Transaction.sending_account,
                isouter=True,
            )
            .join(
                receiver_member,
                receiver_member.account == models.Transaction.receiving_account,
                isouter=True,
            )
            .join(
                receiver_company,
                or_(
                    receiver_company.r_account == models.Transaction.receiving_account,
                    receiver_company.p_account == models.Transaction.receiving_account,
                    receiver_company.a_account == models.Transaction.receiving_account,
                    receiver_company.prd_account
                    == models.Transaction.receiving_account,
                ),
                isouter=True,
            )
            .join(
                receiver_social_accounting,
                receiver_social_accounting.account
                == models.Transaction.receiving_account,
                isouter=True,
            )
            .with_entities(
                models.Transaction,
                sender_member,
                sender_company,
                sender_social_accounting,
                receiver_member,
                receiver_company,
                receiver_social_accounting,
            ),
            mapper=self.map_transaction_and_sender_and_receiver,
            db=self.db,
        )

    @classmethod
    def map_transaction_and_sender_and_receiver(
        cls, orm: Any
    ) -> Tuple[entities.Transaction, entities.AccountOwner, entities.AccountOwner]:
        (
            transaction,
            sending_member,
            sending_company,
            sender_social_accounting,
            receiver_member,
            receiver_company,
            receiver_social_accounting,
        ) = orm
        sender: entities.AccountOwner
        receiver: entities.AccountOwner
        if sending_member:
            sender = DatabaseGatewayImpl.member_from_orm(sending_member)
        elif sending_company:
            sender = DatabaseGatewayImpl.company_from_orm(sending_company)
        else:
            sender = AccountingRepository.social_accounting_from_orm(
                sender_social_accounting
            )
        if receiver_member:
            receiver = DatabaseGatewayImpl.member_from_orm(receiver_member)
        elif receiver_company:
            receiver = DatabaseGatewayImpl.company_from_orm(receiver_company)
        else:
            receiver = AccountingRepository.social_accounting_from_orm(
                receiver_social_accounting
            )
        return (
            DatabaseGatewayImpl.transaction_from_orm(transaction),
            sender,
            receiver,
        )


class AccountQueryResult(FlaskQueryResult[entities.Account]):
    def with_id(self, *id_: UUID) -> AccountQueryResult:
        ids = list(map(str, id_))
        return self._with_modified_query(
            lambda query: query.filter(models.Account.id.in_(ids))
        )

    def joined_with_owner(
        self,
    ) -> FlaskQueryResult[Tuple[entities.Account, entities.AccountOwner]]:
        member = aliased(models.Member)
        company = aliased(models.Company)
        social_accounting = aliased(models.SocialAccounting)
        query = (
            self.query.join(member, member.account == models.Account.id, isouter=True)
            .join(
                company,
                or_(
                    company.p_account == models.Account.id,
                    company.r_account == models.Account.id,
                    company.a_account == models.Account.id,
                    company.prd_account == models.Account.id,
                ),
                isouter=True,
            )
            .join(
                social_accounting,
                models.Account.id == social_accounting.account,
                isouter=True,
            )
            .with_entities(models.Account, member, company, social_accounting)
        )
        return FlaskQueryResult(
            query=query,
            mapper=self.map_account_and_owner,
            db=self.db,
        )

    @classmethod
    def map_account_and_owner(
        cls, orm: Any
    ) -> Tuple[entities.Account, entities.AccountOwner]:
        owner: entities.AccountOwner
        account, member, company, social_accounting = orm
        if member:
            owner = DatabaseGatewayImpl.member_from_orm(member)
        elif company:
            owner = DatabaseGatewayImpl.company_from_orm(company)
        else:
            owner = AccountingRepository.social_accounting_from_orm(social_accounting)
        return (
            AccountRepository.account_from_orm(account),
            owner,
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
            lambda query: query.join(
                transaction, models.CompanyPurchase.transaction_id == transaction.id
            ).order_by(ordering)
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
                DatabaseGatewayImpl.transaction_from_orm(transaction_orm),
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
                DatabaseGatewayImpl.transaction_from_orm(transaction_orm),
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
            lambda query: query.join(
                transaction, models.ConsumerPurchase.transaction_id == transaction.id
            ).order_by(ordering)
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
                DatabaseGatewayImpl.transaction_from_orm(transaction_orm),
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


class CooperationResult(FlaskQueryResult[entities.Cooperation]):
    def with_id(self, id_: UUID) -> Self:
        return self._with_modified_query(
            lambda query: query.filter(models.Cooperation.id == str(id_))
        )

    def with_name_ignoring_case(self, name: str) -> Self:
        return self._with_modified_query(
            lambda query: query.filter(
                func.lower(models.Cooperation.name) == func.lower(name)
            )
        )

    def coordinated_by_company(self, company_id: UUID) -> Self:
        return self._with_modified_query(
            lambda query: query.filter(
                models.Cooperation.coordinator == str(company_id)
            )
        )

    def joined_with_coordinator(
        self,
    ) -> FlaskQueryResult[Tuple[entities.Cooperation, entities.Company]]:
        def mapper(
            orm,
        ) -> Tuple[entities.Cooperation, entities.Company]:
            cooperation_orm, company_orm = orm
            return (
                DatabaseGatewayImpl.cooperation_from_orm(cooperation_orm),
                DatabaseGatewayImpl.company_from_orm(company_orm),
            )

        company = aliased(models.Company)
        return FlaskQueryResult(
            db=self.db,
            query=self.query.join(
                company, models.Cooperation.coordinator == company.id
            ).with_entities(models.Cooperation, company),
            mapper=mapper,
        )


class CompanyWorkInviteResult(FlaskQueryResult[entities.CompanyWorkInvite]):
    def with_id(self, id: UUID) -> Self:
        return self._with_modified_query(
            lambda query: query.filter(models.CompanyWorkInvite.id == str(id))
        )

    def issued_by(self, company: UUID) -> Self:
        return self._with_modified_query(
            lambda query: query.filter(models.CompanyWorkInvite.company == str(company))
        )

    def addressing(self, member: UUID) -> Self:
        return self._with_modified_query(
            lambda query: query.filter(models.CompanyWorkInvite.member == str(member))
        )

    def delete(self) -> None:
        self.query.delete()


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
class AccountRepository(repositories.AccountRepository):
    db: SQLAlchemy

    @classmethod
    def account_from_orm(cls, account_orm: Account) -> entities.Account:
        return entities.Account(
            id=UUID(account_orm.id),
        )

    def create_account(self) -> entities.Account:
        account = Account(id=str(uuid4()))
        self.db.session.add(account)
        return self.account_from_orm(account)

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

    def get_accounts(self) -> AccountQueryResult:
        return AccountQueryResult(
            db=self.db,
            mapper=self.account_from_orm,
            query=models.Account.query,
        )


@dataclass
class AccountingRepository:
    account_repository: AccountRepository
    db: SQLAlchemy

    @classmethod
    def social_accounting_from_orm(
        cls, accounting_orm: SocialAccounting
    ) -> entities.SocialAccounting:
        return entities.SocialAccounting(
            account=UUID(accounting_orm.account),
            id=UUID(accounting_orm.id),
        )

    def get_or_create_social_accounting(self) -> entities.SocialAccounting:
        return self.social_accounting_from_orm(
            self.get_or_create_social_accounting_orm()
        )

    def get_or_create_social_accounting_orm(self) -> SocialAccounting:
        social_accounting = models.SocialAccounting.query.first()
        if not social_accounting:
            social_accounting = SocialAccounting(
                id=str(uuid4()),
            )
            account = self.account_repository.create_account()
            social_accounting.account = str(account.id)
            self.db.session.add(social_accounting)
        return social_accounting

    def get_by_id(self, id: UUID) -> Optional[entities.SocialAccounting]:
        accounting_orm = SocialAccounting.query.filter_by(id=str(id)).first()
        if accounting_orm is None:
            return None
        return self.social_accounting_from_orm(accounting_orm)


@dataclass
class PlanDraftRepository(repositories.PlanDraftRepository):
    db: SQLAlchemy

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
        return entities.PlanDraft(
            id=orm.id,
            creation_date=orm.plan_creation_date,
            planner=UUID(orm.planner),
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

    def create_cooperation(
        self,
        creation_timestamp: datetime,
        name: str,
        definition: str,
        coordinator: UUID,
    ) -> entities.Cooperation:
        cooperation = models.Cooperation(
            creation_date=creation_timestamp,
            name=name,
            definition=definition,
            coordinator=str(coordinator),
        )
        self.db.session.add(cooperation)
        self.db.session.flush()
        return self.cooperation_from_orm(cooperation)

    def get_cooperations(self) -> CooperationResult:
        return CooperationResult(
            mapper=self.cooperation_from_orm,
            query=models.Cooperation.query,
            db=self.db,
        )

    @classmethod
    def cooperation_from_orm(self, orm: models.Cooperation) -> entities.Cooperation:
        return entities.Cooperation(
            id=UUID(orm.id),
            creation_date=orm.creation_date,
            name=orm.name,
            definition=orm.definition,
            coordinator=UUID(orm.coordinator),
        )

    @classmethod
    def transaction_from_orm(cls, transaction: Transaction) -> entities.Transaction:
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
        return self.transaction_from_orm(transaction)

    def get_transactions(self) -> TransactionQueryResult:
        return TransactionQueryResult(
            query=models.Transaction.query,
            mapper=self.transaction_from_orm,
            db=self.db,
        )

    def get_company_work_invites(self) -> CompanyWorkInviteResult:
        return CompanyWorkInviteResult(
            query=models.CompanyWorkInvite.query,
            db=self.db,
            mapper=self.company_work_invite_from_orm,
        )

    def create_company_work_invite(
        self, company: UUID, member: UUID
    ) -> entities.CompanyWorkInvite:
        orm = models.CompanyWorkInvite(
            id=str(uuid4()),
            company=str(company),
            member=str(member),
        )
        self.db.session.add(orm)
        return self.company_work_invite_from_orm(orm)

    @classmethod
    def company_work_invite_from_orm(
        cls, orm: models.CompanyWorkInvite
    ) -> entities.CompanyWorkInvite:
        return entities.CompanyWorkInvite(
            id=UUID(orm.id),
            member=UUID(orm.member),
            company=UUID(orm.company),
        )

    @classmethod
    def member_from_orm(cls, orm_object: Member) -> entities.Member:
        return entities.Member(
            id=UUID(orm_object.id),
            name=orm_object.name,
            account=UUID(orm_object.account),
            email=orm_object.user.email,
            registered_on=orm_object.registered_on,
            password_hash=orm_object.user.password,
        )

    def create_member(
        self,
        *,
        email: str,
        name: str,
        password_hash: str,
        account: entities.Account,
        registered_on: datetime,
    ) -> entities.Member:
        user_orm = self._get_or_create_user(
            email=email, password_hash=password_hash, email_confirmed_on=None
        )
        orm_member = Member(
            id=str(uuid4()),
            user=user_orm,
            name=name,
            account=str(account.id),
            registered_on=registered_on,
        )
        self.db.session.add(orm_member)
        return self.member_from_orm(orm_member)

    def get_members(self) -> MemberQueryResult:
        return MemberQueryResult(
            mapper=self.member_from_orm,
            query=Member.query,
            db=self.db,
        )

    def _get_or_create_user(
        self, *, email: str, password_hash: str, email_confirmed_on: Optional[datetime]
    ) -> models.User:
        return self.db.session.query(models.User).filter(
            models.User.email == email
        ).first() or models.User(
            email=email,
            password=password_hash,
            email_confirmed_on=email_confirmed_on,
        )

    @classmethod
    def company_from_orm(cls, company_orm: Company) -> entities.Company:
        return entities.Company(
            id=UUID(company_orm.id),
            email=company_orm.user.email,
            name=company_orm.name,
            means_account=UUID(company_orm.p_account),
            raw_material_account=UUID(company_orm.r_account),
            work_account=UUID(company_orm.a_account),
            product_account=UUID(company_orm.prd_account),
            registered_on=company_orm.registered_on,
            password_hash=company_orm.user.password,
        )

    def create_company(
        self,
        email: str,
        name: str,
        password_hash: str,
        means_account: entities.Account,
        labour_account: entities.Account,
        resource_account: entities.Account,
        products_account: entities.Account,
        registered_on: datetime,
    ) -> entities.Company:
        user_orm = self._get_or_create_user(
            email=email, password_hash=password_hash, email_confirmed_on=None
        )
        company = models.Company(
            id=str(uuid4()),
            name=name,
            registered_on=registered_on,
            user=user_orm,
            p_account=str(means_account.id),
            r_account=str(resource_account.id),
            a_account=str(labour_account.id),
            prd_account=str(products_account.id),
        )
        self.db.session.add(company)
        self.db.session.flush()
        return self.company_from_orm(company)

    def get_companies(self) -> CompanyQueryResult:
        return CompanyQueryResult(
            query=Company.query,
            mapper=self.company_from_orm,
            db=self.db,
        )

    def create_accountant(self, email: str, name: str, password_hash: str) -> UUID:
        user_id = uuid4()
        user_orm = self._get_or_create_user(
            email=email, password_hash=password_hash, email_confirmed_on=None
        )
        accountant = models.Accountant(
            id=str(user_id),
            name=name,
            user=user_orm,
        )
        self.db.session.add(accountant)
        return user_id

    def get_accountants(self) -> AccountantResult:
        return AccountantResult(
            query=models.Accountant.query,
            mapper=self.accountant_from_orm,
            db=self.db,
        )

    @classmethod
    def accountant_from_orm(self, orm: models.Accountant) -> entities.Accountant:
        return entities.Accountant(
            email_address=orm.user.email,
            name=orm.name,
            id=UUID(orm.id),
            password_hash=orm.user.password,
        )

    @classmethod
    def email_address_from_orm(self, orm: models.User) -> entities.EmailAddress:
        return entities.EmailAddress(
            orm.email,
            confirmed_on=orm.email_confirmed_on,
        )
