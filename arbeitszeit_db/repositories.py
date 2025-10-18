from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime
from decimal import Decimal
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Iterator,
    Optional,
    Self,
    Tuple,
    TypeVar,
)
from uuid import UUID, uuid4

from sqlalchemy import Delete, Insert, String, Update, insert
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import InstrumentedAttribute, aliased, scoped_session
from sqlalchemy.orm.query import Query
from sqlalchemy.sql.expression import ColumnElement, and_, delete, func, or_, update
from sqlalchemy.sql.functions import concat

from arbeitszeit import records
from arbeitszeit.transfers import TransferType
from arbeitszeit_db import models
from arbeitszeit_db.db import Database
from arbeitszeit_db.models import (
    Account,
    Company,
    Member,
    PlanDraft,
    SocialAccounting,
)

T = TypeVar("T", covariant=True)


def _add_days_to_date(
    db_session: scoped_session,
    date_column: InstrumentedAttribute[datetime],
    days_column: InstrumentedAttribute[Decimal],
) -> ColumnElement[datetime]:
    bind = db_session.bind
    assert bind is not None
    engine_name = bind.engine.name

    if engine_name == "sqlite":
        return func.datetime(
            date_column, "+" + func.cast(days_column, String) + " days"
        )
    else:
        return (
            func.cast(concat(days_column, " days"), postgresql.INTERVAL) + date_column
        )


class FlaskQueryResult(Generic[T]):
    def __init__(self, query: Query, mapper: Callable[[Any], T], db: Database) -> None:
        self.query = query
        self.mapper = mapper
        self.db = db

    def limit(self, n: int) -> Self:
        return type(self)(query=self.query.limit(n), mapper=self.mapper, db=self.db)

    def offset(self, n: int) -> Self:
        return type(self)(query=self.query.offset(n), mapper=self.mapper, db=self.db)

    def first(self) -> Optional[T]:
        element = self.query.first()
        if element is None:
            return None
        return self.mapper(element)

    def _with_modified_query(self, modification: Callable[[Query], Any]) -> Self:
        return type(self)(
            query=modification(self.query), mapper=self.mapper, db=self.db
        )

    def __iter__(self) -> Iterator[T]:
        return (self.mapper(item) for item in self.query)

    def __len__(self) -> int:
        return self.query.count()


class PlanQueryResult(FlaskQueryResult[records.Plan]):
    def ordered_by_creation_date(self, ascending: bool = True) -> Self:
        ordering = (
            models.Plan.plan_creation_date.asc()
            if ascending
            else models.Plan.plan_creation_date.desc()
        )
        return self._with_modified_query(lambda query: query.order_by(ordering))

    def ordered_by_approval_date(self, ascending: bool = True) -> Self:
        plan_approval = aliased(models.PlanApproval)
        ordering = plan_approval.date.asc() if ascending else plan_approval.date.desc()
        return self._with_modified_query(
            lambda query: query.outerjoin(plan_approval).order_by(ordering)
        )

    def ordered_by_planner_name(self, ascending: bool = True) -> Self:
        company = aliased(models.Company)
        join_condition = company.id == models.Plan.planner
        order_criteria = company.name.asc() if ascending else company.name.desc()
        return self._with_modified_query(
            lambda q: q.join(company, join_condition).order_by(order_criteria)
        )

    def ordered_by_rejection_date(self, ascending: bool = True) -> Self:
        review = aliased(models.PlanReview)
        ordering = (
            review.rejection_date.asc() if ascending else review.rejection_date.desc()
        )
        query = self._with_modified_query(
            lambda query: query.join(review, review.plan_id == models.Plan.id).order_by(
                ordering
            )
        )
        return query

    def with_id_containing(self, query: str) -> Self:
        return self._with_modified_query(
            lambda db_query: db_query.filter(models.Plan.id.contains(query))
        )

    def with_product_name_containing(self, query: str) -> Self:
        return self._with_modified_query(
            lambda db_query: db_query.filter(models.Plan.prd_name.ilike(f"%{query}%"))
        )

    def that_are_approved(self) -> Self:
        return self._with_modified_query(
            lambda query: query.filter(models.Plan.approval != None)
        )

    def that_are_rejected(self) -> Self:
        plan_review = aliased(models.PlanReview)
        return self._with_modified_query(
            lambda query: query.join(plan_review).filter(
                plan_review.rejection_date != None
            )
        )

    def that_were_approved_before(self, timestamp: datetime) -> Self:
        plan_approval = aliased(models.PlanApproval)
        return self._with_modified_query(
            lambda query: query.join(plan_approval).filter(
                plan_approval.date <= timestamp
            )
        )

    def that_will_expire_after(self, timestamp: datetime) -> Self:
        approval = aliased(models.PlanApproval)
        expiration_date = _add_days_to_date(
            self.db.session, approval.date, models.Plan.timeframe
        )
        return self._with_modified_query(
            lambda query: query.join(approval).filter(expiration_date > timestamp)
        )

    def that_are_expired_as_of(self, timestamp: datetime) -> Self:
        approval = aliased(models.PlanApproval)
        expiration_date = _add_days_to_date(
            self.db.session, approval.date, models.Plan.timeframe
        )
        return self._with_modified_query(
            lambda query: query.join(approval).filter(expiration_date <= timestamp)
        )

    def that_are_productive(self) -> Self:
        return self._with_modified_query(
            lambda query: query.filter(models.Plan.is_public_service == False)
        )

    def that_are_public(self) -> Self:
        return self._with_modified_query(
            lambda query: query.filter(models.Plan.is_public_service == True)
        )

    def that_are_cooperating(self) -> Self:
        plan_cooperation = aliased(models.PlanCooperation)
        return self._with_modified_query(
            lambda query: query.join(
                plan_cooperation, plan_cooperation.plan == models.Plan.id
            )
        )

    def planned_by(self, *company: UUID) -> Self:
        companies = list(map(str, company))
        return self._with_modified_query(
            lambda query: query.filter(models.Plan.planner.in_(companies))
        )

    def with_id(self, *id_: UUID) -> Self:
        ids = list(map(str, id_))
        return self._with_modified_query(
            lambda query: query.filter(models.Plan.id.in_(ids))
        )

    def without_completed_review(self) -> Self:
        plan_review = aliased(models.PlanReview)
        return self._with_modified_query(
            lambda query: query.join(
                plan_review, plan_review.plan_id == models.Plan.id
            ).filter(
                and_(
                    models.Plan.approval == None,
                    plan_review.rejection_date == None,
                )
            )
        )

    def with_open_cooperation_request(
        self, *, cooperation: Optional[UUID] = None
    ) -> Self:
        return self._with_modified_query(
            lambda query: query.filter(
                models.Plan.requested_cooperation == str(cooperation)
                if cooperation
                else models.Plan.requested_cooperation != None
            )
        )

    def that_are_in_same_cooperation_as(self, plan: UUID) -> Self:
        plan_cooperation = aliased(models.PlanCooperation)

        cooperation_subquery = (
            self.db.session.query(models.PlanCooperation.cooperation)
            .filter(models.PlanCooperation.plan == str(plan))
            .scalar_subquery()
        )

        return self._with_modified_query(
            lambda query: query.join(
                plan_cooperation, plan_cooperation.plan == models.Plan.id
            ).filter(plan_cooperation.cooperation.in_(cooperation_subquery))
        )

    def that_are_part_of_cooperation(self, *cooperation: UUID) -> Self:
        cooperations = list(map(str, cooperation))
        plan_cooperation = aliased(models.PlanCooperation)
        if not cooperation:
            return self._with_modified_query(
                lambda query: query.join(
                    plan_cooperation, plan_cooperation.plan == models.Plan.id
                )
            )
        else:
            return self._with_modified_query(
                lambda query: query.join(
                    plan_cooperation, plan_cooperation.plan == models.Plan.id
                ).filter(plan_cooperation.cooperation.in_(cooperations))
            )

    def that_request_cooperation_with_coordinator(self, *company: UUID) -> Self:
        companies = list(map(str, company))

        cooperation = aliased(models.Cooperation)
        most_recent_tenure_holder = (
            self.db.session.query(models.CoordinationTenure)
            .filter(models.CoordinationTenure.cooperation == cooperation.id)
            .order_by(models.CoordinationTenure.start_date.desc())
            .with_entities(models.CoordinationTenure.company)
            .limit(1)
            .scalar_subquery()
        )
        if companies:
            return self._with_modified_query(
                lambda query: query.join(
                    cooperation,
                    models.Plan.requested_cooperation == cooperation.id,
                ).filter(most_recent_tenure_holder.in_(companies))
            )
        else:
            return self._with_modified_query(
                lambda query: query.filter(models.Plan.requested_cooperation != None)
            )

    def get_statistics(self) -> records.PlanningStatistics:
        result = self.query.with_entities(
            func.avg(models.Plan.timeframe).label("duration"),
            func.sum(models.Plan.costs_p).label("costs_p"),
            func.sum(models.Plan.costs_r).label("costs_r"),
            func.sum(models.Plan.costs_a).label("costs_a"),
        ).first()
        if result is None:
            return records.PlanningStatistics(
                average_plan_duration_in_days=Decimal(0),
                total_planned_costs=records.ProductionCosts(
                    means_cost=Decimal(0),
                    resource_cost=Decimal(0),
                    labour_cost=Decimal(0),
                ),
            )
        return records.PlanningStatistics(
            average_plan_duration_in_days=(
                Decimal(result.duration) if result.duration else Decimal(0)
            ),
            total_planned_costs=records.ProductionCosts(
                means_cost=Decimal(result.costs_p) if result.costs_p else Decimal(0),
                resource_cost=Decimal(result.costs_r) if result.costs_r else Decimal(0),
                labour_cost=Decimal(result.costs_a) if result.costs_a else Decimal(0),
            ),
        )

    def that_are_not_hidden(self) -> Self:
        return self._with_modified_query(
            lambda query: query.filter(models.Plan.hidden_by_user == False)
        )

    def joined_with_planner_and_cooperation(self) -> FlaskQueryResult[
        Tuple[
            records.Plan,
            records.Company,
            Optional[records.Cooperation],
        ]
    ]:
        def mapper(orm: Any) -> Tuple[
            records.Plan,
            records.Company,
            Optional[records.Cooperation],
        ]:
            return (
                DatabaseGatewayImpl.plan_from_orm(orm[0]),
                DatabaseGatewayImpl.company_from_orm(orm[1]),
                DatabaseGatewayImpl.cooperation_from_orm(orm[2]) if orm[2] else None,
            )

        planner = aliased(models.Company)
        cooperation = aliased(models.Cooperation)
        plan_cooperation = aliased(models.PlanCooperation)

        query = (
            self.query.join(planner, planner.id == models.Plan.planner)
            .outerjoin(
                plan_cooperation,
                plan_cooperation.plan == models.Plan.id,
            )
            .outerjoin(
                cooperation,
                cooperation.id == plan_cooperation.cooperation,
            )
            .with_entities(
                models.Plan,
                planner,
                cooperation,
            )
        )

        return FlaskQueryResult(
            db=self.db,
            mapper=mapper,
            query=query,
        )

    def joined_with_cooperation(
        self,
    ) -> FlaskQueryResult[tuple[records.Plan, Optional[records.Cooperation]]]:
        def mapper(orm: Any) -> tuple[records.Plan, Optional[records.Cooperation]]:
            return (
                DatabaseGatewayImpl.plan_from_orm(orm[0]),
                DatabaseGatewayImpl.cooperation_from_orm(orm[1]) if orm[1] else None,
            )

        plan_cooperation = aliased(models.PlanCooperation)
        cooperation = aliased(models.Cooperation)
        query = (
            self.query.join(
                plan_cooperation, plan_cooperation.plan == models.Plan.id, isouter=True
            )
            .join(
                cooperation,
                cooperation.id == plan_cooperation.cooperation,
                isouter=True,
            )
            .with_entities(models.Plan, cooperation)
        )

        return FlaskQueryResult(
            db=self.db,
            query=query,
            mapper=mapper,
        )

    def joined_with_provided_product_amount(
        self,
    ) -> FlaskQueryResult[Tuple[records.Plan, int]]:
        productive_consumptions = (
            self.db.session.query(models.ProductiveConsumption)
            .filter(models.ProductiveConsumption.plan_id == models.Plan.id)
            .with_entities(func.sum(models.ProductiveConsumption.amount))
            .scalar_subquery()
        )
        private_consumptions = (
            self.db.session.query(models.PrivateConsumption)
            .filter(models.PrivateConsumption.plan_id == models.Plan.id)
            .with_entities(func.sum(models.PrivateConsumption.amount))
            .scalar_subquery()
        )
        query = self.query.with_entities(
            models.Plan,
            func.coalesce(productive_consumptions, 0)
            + func.coalesce(private_consumptions, 0),
        )
        return FlaskQueryResult(
            query=query,
            db=self.db,
            mapper=lambda orm: (
                DatabaseGatewayImpl.plan_from_orm(orm[0]),
                orm[1],
            ),
        )

    def delete(self) -> None:
        self.query.delete()
        self.db.session.flush()

    def update(self) -> PlanUpdate:
        return PlanUpdate(
            query=self.query,
            db=self.db,
        )


@dataclass
class PlanUpdate:
    query: Query
    db: Database
    plan_update_values: Dict[str, Any] = field(default_factory=dict)
    review_update_values: Dict[str, Any] = field(default_factory=dict)
    cooperation_update: SetCooperation | None = None

    @dataclass
    class SetCooperation:
        cooperation: Optional[UUID]

    def perform(self) -> int:
        sql_statement: Update | Delete | Insert
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
            row_count = result.rowcount
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
            row_count = max(row_count, result.rowcount)
        if self.cooperation_update:
            match self.cooperation_update:
                case self.SetCooperation(cooperation=None):
                    sql_statement = delete(models.PlanCooperation).where(
                        models.PlanCooperation.plan.in_(
                            self.query.with_entities(models.Plan.id).scalar_subquery()
                        )
                    )
                case self.SetCooperation(cooperation=coop_id):
                    values = [
                        dict(plan=plan.id, cooperation=str(coop_id))
                        for plan in self.query
                    ]
                    sql_statement = (
                        insert(models.PlanCooperation)
                        .values(values)
                        .on_conflict_do_update(
                            constraint="plan_cooperation_pkey",
                            set_=dict(cooperation=str(coop_id)),
                        )
                    )
            result = self.db.session.execute(sql_statement)
            row_count = max(row_count, result.rowcount)
        self.db.session.flush()
        return row_count

    def set_cooperation(self, cooperation: Optional[UUID]) -> Self:
        return replace(
            self,
            cooperation_update=self.SetCooperation(cooperation),
        )

    def set_requested_cooperation(self, cooperation: Optional[UUID]) -> Self:
        return replace(
            self,
            plan_update_values=dict(
                self.plan_update_values,
                requested_cooperation=str(cooperation) if cooperation else None,
            ),
        )

    def set_rejection_date(self, rejection_date: Optional[datetime]) -> Self:
        return replace(
            self,
            review_update_values=dict(
                self.review_update_values, rejection_date=rejection_date
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


class PlanDraftResult(FlaskQueryResult[records.PlanDraft]):
    def with_id(self, id_: UUID) -> Self:
        return self._with_modified_query(
            lambda query: query.filter(models.PlanDraft.id == str(id_))
        )

    def planned_by(self, *company: UUID) -> Self:
        return self._with_modified_query(
            lambda query: query.filter(
                models.PlanDraft.planner.in_([str(i) for i in company])
            )
        )

    def delete(self) -> int:
        row_count = self.query.delete()
        self.db.session.flush()
        return row_count

    def update(self) -> PlanDraftUpdate:
        return PlanDraftUpdate(db=self.db, query=self.query)

    def joined_with_planner_and_email_address(
        self,
    ) -> FlaskQueryResult[
        tuple[records.PlanDraft, records.Company, records.EmailAddress]
    ]:
        def mapper(
            row: Any,
        ) -> tuple[records.PlanDraft, records.Company, records.EmailAddress]:
            return (
                DatabaseGatewayImpl.plan_draft_from_orm(row[0]),
                DatabaseGatewayImpl.company_from_orm(row[1]),
                DatabaseGatewayImpl.email_address_from_orm(row[2]),
            )

        company = aliased(models.Company)
        user = aliased(models.User)
        email = aliased(models.Email)
        query = (
            self.query.join(company, models.PlanDraft.planner == company.id)
            .join(user, company.user_id == user.id)
            .join(email, user.email_address == email.address)
            .with_entities(models.PlanDraft, company, email)
        )
        return FlaskQueryResult(
            db=self.db,
            mapper=mapper,
            query=query,
        )


@dataclass
class PlanDraftUpdate:
    db: Database
    query: Query
    changes: Dict[str, Any] = field(default_factory=dict)

    def set_product_name(self, name: str) -> Self:
        return self._update_column("prd_name", name)

    def set_amount(self, n: int) -> Self:
        return self._update_column("prd_amount", n)

    def set_description(self, description: str) -> Self:
        return self._update_column("description", description)

    def set_labour_cost(self, costs: Decimal) -> Self:
        return self._update_column("costs_a", costs)

    def set_means_cost(self, costs: Decimal) -> Self:
        return self._update_column("costs_p", costs)

    def set_resource_cost(self, costs: Decimal) -> Self:
        return self._update_column("costs_r", costs)

    def set_is_public_service(self, is_public_service: bool) -> Self:
        return self._update_column("is_public_service", is_public_service)

    def set_timeframe(self, days: int) -> Self:
        return self._update_column("timeframe", days)

    def set_unit_of_distribution(self, unit: str) -> Self:
        return self._update_column("prd_unit", unit)

    def _update_column(self, column: str, value: Any) -> Self:
        return replace(self, changes=dict(self.changes, **{column: value}))

    def perform(self) -> int:
        if not self.changes:
            return 0
        sql_statement = (
            update(models.PlanDraft)
            .where(
                models.PlanDraft.id.in_(
                    self.query.with_entities(models.PlanDraft.id).scalar_subquery()
                )
            )
            .values(**self.changes)
            .execution_options(synchronize_session="fetch")
        )
        rowcount = self.db.session.execute(sql_statement).rowcount
        self.db.session.flush()
        return rowcount


@dataclass
class PlanApprovalResult(FlaskQueryResult[records.PlanApproval]): ...


class MemberQueryResult(FlaskQueryResult[records.Member]):
    def working_at_company(self, company: UUID) -> Self:
        return self._with_modified_query(
            lambda query: query.filter(models.Member.workplaces.any(id=str(company)))
        )

    def with_id(self, member: UUID) -> Self:
        return self._with_modified_query(
            lambda query: query.filter(models.Member.id == str(member))
        )

    def with_email_address(self, email: str) -> Self:
        user = aliased(models.User)
        return self._with_modified_query(
            lambda query: query.join(user).filter(
                func.lower(user.email_address) == func.lower(email)
            )
        )

    def joined_with_email_address(
        self,
    ) -> FlaskQueryResult[Tuple[records.Member, records.EmailAddress]]:
        def mapper(row):
            member_orm, email_orm = row
            return (
                DatabaseGatewayImpl.member_from_orm(member_orm),
                DatabaseGatewayImpl.email_address_from_orm(email_orm),
            )

        user = aliased(models.User)
        email = aliased(models.Email)
        return FlaskQueryResult(
            mapper=mapper,
            db=self.db,
            query=self.query.join(user, user.id == models.Member.user_id)
            .join(email, email.address == user.email_address)
            .with_entities(models.Member, email),
        )


class CompanyQueryResult(FlaskQueryResult[records.Company]):
    def with_id(self, id_: UUID) -> Self:
        return self._with_modified_query(
            lambda query: query.filter(models.Company.id == str(id_))
        )

    def with_email_address(self, email: str) -> Self:
        return self._with_modified_query(
            lambda query: query.join(models.User).filter(
                func.lower(models.User.email_address) == func.lower(email)
            )
        )

    def that_are_workplace_of_member(self, member: UUID) -> Self:
        return self._with_modified_query(
            lambda query: query.filter(
                models.Company.workers.any(models.Member.id == str(member))
            )
        )

    def that_is_coordinating_cooperation(self, cooperation: UUID) -> Self:
        coop = aliased(models.Cooperation)
        most_recent_tenure_holder = (
            self.db.session.query(models.CoordinationTenure)
            .filter(models.CoordinationTenure.cooperation == coop.id)
            .order_by(models.CoordinationTenure.start_date.desc())
            .with_entities(models.CoordinationTenure.company)
            .limit(1)
            .scalar_subquery()
        )
        return self._with_modified_query(
            lambda query: query.join(
                coop, most_recent_tenure_holder == models.Company.id
            ).filter(coop.id == str(cooperation))
        )

    def add_worker(self, member: UUID) -> int:
        companies_changed = 0
        member_orm = (
            self.db.session.query(models.Member)
            .filter(models.Member.id == str(member))
            .first()
        )
        assert member_orm
        for company in self.query:
            companies_changed += 1
            company.workers.append(member_orm)
        self.db.session.flush()
        return companies_changed

    def remove_worker(self, member: UUID) -> int:
        companies_changed = 0
        member_orm = (
            self.db.session.query(models.Member)
            .filter(models.Member.id == str(member))
            .first()
        )
        assert member_orm
        for company in self.query:
            companies_changed += 1
            company.workers.remove(member_orm)
        self.db.session.flush()
        return companies_changed

    def with_name_containing(self, query: str) -> Self:
        return self._with_modified_query(
            lambda db_query: db_query.filter(models.Company.name.ilike(f"%{query}%"))
        )

    def with_email_containing(self, query: str) -> Self:
        return self._with_modified_query(
            lambda db_query: db_query.join(models.User).filter(
                models.User.email_address.ilike(f"%{query}%")
            )
        )

    def joined_with_email_address(
        self,
    ) -> FlaskQueryResult[Tuple[records.Company, records.EmailAddress]]:
        def mapper(row):
            company_orm, email_orm = row
            return (
                DatabaseGatewayImpl.company_from_orm(company_orm),
                DatabaseGatewayImpl.email_address_from_orm(email_orm),
            )

        user = aliased(models.User)
        email = aliased(models.Email)
        return FlaskQueryResult(
            mapper=mapper,
            db=self.db,
            query=self.query.join(user, user.id == models.Company.user_id)
            .join(email, email.address == user.email_address)
            .with_entities(models.Company, email),
        )


class AccountantResult(FlaskQueryResult[records.Accountant]):
    def with_email_address(self, email: str) -> Self:
        user = aliased(models.User)
        return self._with_modified_query(
            lambda query: query.join(user).filter(
                func.lower(user.email_address) == func.lower(email),
            )
        )

    def with_id(self, id_: UUID) -> Self:
        return self._with_modified_query(
            lambda query: query.filter(models.Accountant.id == str(id_))
        )

    def joined_with_email_address(
        self,
    ) -> FlaskQueryResult[Tuple[records.Accountant, records.EmailAddress]]:
        def mapper(orm: Any) -> Tuple[records.Accountant, records.EmailAddress]:
            return (
                DatabaseGatewayImpl.accountant_from_orm(orm[0]),
                DatabaseGatewayImpl.email_address_from_orm(orm[1]),
            )

        user = aliased(models.User)
        email = aliased(models.Email)
        query = (
            self.query.join(user, user.id == models.Accountant.user_id)
            .join(email, email.address == user.email_address)
            .with_entities(models.Accountant, email)
        )

        return FlaskQueryResult(
            db=self.db,
            query=query,
            mapper=mapper,
        )


class TransferQueryResult(FlaskQueryResult[records.Transfer]):
    def where_account_is_debtor(self, *account: UUID) -> Self:
        accounts = list(map(str, account))
        return self._with_modified_query(
            lambda query: query.filter(models.Transfer.debit_account.in_(accounts))
        )

    def where_account_is_creditor(self, *account: UUID) -> Self:
        accounts = list(map(str, account))
        return self._with_modified_query(
            lambda query: query.filter(models.Transfer.credit_account.in_(accounts))
        )

    def where_account_is_debtor_or_creditor(self, *account: UUID) -> Self:
        accounts = list(map(str, account))
        return self._with_modified_query(
            lambda query: query.filter(
                models.Transfer.debit_account.in_(accounts)
                | models.Transfer.credit_account.in_(accounts)
            )
        )

    def joined_with_debtor(
        self,
    ) -> FlaskQueryResult[Tuple[records.Transfer, records.AccountOwner]]:
        member = aliased(models.Member)
        company = aliased(models.Company)
        social_accounting = aliased(models.SocialAccounting)
        cooperation = aliased(models.Cooperation)
        query = (
            self.query.join(
                member, member.account == models.Transfer.debit_account, isouter=True
            )
            .join(
                company,
                or_(
                    company.p_account == models.Transfer.debit_account,
                    company.r_account == models.Transfer.debit_account,
                    company.a_account == models.Transfer.debit_account,
                    company.prd_account == models.Transfer.debit_account,
                ),
                isouter=True,
            )
            .join(
                social_accounting,
                social_accounting.account_psf == models.Transfer.debit_account,
                isouter=True,
            )
            .join(
                cooperation,
                cooperation.account == models.Transfer.debit_account,
                isouter=True,
            )
            .with_entities(
                models.Transfer, member, company, social_accounting, cooperation
            )
        )
        return FlaskQueryResult(
            query=query,
            mapper=self.map_transfer_and_account_owner,
            db=self.db,
        )

    def joined_with_creditor(
        self,
    ) -> FlaskQueryResult[Tuple[records.Transfer, records.AccountOwner]]:
        member = aliased(models.Member)
        company = aliased(models.Company)
        social_accounting = aliased(models.SocialAccounting)
        cooperation = aliased(models.Cooperation)
        query = (
            self.query.join(
                member, member.account == models.Transfer.credit_account, isouter=True
            )
            .join(
                company,
                or_(
                    company.p_account == models.Transfer.credit_account,
                    company.r_account == models.Transfer.credit_account,
                    company.a_account == models.Transfer.credit_account,
                    company.prd_account == models.Transfer.credit_account,
                ),
                isouter=True,
            )
            .join(
                social_accounting,
                social_accounting.account_psf == models.Transfer.credit_account,
                isouter=True,
            )
            .join(
                cooperation,
                cooperation.account == models.Transfer.credit_account,
                isouter=True,
            )
            .with_entities(
                models.Transfer, member, company, social_accounting, cooperation
            )
        )
        return FlaskQueryResult(
            query=query,
            mapper=self.map_transfer_and_account_owner,
            db=self.db,
        )

    @classmethod
    def map_transfer_and_account_owner(
        cls, orm: Any
    ) -> Tuple[records.Transfer, records.AccountOwner]:
        transfer, member, company, social_accounting, cooperation = orm
        account_owner: records.AccountOwner
        if member:
            account_owner = DatabaseGatewayImpl.member_from_orm(member)
        elif company:
            account_owner = DatabaseGatewayImpl.company_from_orm(company)
        elif social_accounting:
            account_owner = AccountingRepository.social_accounting_from_orm(
                social_accounting
            )
        else:
            account_owner = DatabaseGatewayImpl.cooperation_from_orm(cooperation)
        return DatabaseGatewayImpl.transfer_from_orm(transfer), account_owner

    def joined_with_debtor_and_creditor(
        self,
    ) -> FlaskQueryResult[
        Tuple[records.Transfer, records.AccountOwner, records.AccountOwner]
    ]:
        debtor_aliases = self._create_account_owner_aliases()
        creditor_aliases = self._create_account_owner_aliases()

        query = (
            self.query
            # Join debtor side
            .join(
                debtor_aliases.member,
                debtor_aliases.member.account == models.Transfer.debit_account,
                isouter=True,
            )
            .join(
                debtor_aliases.company,
                or_(
                    debtor_aliases.company.p_account == models.Transfer.debit_account,
                    debtor_aliases.company.r_account == models.Transfer.debit_account,
                    debtor_aliases.company.a_account == models.Transfer.debit_account,
                    debtor_aliases.company.prd_account == models.Transfer.debit_account,
                ),
                isouter=True,
            )
            .join(
                debtor_aliases.social_accounting,
                debtor_aliases.social_accounting.account_psf
                == models.Transfer.debit_account,
                isouter=True,
            )
            .join(
                debtor_aliases.cooperation,
                debtor_aliases.cooperation.account == models.Transfer.debit_account,
                isouter=True,
            )
            # Join creditor side
            .join(
                creditor_aliases.member,
                creditor_aliases.member.account == models.Transfer.credit_account,
                isouter=True,
            )
            .join(
                creditor_aliases.company,
                or_(
                    creditor_aliases.company.p_account
                    == models.Transfer.credit_account,
                    creditor_aliases.company.r_account
                    == models.Transfer.credit_account,
                    creditor_aliases.company.a_account
                    == models.Transfer.credit_account,
                    creditor_aliases.company.prd_account
                    == models.Transfer.credit_account,
                ),
                isouter=True,
            )
            .join(
                creditor_aliases.social_accounting,
                creditor_aliases.social_accounting.account_psf
                == models.Transfer.credit_account,
                isouter=True,
            )
            .join(
                creditor_aliases.cooperation,
                creditor_aliases.cooperation.account == models.Transfer.credit_account,
                isouter=True,
            )
            .with_entities(
                models.Transfer,
                debtor_aliases.member,
                debtor_aliases.company,
                debtor_aliases.social_accounting,
                debtor_aliases.cooperation,
                creditor_aliases.member,
                creditor_aliases.company,
                creditor_aliases.social_accounting,
                creditor_aliases.cooperation,
            )
        )
        return FlaskQueryResult(
            query=query,
            mapper=self.map_transfer_and_debtor_and_creditor,
            db=self.db,
        )

    def _create_account_owner_aliases(self):
        class AccountOwnerAliases:
            def __init__(self):
                self.member = aliased(models.Member)
                self.company = aliased(models.Company)
                self.social_accounting = aliased(models.SocialAccounting)
                self.cooperation = aliased(models.Cooperation)

        return AccountOwnerAliases()

    @classmethod
    def map_transfer_and_debtor_and_creditor(
        cls, orm: Any
    ) -> Tuple[records.Transfer, records.AccountOwner, records.AccountOwner]:
        (
            transfer,
            debtor_member,
            debtor_company,
            debtor_social_accounting,
            debtor_cooperation,
            creditor_member,
            creditor_company,
            creditor_social_accounting,
            creditor_cooperation,
        ) = orm

        debtor_owner = cls._determine_account_owner(
            debtor_member, debtor_company, debtor_social_accounting, debtor_cooperation
        )
        creditor_owner = cls._determine_account_owner(
            creditor_member,
            creditor_company,
            creditor_social_accounting,
            creditor_cooperation,
        )

        return (
            DatabaseGatewayImpl.transfer_from_orm(transfer),
            debtor_owner,
            creditor_owner,
        )

    @classmethod
    def _determine_account_owner(
        cls, member, company, social_accounting, cooperation
    ) -> records.AccountOwner:
        if member:
            return DatabaseGatewayImpl.member_from_orm(member)
        elif company:
            return DatabaseGatewayImpl.company_from_orm(company)
        elif social_accounting:
            return AccountingRepository.social_accounting_from_orm(social_accounting)
        else:
            assert cooperation
            return DatabaseGatewayImpl.cooperation_from_orm(cooperation)

    def ordered_by_date(
        self, *, ascending: bool = True
    ) -> FlaskQueryResult[records.Transfer]:
        ordering = (
            models.Transfer.date.asc() if ascending else models.Transfer.date.desc()
        )
        return self._with_modified_query(lambda query: query.order_by(ordering))


class AccountQueryResult(FlaskQueryResult[records.Account]):
    def with_id(self, *id_: UUID) -> Self:
        ids = list(map(str, id_))
        return self._with_modified_query(
            lambda query: query.filter(models.Account.id.in_(ids))
        )

    def owned_by_member(self, *members: UUID) -> Self:
        member = aliased(models.Member)
        return self._with_modified_query(
            lambda query: query.join(
                member, member.account == models.Account.id
            ).filter(member.id.in_([str(m) for m in members]))
        )

    def owned_by_company(self, *companies: UUID) -> Self:
        company = aliased(models.Company)
        return self._with_modified_query(
            lambda query: query.join(
                company,
                or_(
                    company.p_account == models.Account.id,
                    company.r_account == models.Account.id,
                    company.a_account == models.Account.id,
                    company.prd_account == models.Account.id,
                ),
            ).filter(company.id.in_([str(c) for c in companies]))
        )

    def that_are_member_accounts(self) -> Self:
        member = aliased(models.Member)
        return self._with_modified_query(
            lambda query: query.join(member, member.account == models.Account.id)
        )

    def that_are_product_accounts(self) -> Self:
        company = aliased(models.Company)
        return self._with_modified_query(
            lambda query: query.join(company, company.prd_account == models.Account.id)
        )

    def that_are_labour_accounts(self) -> Self:
        company = aliased(models.Company)
        return self._with_modified_query(
            lambda query: query.join(company, company.a_account == models.Account.id)
        )

    def joined_with_balance(self) -> FlaskQueryResult[Tuple[records.Account, Decimal]]:
        from sqlalchemy import func, select

        tf_credited = (
            select(
                models.Transfer.credit_account.label("account_id"),
                func.sum(models.Transfer.value).label("credited"),
            )
            .group_by(models.Transfer.credit_account)
            .subquery()
        )

        tf_debited = (
            select(
                models.Transfer.debit_account.label("account_id"),
                func.sum(models.Transfer.value).label("debited"),
            )
            .group_by(models.Transfer.debit_account)
            .subquery()
        )

        query = (
            self.query.outerjoin(
                tf_credited, models.Account.id == tf_credited.c.account_id
            )
            .outerjoin(tf_debited, models.Account.id == tf_debited.c.account_id)
            .with_entities(
                models.Account,
                (
                    func.coalesce(tf_credited.c.credited, 0)
                    - func.coalesce(tf_debited.c.debited, 0)
                ).label("balance"),
            )
        )

        return FlaskQueryResult(
            query=query,
            db=self.db,
            mapper=self.map_account_and_balance,
        )

    @classmethod
    def map_account_and_balance(cls, orm: Any) -> Tuple[records.Account, Decimal]:
        return DatabaseGatewayImpl.account_from_orm(orm[0]), orm[1] or Decimal(0)


class ProductiveConsumptionResult(FlaskQueryResult[records.ProductiveConsumption]):
    def where_consumer_is_company(self, company: UUID) -> Self:
        transfer = aliased(models.Transfer)
        account = aliased(models.Account)
        consuming_company = aliased(models.Company)
        return self._with_modified_query(
            lambda query: query.join(
                transfer,
                models.ProductiveConsumption.transfer_of_productive_consumption
                == transfer.id,
            )
            .join(account, transfer.debit_account == account.id)
            .join(
                consuming_company,
                or_(
                    account.id == consuming_company.p_account,
                    account.id == consuming_company.r_account,
                ),
            )
            .filter(consuming_company.id == str(company))
        )

    def where_provider_is_company(self, company: UUID) -> Self:
        transfer = aliased(models.Transfer)
        account = aliased(models.Account)
        providing_company = aliased(models.Company)
        return self._with_modified_query(
            lambda query: query.join(
                transfer,
                models.ProductiveConsumption.transfer_of_productive_consumption
                == transfer.id,
            )
            .join(account, transfer.credit_account == account.id)
            .join(
                providing_company,
                account.id == providing_company.prd_account,
            )
            .filter(providing_company.id == str(company))
        )

    def ordered_by_creation_date(self, *, ascending: bool = True) -> Self:
        transfer = aliased(models.Transfer)
        ordering = transfer.date.asc() if ascending else transfer.date.desc()
        return self._with_modified_query(
            lambda query: query.join(
                transfer,
                models.ProductiveConsumption.transfer_of_productive_consumption
                == transfer.id,
            ).order_by(ordering)
        )

    def joined_with_transfer_and_plan(
        self,
    ) -> FlaskQueryResult[
        Tuple[records.ProductiveConsumption, records.Transfer, records.Plan]
    ]:
        def mapper(
            orm,
        ) -> Tuple[records.ProductiveConsumption, records.Transfer, records.Plan]:
            consumption_orm, transfer_orm, plan_orm = orm
            return (
                DatabaseGatewayImpl.productive_consumption_from_orm(consumption_orm),
                DatabaseGatewayImpl.transfer_from_orm(transfer_orm),
                DatabaseGatewayImpl.plan_from_orm(plan_orm),
            )

        transfer = aliased(models.Transfer)
        plan = aliased(models.Plan)
        return FlaskQueryResult(
            db=self.db,
            mapper=mapper,
            query=self.query.join(
                transfer,
                models.ProductiveConsumption.transfer_of_productive_consumption
                == transfer.id,
            )
            .join(plan, models.ProductiveConsumption.plan_id == plan.id)
            .with_entities(models.ProductiveConsumption, transfer, plan),
        )

    def joined_with_transfer(
        self,
    ) -> FlaskQueryResult[Tuple[records.ProductiveConsumption, records.Transfer]]:
        def mapper(
            orm,
        ) -> Tuple[records.ProductiveConsumption, records.Transfer]:
            consumption_orm, transfer_orm = orm
            return (
                DatabaseGatewayImpl.productive_consumption_from_orm(consumption_orm),
                DatabaseGatewayImpl.transfer_from_orm(transfer_orm),
            )

        transfer = aliased(models.Transfer)
        return FlaskQueryResult(
            db=self.db,
            mapper=mapper,
            query=self.query.join(
                transfer,
                models.ProductiveConsumption.transfer_of_productive_consumption
                == transfer.id,
            ).with_entities(models.ProductiveConsumption, transfer),
        )

    def joined_with_transfer_and_provider(
        self,
    ) -> FlaskQueryResult[
        Tuple[records.ProductiveConsumption, records.Transfer, records.Company]
    ]:
        def mapper(
            orm,
        ) -> Tuple[records.ProductiveConsumption, records.Transfer, records.Company]:
            consumption_orm, transfer_orm, provider_orm = orm
            return (
                DatabaseGatewayImpl.productive_consumption_from_orm(consumption_orm),
                DatabaseGatewayImpl.transfer_from_orm(transfer_orm),
                DatabaseGatewayImpl.company_from_orm(provider_orm),
            )

        transfer = aliased(models.Transfer)
        provider = aliased(models.Company)
        plan = aliased(models.Plan)
        return FlaskQueryResult(
            db=self.db,
            mapper=mapper,
            query=self.query.join(
                transfer,
                models.ProductiveConsumption.transfer_of_productive_consumption
                == transfer.id,
            )
            .join(plan, models.ProductiveConsumption.plan_id == plan.id)
            .join(provider, provider.id == plan.planner)
            .with_entities(models.ProductiveConsumption, transfer, provider),
        )

    def joined_with_transfer_and_plan_and_consumer(
        self,
    ) -> FlaskQueryResult[
        Tuple[
            records.ProductiveConsumption,
            records.Transfer,
            records.Plan,
            records.Company,
        ]
    ]:
        def mapper(
            orm,
        ) -> Tuple[
            records.ProductiveConsumption,
            records.Transfer,
            records.Plan,
            records.Company,
        ]:
            consumption_orm, transfer_orm, plan_orm, company_orm = orm
            return (
                DatabaseGatewayImpl.productive_consumption_from_orm(consumption_orm),
                DatabaseGatewayImpl.transfer_from_orm(transfer_orm),
                DatabaseGatewayImpl.plan_from_orm(plan_orm),
                DatabaseGatewayImpl.company_from_orm(company_orm),
            )

        transfer = aliased(models.Transfer)
        account = aliased(models.Account)
        plan = aliased(models.Plan)
        company = aliased(models.Company)
        return FlaskQueryResult(
            db=self.db,
            mapper=mapper,
            query=self.query.join(
                transfer,
                models.ProductiveConsumption.transfer_of_productive_consumption
                == transfer.id,
            )
            .join(account, transfer.debit_account == account.id)
            .join(
                company,
                or_(
                    company.p_account == account.id,
                    company.r_account == account.id,
                ),
            )
            .join(plan, models.ProductiveConsumption.plan_id == plan.id)
            .with_entities(models.ProductiveConsumption, transfer, plan, company),
        )


class PrivateConsumptionResult(FlaskQueryResult[records.PrivateConsumption]):
    def where_consumer_is_member(self, member: UUID) -> Self:
        transfer = aliased(models.Transfer)
        account = aliased(models.Account)
        consuming_member = aliased(models.Member)
        return self._with_modified_query(
            lambda query: query.join(
                transfer,
                models.PrivateConsumption.transfer_of_private_consumption
                == transfer.id,
            )
            .join(account, transfer.debit_account == account.id)
            .join(
                consuming_member,
                account.id == consuming_member.account,
            )
            .filter(consuming_member.id == str(member))
        )

    def ordered_by_creation_date(self, *, ascending: bool = True) -> Self:
        transfer = aliased(models.Transfer)
        ordering = transfer.date.asc() if ascending else transfer.date.desc()
        return self._with_modified_query(
            lambda query: query.join(
                transfer,
                models.PrivateConsumption.transfer_of_private_consumption
                == transfer.id,
            ).order_by(ordering)
        )

    def where_provider_is_company(self, company: UUID) -> Self:
        transfer = aliased(models.Transfer)
        account = aliased(models.Account)
        providing_company = aliased(models.Company)
        return self._with_modified_query(
            lambda query: query.join(
                transfer,
                models.PrivateConsumption.transfer_of_private_consumption
                == transfer.id,
            )
            .join(account, transfer.credit_account == account.id)
            .join(
                providing_company,
                account.id == providing_company.prd_account,
            )
            .filter(providing_company.id == str(company))
        )

    def joined_with_transfer_and_plan(
        self,
    ) -> FlaskQueryResult[
        Tuple[records.PrivateConsumption, records.Transfer, records.Plan]
    ]:
        def mapper(
            orm,
        ) -> Tuple[records.PrivateConsumption, records.Transfer, records.Plan]:
            consumption_orm, transfer_orm, plan_orm = orm
            return (
                DatabaseGatewayImpl.private_consumption_from_orm(consumption_orm),
                DatabaseGatewayImpl.transfer_from_orm(transfer_orm),
                DatabaseGatewayImpl.plan_from_orm(plan_orm),
            )

        transfer = aliased(models.Transfer)
        plan = aliased(models.Plan)
        return FlaskQueryResult(
            db=self.db,
            mapper=mapper,
            query=self.query.join(
                transfer,
                models.PrivateConsumption.transfer_of_private_consumption
                == transfer.id,
            )
            .join(plan, models.PrivateConsumption.plan_id == plan.id)
            .with_entities(models.PrivateConsumption, transfer, plan),
        )

    def joined_with_transfer_and_plan_and_consumer(
        self,
    ) -> FlaskQueryResult[
        Tuple[
            records.PrivateConsumption,
            records.Transfer,
            records.Plan,
            records.Member,
        ]
    ]:
        def mapper(
            orm,
        ) -> Tuple[
            records.PrivateConsumption,
            records.Transfer,
            records.Plan,
            records.Member,
        ]:
            consumption_orm, transfer_orm, plan_orm, member_orm = orm
            return (
                DatabaseGatewayImpl.private_consumption_from_orm(consumption_orm),
                DatabaseGatewayImpl.transfer_from_orm(transfer_orm),
                DatabaseGatewayImpl.plan_from_orm(plan_orm),
                DatabaseGatewayImpl.member_from_orm(member_orm),
            )

        transfer = aliased(models.Transfer)
        account = aliased(models.Account)
        plan = aliased(models.Plan)
        member = aliased(models.Member)
        return FlaskQueryResult(
            db=self.db,
            mapper=mapper,
            query=self.query.join(
                transfer,
                models.PrivateConsumption.transfer_of_private_consumption
                == transfer.id,
            )
            .join(account, transfer.debit_account == account.id)
            .join(
                member,
                account.id == member.account,
            )
            .join(plan, models.PrivateConsumption.plan_id == plan.id)
            .with_entities(models.PrivateConsumption, transfer, plan, member),
        )


class CooperationResult(FlaskQueryResult[records.Cooperation]):
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
        most_recent_tenure_holder = (
            self.db.session.query(models.CoordinationTenure)
            .filter(models.CoordinationTenure.cooperation == models.Cooperation.id)
            .order_by(models.CoordinationTenure.start_date.desc())
            .with_entities(models.CoordinationTenure.company)
            .limit(1)
            .scalar_subquery()
        )
        query = self.query.filter(most_recent_tenure_holder == str(company_id))
        return self._with_modified_query(lambda _: query)

    def of_plan(self, plan_id: UUID) -> Self:
        plan_cooperation = aliased(models.PlanCooperation)
        return self._with_modified_query(
            lambda query: query.join(
                plan_cooperation,
                plan_cooperation.cooperation == models.Cooperation.id,
            ).filter(plan_cooperation.plan == str(plan_id))
        )

    def joined_with_current_coordinator(
        self,
    ) -> FlaskQueryResult[Tuple[records.Cooperation, records.Company]]:
        def mapper(
            orm,
        ) -> Tuple[records.Cooperation, records.Company]:
            cooperation_orm, company_orm = orm
            return (
                DatabaseGatewayImpl.cooperation_from_orm(cooperation_orm),
                DatabaseGatewayImpl.company_from_orm(company_orm),
            )

        company = aliased(models.Company)
        most_recent_tenure_holder = (
            self.db.session.query(models.CoordinationTenure)
            .filter(models.CoordinationTenure.cooperation == models.Cooperation.id)
            .order_by(models.CoordinationTenure.start_date.desc())
            .with_entities(models.CoordinationTenure.company)
            .limit(1)
            .scalar_subquery()
        )

        query = self.query.join(
            company, most_recent_tenure_holder == company.id
        ).with_entities(models.Cooperation, company)

        return FlaskQueryResult(
            db=self.db,
            query=query,
            mapper=mapper,
        )


class CoordinationTenureResult(FlaskQueryResult[records.CoordinationTenure]):
    def with_id(self, id_: UUID) -> Self:
        return self._with_modified_query(
            lambda query: query.filter(models.CoordinationTenure.id == str(id_))
        )

    def of_cooperation(self, cooperation_id: UUID) -> Self:
        return self._with_modified_query(
            lambda query: query.filter(
                models.CoordinationTenure.cooperation == str(cooperation_id)
            )
        )

    def joined_with_coordinator(
        self,
    ) -> FlaskQueryResult[Tuple[records.CoordinationTenure, records.Company]]:
        def mapper(
            orm,
        ) -> Tuple[records.CoordinationTenure, records.Company]:
            tenure_orm, company_orm = orm
            return (
                DatabaseGatewayImpl.coordination_tenure_from_orm(tenure_orm),
                DatabaseGatewayImpl.company_from_orm(company_orm),
            )

        company = aliased(models.Company)
        query = self.query.join(
            company, models.CoordinationTenure.company == company.id
        ).with_entities(models.CoordinationTenure, company)

        return FlaskQueryResult(
            db=self.db,
            query=query,
            mapper=mapper,
        )

    def ordered_by_start_date(self, *, ascending: bool = True) -> Self:
        ordering = (
            models.CoordinationTenure.start_date.asc()
            if ascending
            else models.CoordinationTenure.start_date.desc()
        )
        return self._with_modified_query(lambda query: query.order_by(ordering))


class CoordinationTransferRequestResult(
    FlaskQueryResult[records.CoordinationTransferRequest]
):
    def with_id(self, id_: UUID) -> Self:
        return self._with_modified_query(
            lambda query: query.filter(
                models.CoordinationTransferRequest.id == str(id_)
            )
        )

    def requested_by(self, coordination_tenure: UUID) -> Self:
        return self._with_modified_query(
            lambda query: query.filter(
                models.CoordinationTransferRequest.requesting_coordination_tenure
                == str(coordination_tenure)
            )
        )

    def joined_with_cooperation(
        self,
    ) -> FlaskQueryResult[
        Tuple[records.CoordinationTransferRequest, records.Cooperation]
    ]:
        def mapper(
            orm,
        ) -> Tuple[records.CoordinationTransferRequest, records.Cooperation]:
            request_orm, cooperation_orm = orm
            return (
                DatabaseGatewayImpl.coordination_transfer_request_from_orm(request_orm),
                DatabaseGatewayImpl.cooperation_from_orm(cooperation_orm),
            )

        cooperation = aliased(models.Cooperation)
        coordination_tenure = aliased(models.CoordinationTenure)
        query = (
            self.query.join(
                coordination_tenure,
                coordination_tenure.id
                == models.CoordinationTransferRequest.requesting_coordination_tenure,
            )
            .join(cooperation, cooperation.id == coordination_tenure.cooperation)
            .with_entities(models.CoordinationTransferRequest, cooperation)
        )

        return FlaskQueryResult(
            db=self.db,
            query=query,
            mapper=mapper,
        )


class CompanyWorkInviteResult(FlaskQueryResult[records.CompanyWorkInvite]):
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
        self.db.session.flush()

    def joined_with_member(
        self,
    ) -> FlaskQueryResult[Tuple[records.CompanyWorkInvite, records.Member]]:
        def mapper(orm) -> Tuple[records.CompanyWorkInvite, records.Member]:
            invite_orm, member_orm = orm
            return (
                DatabaseGatewayImpl.company_work_invite_from_orm(invite_orm),
                DatabaseGatewayImpl.member_from_orm(member_orm),
            )

        member = aliased(models.Member)
        query = self.query.join(
            member, member.id == models.CompanyWorkInvite.member
        ).with_entities(models.CompanyWorkInvite, member)

        return FlaskQueryResult(
            db=self.db,
            query=query,
            mapper=mapper,
        )


class EmailAddressResult(FlaskQueryResult[records.EmailAddress]):
    def with_address(self, *addresses: str) -> Self:
        return self._with_modified_query(
            lambda query: query.filter(models.Email.address.in_(addresses))
        )

    def that_belong_to_member(self, member: UUID) -> Self:
        members = aliased(models.Member)
        user = aliased(models.User)
        return self._with_modified_query(
            lambda query: query.join(user, user.email_address == models.Email.address)
            .join(members, members.user_id == user.id)
            .filter(members.id == str(member))
        )

    def that_belong_to_company(self, company: UUID) -> Self:
        companies = aliased(models.Company)
        user = aliased(models.User)
        return self._with_modified_query(
            lambda query: query.join(user, user.email_address == models.Email.address)
            .join(companies, companies.user_id == user.id)
            .filter(companies.id == str(company))
        )

    def delete(self) -> None:
        self.query.delete()
        self.db.session.flush()

    def update(self) -> EmailAddressUpdate:
        return EmailAddressUpdate(db=self.db, query=self.query)


@dataclass
class EmailAddressUpdate:
    db: Database
    query: Query
    changes: Dict[str, Any] = field(default_factory=dict)

    def set_confirmation_timestamp(self, timestamp: Optional[datetime]) -> Self:
        return replace(self, changes=dict(self.changes, confirmed_on=timestamp))

    def perform(self) -> int:
        if not self.changes:
            return 0
        sql_statement = (
            update(models.Email)
            .where(
                models.Email.address.in_(
                    self.query.with_entities(models.Email.address).scalar_subquery()
                )
            )
            .values(**self.changes)
            .execution_options(synchronize_session="fetch")
        )
        rowcount = self.db.session.execute(sql_statement).rowcount
        self.db.session.flush()
        return rowcount


class RegisteredHoursWorkedResult(FlaskQueryResult[records.RegisteredHoursWorked]):
    def at_company(self, company: UUID) -> Self:
        return self._with_modified_query(
            lambda query: query.filter(
                models.RegisteredHoursWorked.company == str(company)
            )
        )

    def ordered_by_registration_time(self, *, is_ascending: bool = True) -> Self:
        ordering = (
            models.RegisteredHoursWorked.registered_on.asc()
            if is_ascending
            else models.RegisteredHoursWorked.registered_on.desc()
        )
        return self._with_modified_query(lambda query: query.order_by(ordering))

    def joined_with_worker(self) -> FlaskQueryResult[
        Tuple[
            records.RegisteredHoursWorked,
            records.Member,
        ]
    ]:
        def mapper(
            orm,
        ) -> Tuple[records.RegisteredHoursWorked, records.Member]:
            hours_orm, member_orm = orm
            return (
                DatabaseGatewayImpl.registered_hours_worked_from_orm(hours_orm),
                DatabaseGatewayImpl.member_from_orm(member_orm),
            )

        members = aliased(models.Member)
        query = self.query.join(
            members, members.id == models.RegisteredHoursWorked.worker
        ).with_entities(models.RegisteredHoursWorked, members)

        return FlaskQueryResult(
            db=self.db,
            query=query,
            mapper=mapper,
        )

    def joined_with_transfer_of_work_certificates(self) -> FlaskQueryResult[
        Tuple[
            records.RegisteredHoursWorked,
            records.Transfer,
        ]
    ]:
        def mapper(
            orm,
        ) -> Tuple[records.RegisteredHoursWorked, records.Transfer]:
            hours_orm, transfer_orm = orm
            return (
                DatabaseGatewayImpl.registered_hours_worked_from_orm(hours_orm),
                DatabaseGatewayImpl.transfer_from_orm(transfer_orm),
            )

        transfers = aliased(models.Transfer)
        query = self.query.join(
            transfers,
            transfers.id == models.RegisteredHoursWorked.transfer_of_work_certificates,
        ).with_entities(models.RegisteredHoursWorked, transfers)

        return FlaskQueryResult(
            db=self.db,
            query=query,
            mapper=mapper,
        )

    def joined_with_worker_and_transfer_of_work_certificates(self) -> FlaskQueryResult[
        Tuple[
            records.RegisteredHoursWorked,
            records.Member,
            records.Transfer,
        ]
    ]:
        def mapper(
            orm,
        ) -> Tuple[records.RegisteredHoursWorked, records.Member, records.Transfer]:
            hours_orm, member_orm, transfer_orm = orm
            return (
                DatabaseGatewayImpl.registered_hours_worked_from_orm(hours_orm),
                DatabaseGatewayImpl.member_from_orm(member_orm),
                DatabaseGatewayImpl.transfer_from_orm(transfer_orm),
            )

        members = aliased(models.Member)
        transfers = aliased(models.Transfer)
        query = (
            self.query.join(members, members.id == models.RegisteredHoursWorked.worker)
            .join(
                transfers,
                transfers.id
                == models.RegisteredHoursWorked.transfer_of_work_certificates,
            )
            .with_entities(models.RegisteredHoursWorked, members, transfers)
        )

        return FlaskQueryResult(
            db=self.db,
            query=query,
            mapper=mapper,
        )


class AccountCredentialsResult(FlaskQueryResult[records.AccountCredentials]):
    def for_user_account_with_id(self, user_id: UUID) -> Self:
        id_ = str(user_id)
        member = aliased(models.Member)
        company = aliased(models.Company)
        accountant = aliased(models.Accountant)
        return self._with_modified_query(
            lambda query: query.join(
                member, member.user_id == models.User.id, isouter=True
            )
            .join(company, company.user_id == models.User.id, isouter=True)
            .join(accountant, accountant.user_id == models.User.id, isouter=True)
            .filter(or_(member.id == id_, company.id == id_, accountant.id == id_))
        )

    def with_email_address(self, address: str) -> Self:
        return self._with_modified_query(
            lambda query: query.filter(
                func.lower(models.User.email_address) == func.lower(address)
            )
        )

    def joined_with_accountant(
        self,
    ) -> FlaskQueryResult[
        Tuple[records.AccountCredentials, Optional[records.Accountant]]
    ]:
        def mapper(
            orm: Any,
        ) -> Tuple[records.AccountCredentials, Optional[records.Accountant]]:
            return (
                DatabaseGatewayImpl.account_credentials_from_orm(orm[0]),
                DatabaseGatewayImpl.accountant_from_orm(orm[1]) if orm[1] else None,
            )

        accountant = aliased(models.Accountant)
        query = self.query.join(
            accountant, accountant.user_id == models.User.id, isouter=True
        ).with_entities(models.User, accountant)
        return FlaskQueryResult(
            query=query,
            db=self.db,
            mapper=mapper,
        )

    def joined_with_email_address_and_accountant(
        self,
    ) -> FlaskQueryResult[
        Tuple[
            records.AccountCredentials,
            records.EmailAddress,
            Optional[records.Accountant],
        ]
    ]:
        def mapper(
            orm: Any,
        ) -> Tuple[
            records.AccountCredentials,
            records.EmailAddress,
            Optional[records.Accountant],
        ]:
            return (
                DatabaseGatewayImpl.account_credentials_from_orm(orm[0]),
                DatabaseGatewayImpl.email_address_from_orm(orm[1]),
                DatabaseGatewayImpl.accountant_from_orm(orm[2]) if orm[2] else None,
            )

        accountant = aliased(models.Accountant)
        email = aliased(models.Email)
        query = (
            self.query.join(email, email.address == models.User.email_address)
            .join(accountant, accountant.user_id == models.User.id, isouter=True)
            .with_entities(models.User, email, accountant)
        )
        return FlaskQueryResult(
            query=query,
            db=self.db,
            mapper=mapper,
        )

    def joined_with_member(
        self,
    ) -> FlaskQueryResult[Tuple[records.AccountCredentials, Optional[records.Member]]]:
        def mapper(
            orm: Any,
        ) -> Tuple[records.AccountCredentials, Optional[records.Member]]:
            return (
                DatabaseGatewayImpl.account_credentials_from_orm(orm[0]),
                DatabaseGatewayImpl.member_from_orm(orm[1]) if orm[1] else None,
            )

        member = aliased(models.Member)
        query = self.query.join(
            member, member.user_id == models.User.id, isouter=True
        ).with_entities(models.User, member)
        return FlaskQueryResult(
            query=query,
            db=self.db,
            mapper=mapper,
        )

    def joined_with_email_address_and_member(
        self,
    ) -> FlaskQueryResult[
        Tuple[
            records.AccountCredentials, records.EmailAddress, Optional[records.Member]
        ]
    ]:
        def mapper(
            orm: Any,
        ) -> Tuple[
            records.AccountCredentials, records.EmailAddress, Optional[records.Member]
        ]:
            return (
                DatabaseGatewayImpl.account_credentials_from_orm(orm[0]),
                DatabaseGatewayImpl.email_address_from_orm(orm[1]),
                DatabaseGatewayImpl.member_from_orm(orm[2]) if orm[2] else None,
            )

        member = aliased(models.Member)
        email = aliased(models.Email)
        query = (
            self.query.join(email, email.address == models.User.email_address)
            .join(member, member.user_id == models.User.id, isouter=True)
            .with_entities(models.User, email, member)
        )
        return FlaskQueryResult(
            query=query,
            db=self.db,
            mapper=mapper,
        )

    def joined_with_company(
        self,
    ) -> FlaskQueryResult[Tuple[records.AccountCredentials, Optional[records.Company]]]:
        def mapper(
            orm: Any,
        ) -> Tuple[records.AccountCredentials, Optional[records.Company]]:
            return (
                DatabaseGatewayImpl.account_credentials_from_orm(orm[0]),
                DatabaseGatewayImpl.company_from_orm(orm[1]) if orm[1] else None,
            )

        company = aliased(models.Company)
        query = self.query.join(
            company, company.user_id == models.User.id, isouter=True
        ).with_entities(models.User, company)
        return FlaskQueryResult(
            query=query,
            db=self.db,
            mapper=mapper,
        )

    def joined_with_email_address_and_company(
        self,
    ) -> FlaskQueryResult[
        Tuple[
            records.AccountCredentials,
            records.EmailAddress,
            Optional[records.Company],
        ]
    ]:
        def mapper(
            orm: Any,
        ) -> Tuple[
            records.AccountCredentials, records.EmailAddress, Optional[records.Company]
        ]:
            return (
                DatabaseGatewayImpl.account_credentials_from_orm(orm[0]),
                DatabaseGatewayImpl.email_address_from_orm(orm[1]),
                DatabaseGatewayImpl.company_from_orm(orm[2]) if orm[2] else None,
            )

        email = aliased(models.Email)
        company = aliased(models.Company)
        query = (
            self.query.join(email, email.address == models.User.email_address)
            .join(company, company.user_id == models.User.id, isouter=True)
            .with_entities(models.User, email, company)
        )
        return FlaskQueryResult(
            db=self.db,
            query=query,
            mapper=mapper,
        )

    def update(self) -> AccountCredentialsUpdate:
        return AccountCredentialsUpdate(db=self.db, query=self.query)


@dataclass
class AccountCredentialsUpdate:
    db: Database
    query: Query
    new_address: Optional[str] = None
    password_hash: Optional[str] = None

    def change_email_address(self, new_email_address: str) -> Self:
        return replace(
            self,
            new_address=new_email_address,
        )

    def change_password_hash(self, new_password_hash: str) -> Self:
        return replace(
            self,
            password_hash=new_password_hash,
        )

    def perform(self) -> int:
        new_values = dict()
        if self.new_address is not None:
            new_values["email_address"] = self.new_address
        if self.password_hash:
            new_values["password"] = self.password_hash
        if not new_values:
            return 0
        sql_statement = (
            update(models.User)
            .where(models.User.id.in_(self.query.with_entities(models.User.id)))
            .values(**new_values)
            .execution_options(synchronize_session="fetch")
        )
        rowcount = self.db.session.execute(sql_statement).rowcount
        self.db.session.flush()
        return rowcount


@dataclass
class AccountingRepository:
    database_gateway: DatabaseGatewayImpl
    db: Database

    @classmethod
    def social_accounting_from_orm(
        cls, accounting_orm: SocialAccounting
    ) -> records.SocialAccounting:
        return records.SocialAccounting(
            id=UUID(accounting_orm.id),
            account_psf=UUID(accounting_orm.account_psf),
        )

    def get_or_create_social_accounting(self) -> records.SocialAccounting:
        return self.social_accounting_from_orm(
            self.get_or_create_social_accounting_orm()
        )

    def get_or_create_social_accounting_orm(self) -> SocialAccounting:
        social_accounting = self.db.session.query(models.SocialAccounting).first()
        if not social_accounting:
            social_accounting = SocialAccounting(
                id=str(uuid4()),
            )
            account_psf = self.database_gateway.create_account()
            social_accounting.account_psf = str(account_psf.id)
            self.db.session.add(social_accounting)
            self.db.session.flush()
        return social_accounting

    def get_by_id(self, id: UUID) -> Optional[records.SocialAccounting]:
        accounting_orm = (
            self.db.session.query(SocialAccounting).filter_by(id=str(id)).first()
        )
        if accounting_orm is None:
            return None
        return self.social_accounting_from_orm(accounting_orm)


class PasswordResetRequestResult(FlaskQueryResult[records.PasswordResetRequest]):
    def with_email_address(self, email_address: str) -> Self:
        return self._with_modified_query(
            lambda query: query.filter(
                models.PasswordResetRequest.email_address == func.lower(email_address)
            )
        )

    def with_creation_date_after(self, creation_threshold: datetime) -> Self:
        return self._with_modified_query(
            lambda query: query.filter(
                models.PasswordResetRequest.created_at > creation_threshold
            )
        )


@dataclass
class DatabaseGatewayImpl:
    db: Database

    def create_productive_consumption(
        self,
        transfer_of_productive_consumption: UUID,
        transfer_of_compensation: UUID | None,
        amount: int,
        plan: UUID,
    ) -> records.ProductiveConsumption:
        orm = models.ProductiveConsumption(
            plan_id=str(plan),
            transfer_of_productive_consumption=str(transfer_of_productive_consumption),
            transfer_of_compensation=(
                str(transfer_of_compensation) if transfer_of_compensation else None
            ),
            amount=amount,
        )
        self.db.session.add(orm)
        self.db.session.flush()
        return self.productive_consumption_from_orm(orm)

    def get_productive_consumptions(self) -> ProductiveConsumptionResult:
        return ProductiveConsumptionResult(
            query=self.db.session.query(models.ProductiveConsumption),
            mapper=self.productive_consumption_from_orm,
            db=self.db,
        )

    @classmethod
    def productive_consumption_from_orm(
        cls, orm: models.ProductiveConsumption
    ) -> records.ProductiveConsumption:
        return records.ProductiveConsumption(
            id=UUID(orm.id),
            plan_id=UUID(orm.plan_id),
            transfer_of_productive_consumption=UUID(
                orm.transfer_of_productive_consumption
            ),
            transfer_of_compensation=(
                UUID(orm.transfer_of_compensation)
                if orm.transfer_of_compensation
                else None
            ),
            amount=orm.amount,
        )

    def create_private_consumption(
        self,
        transfer_of_private_consumption: UUID,
        transfer_of_compensation: UUID | None,
        amount: int,
        plan: UUID,
    ) -> records.PrivateConsumption:
        orm = models.PrivateConsumption(
            id=str(uuid4()),
            plan_id=str(plan),
            transfer_of_private_consumption=str(transfer_of_private_consumption),
            transfer_of_compensation=(
                str(transfer_of_compensation) if transfer_of_compensation else None
            ),
            amount=amount,
        )
        self.db.session.add(orm)
        self.db.session.flush()
        return self.private_consumption_from_orm(orm)

    def get_private_consumptions(self) -> PrivateConsumptionResult:
        return PrivateConsumptionResult(
            db=self.db,
            query=self.db.session.query(models.PrivateConsumption),
            mapper=self.private_consumption_from_orm,
        )

    @classmethod
    def private_consumption_from_orm(
        cls, orm: models.PrivateConsumption
    ) -> records.PrivateConsumption:
        return records.PrivateConsumption(
            id=UUID(orm.id),
            plan_id=UUID(orm.plan_id),
            transfer_of_private_consumption=UUID(orm.transfer_of_private_consumption),
            transfer_of_compensation=(
                UUID(orm.transfer_of_compensation)
                if orm.transfer_of_compensation
                else None
            ),
            amount=orm.amount,
        )

    def get_plans(self) -> PlanQueryResult:
        return PlanQueryResult(
            query=self.db.session.query(models.Plan),
            mapper=self.plan_from_orm,
            db=self.db,
        )

    def create_plan(
        self,
        creation_timestamp: datetime,
        planner: UUID,
        production_costs: records.ProductionCosts,
        product_name: str,
        distribution_unit: str,
        amount_produced: int,
        product_description: str,
        duration_in_days: int,
        is_public_service: bool,
    ) -> records.Plan:
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
        review = models.PlanReview(plan=plan, rejection_date=None)
        self.db.session.add(plan)
        self.db.session.add(review)
        self.db.session.flush()
        return self.plan_from_orm(plan)

    @classmethod
    def plan_from_orm(cls, plan: models.Plan) -> records.Plan:
        production_costs = records.ProductionCosts(
            labour_cost=plan.costs_a,
            resource_cost=plan.costs_r,
            means_cost=plan.costs_p,
        )
        return records.Plan(
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
            approval_date=plan.approval.date if plan.approval else None,
            rejection_date=plan.review.rejection_date if plan.review else None,
            requested_cooperation=(
                UUID(plan.requested_cooperation) if plan.requested_cooperation else None
            ),
            hidden_by_user=plan.hidden_by_user,
        )

    def create_cooperation(
        self,
        creation_timestamp: datetime,
        name: str,
        definition: str,
        account: UUID,
    ) -> records.Cooperation:
        cooperation = models.Cooperation(
            creation_date=creation_timestamp,
            name=name,
            definition=definition,
            account=str(account),
        )
        self.db.session.add(cooperation)
        self.db.session.flush()
        return self.cooperation_from_orm(cooperation)

    def get_cooperations(self) -> CooperationResult:
        return CooperationResult(
            mapper=self.cooperation_from_orm,
            query=self.db.session.query(models.Cooperation),
            db=self.db,
        )

    @classmethod
    def cooperation_from_orm(cls, orm: models.Cooperation) -> records.Cooperation:
        return records.Cooperation(
            id=UUID(orm.id),
            creation_date=orm.creation_date,
            name=orm.name,
            definition=orm.definition,
            account=UUID(orm.account),
        )

    def create_coordination_tenure(
        self, company: UUID, cooperation: UUID, start_date: datetime
    ) -> records.CoordinationTenure:
        coordination = models.CoordinationTenure(
            company=str(company), cooperation=str(cooperation), start_date=start_date
        )
        self.db.session.add(coordination)
        self.db.session.flush()
        return self.coordination_tenure_from_orm(coordination)

    def get_coordination_tenures(self) -> CoordinationTenureResult:
        return CoordinationTenureResult(
            mapper=self.coordination_tenure_from_orm,
            query=self.db.session.query(models.CoordinationTenure),
            db=self.db,
        )

    @classmethod
    def coordination_tenure_from_orm(
        cls, orm: models.CoordinationTenure
    ) -> records.CoordinationTenure:
        return records.CoordinationTenure(
            id=UUID(orm.id),
            company=UUID(orm.company),
            cooperation=UUID(orm.cooperation),
            start_date=orm.start_date,
        )

    def create_coordination_transfer_request(
        self,
        requesting_coordination_tenure: UUID,
        candidate: UUID,
        request_date: datetime,
    ) -> records.CoordinationTransferRequest:
        orm = models.CoordinationTransferRequest(
            id=str(uuid4()),
            requesting_coordination_tenure=str(requesting_coordination_tenure),
            candidate=str(candidate),
            request_date=request_date,
        )
        self.db.session.add(orm)
        self.db.session.flush()
        return self.coordination_transfer_request_from_orm(orm)

    def get_coordination_transfer_requests(self) -> CoordinationTransferRequestResult:
        return CoordinationTransferRequestResult(
            mapper=self.coordination_transfer_request_from_orm,
            query=self.db.session.query(models.CoordinationTransferRequest),
            db=self.db,
        )

    @classmethod
    def coordination_transfer_request_from_orm(
        cls, coordination_transfer_request: models.CoordinationTransferRequest
    ) -> records.CoordinationTransferRequest:
        return records.CoordinationTransferRequest(
            id=UUID(coordination_transfer_request.id),
            requesting_coordination_tenure=UUID(
                coordination_transfer_request.requesting_coordination_tenure
            ),
            candidate=UUID(coordination_transfer_request.candidate),
            request_date=coordination_transfer_request.request_date,
        )

    @classmethod
    def transfer_from_orm(cls, transfer: models.Transfer) -> records.Transfer:
        return records.Transfer(
            id=UUID(transfer.id),
            date=transfer.date,
            debit_account=UUID(transfer.debit_account),
            credit_account=UUID(transfer.credit_account),
            value=Decimal(transfer.value),
            type=transfer.type,
        )

    def create_transfer(
        self,
        date: datetime,
        debit_account: UUID,
        credit_account: UUID,
        value: Decimal,
        type: TransferType,
    ) -> records.Transfer:
        KNOWN_TRANSFER_TYPES = [
            "credit_p",
            "credit_r",
            "credit_a",
            "credit_public_p",
            "credit_public_r",
            "credit_public_a",
            "private_consumption",
            "productive_consumption_p",
            "productive_consumption_r",
            "compensation_for_coop",
            "compensation_for_company",
            "work_certificates",
            "taxes",
        ]
        if type.value not in KNOWN_TRANSFER_TYPES:
            raise ValueError(
                f"Invalid transfer type: {type}. Check if you need to create a db migration for {type.value}. Then add it to the whitelist."
            )
        transfer = models.Transfer(
            id=str(uuid4()),
            date=date,
            debit_account=str(debit_account),
            credit_account=str(credit_account),
            value=value,
            type=type,
        )
        self.db.session.add(transfer)
        self.db.session.flush()
        return self.transfer_from_orm(transfer)

    def get_transfers(self) -> TransferQueryResult:
        return TransferQueryResult(
            query=self.db.session.query(models.Transfer),
            db=self.db,
            mapper=self.transfer_from_orm,
        )

    def get_company_work_invites(self) -> CompanyWorkInviteResult:
        return CompanyWorkInviteResult(
            query=self.db.session.query(models.CompanyWorkInvite),
            db=self.db,
            mapper=self.company_work_invite_from_orm,
        )

    def create_company_work_invite(
        self, company: UUID, member: UUID
    ) -> records.CompanyWorkInvite:
        orm = models.CompanyWorkInvite(
            id=str(uuid4()),
            company=str(company),
            member=str(member),
        )
        self.db.session.add(orm)
        self.db.session.flush()
        return self.company_work_invite_from_orm(orm)

    @classmethod
    def company_work_invite_from_orm(
        cls, orm: models.CompanyWorkInvite
    ) -> records.CompanyWorkInvite:
        return records.CompanyWorkInvite(
            id=UUID(orm.id),
            member=UUID(orm.member),
            company=UUID(orm.company),
        )

    @classmethod
    def member_from_orm(cls, orm_object: Member) -> records.Member:
        return records.Member(
            id=UUID(orm_object.id),
            name=orm_object.name,
            account=UUID(orm_object.account),
            registered_on=orm_object.registered_on,
        )

    def create_member(
        self,
        *,
        account_credentials: UUID,
        name: str,
        account: records.Account,
        registered_on: datetime,
    ) -> records.Member:
        orm_member = Member(
            id=str(uuid4()),
            user_id=str(account_credentials),
            name=name,
            account=str(account.id),
            registered_on=registered_on,
        )
        self.db.session.add(orm_member)
        self.db.session.flush()
        return self.member_from_orm(orm_member)

    def get_members(self) -> MemberQueryResult:
        return MemberQueryResult(
            mapper=self.member_from_orm,
            query=self.db.session.query(Member),
            db=self.db,
        )

    @classmethod
    def company_from_orm(cls, company_orm: Company) -> records.Company:
        return records.Company(
            id=UUID(company_orm.id),
            name=company_orm.name,
            means_account=UUID(company_orm.p_account),
            raw_material_account=UUID(company_orm.r_account),
            work_account=UUID(company_orm.a_account),
            product_account=UUID(company_orm.prd_account),
            registered_on=company_orm.registered_on,
        )

    def create_company(
        self,
        account_credentials: UUID,
        name: str,
        means_account: records.Account,
        labour_account: records.Account,
        resource_account: records.Account,
        products_account: records.Account,
        registered_on: datetime,
    ) -> records.Company:
        company = models.Company(
            id=str(uuid4()),
            name=name,
            registered_on=registered_on,
            user_id=str(account_credentials),
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
            query=self.db.session.query(Company),
            mapper=self.company_from_orm,
            db=self.db,
        )

    def create_accountant(
        self, account_credentials: UUID, name: str
    ) -> records.Accountant:
        accountant = models.Accountant(
            id=str(uuid4()),
            name=name,
            user_id=str(account_credentials),
        )
        self.db.session.add(accountant)
        self.db.session.flush()
        return self.accountant_from_orm(accountant)

    def get_accountants(self) -> AccountantResult:
        return AccountantResult(
            query=self.db.session.query(models.Accountant),
            mapper=self.accountant_from_orm,
            db=self.db,
        )

    @classmethod
    def accountant_from_orm(cls, orm: models.Accountant) -> records.Accountant:
        return records.Accountant(
            name=orm.name,
            id=UUID(orm.id),
        )

    @classmethod
    def email_address_from_orm(cls, orm: models.Email) -> records.EmailAddress:
        return records.EmailAddress(
            orm.address,
            confirmed_on=orm.confirmed_on,
        )

    def get_email_addresses(self) -> EmailAddressResult:
        return EmailAddressResult(
            query=self.db.session.query(models.Email),
            mapper=self.email_address_from_orm,
            db=self.db,
        )

    def create_email_address(
        self, *, address: str, confirmed_on: Optional[datetime]
    ) -> records.EmailAddress:
        orm = models.Email(address=address, confirmed_on=confirmed_on)
        self.db.session.add(orm)
        if (
            already_existing := self.db.session.query(models.Email)
            .filter(func.lower(models.Email.address) == func.lower(address))
            .first()
        ):
            orm.address = already_existing.address
        self.db.session.flush()
        return self.email_address_from_orm(orm)

    def create_plan_draft(
        self,
        planner: UUID,
        product_name: str,
        description: str,
        costs: records.ProductionCosts,
        production_unit: str,
        amount: int,
        timeframe_in_days: int,
        is_public_service: bool,
        creation_timestamp: datetime,
    ) -> records.PlanDraft:
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
        self.db.session.flush()
        return self.plan_draft_from_orm(orm)

    def get_plan_drafts(self) -> PlanDraftResult:
        return PlanDraftResult(
            db=self.db,
            query=self.db.session.query(models.PlanDraft),
            mapper=self.plan_draft_from_orm,
        )

    @classmethod
    def plan_draft_from_orm(cls, orm: models.PlanDraft) -> records.PlanDraft:
        return records.PlanDraft(
            id=UUID(orm.id),
            creation_date=orm.plan_creation_date,
            planner=UUID(orm.planner),
            production_costs=records.ProductionCosts(
                labour_cost=orm.costs_a,
                resource_cost=orm.costs_r,
                means_cost=orm.costs_p,
            ),
            product_name=orm.prd_name,
            unit_of_distribution=orm.prd_unit,
            amount_produced=orm.prd_amount,
            description=orm.description,
            timeframe=int(orm.timeframe),
            is_public_service=orm.is_public_service,
        )

    @classmethod
    def account_from_orm(cls, account_orm: Account) -> records.Account:
        return records.Account(
            id=UUID(account_orm.id),
        )

    def create_account(self) -> records.Account:
        account = Account(id=str(uuid4()))
        self.db.session.add(account)
        self.db.session.flush()
        return self.account_from_orm(account)

    def get_accounts(self) -> AccountQueryResult:
        return AccountQueryResult(
            db=self.db,
            mapper=self.account_from_orm,
            query=self.db.session.query(models.Account),
        )

    def create_account_credentials(
        self, email_address: str, password_hash: str
    ) -> records.AccountCredentials:
        orm = models.User(
            id=str(uuid4()),
            password=password_hash,
            email_address=email_address,
        )
        self.db.session.add(orm)
        self.db.session.flush()
        return self.account_credentials_from_orm(orm)

    def get_account_credentials(self) -> AccountCredentialsResult:
        return AccountCredentialsResult(
            db=self.db,
            query=self.db.session.query(models.User),
            mapper=self.account_credentials_from_orm,
        )

    @classmethod
    def account_credentials_from_orm(cls, orm: Any) -> records.AccountCredentials:
        return records.AccountCredentials(
            id=UUID(orm.id),
            email_address=orm.email_address,
            password_hash=orm.password,
        )

    @classmethod
    def password_reset_request_from_orm(
        cls, password_reset_request_orm: models.PasswordResetRequest
    ) -> records.PasswordResetRequest:
        return records.PasswordResetRequest(
            id=UUID(password_reset_request_orm.id),
            email_address=password_reset_request_orm.email_address,
            reset_token=password_reset_request_orm.reset_token,
            created_at=password_reset_request_orm.created_at,
        )

    def get_password_reset_requests(self) -> PasswordResetRequestResult:
        return PasswordResetRequestResult(
            query=self.db.session.query(models.PasswordResetRequest),
            mapper=self.password_reset_request_from_orm,
            db=self.db,
        )

    def create_password_reset_request(
        self, email_address: str, reset_token: str, created_at: datetime
    ) -> records.PasswordResetRequest:
        new_entry = models.PasswordResetRequest(
            email_address=email_address, reset_token=reset_token, created_at=created_at
        )
        self.db.session.add(new_entry)
        self.db.session.flush()
        return self.password_reset_request_from_orm(new_entry)

    def create_registered_hours_worked(
        self,
        company: UUID,
        member: UUID,
        transfer_of_work_certificates: UUID,
        transfer_of_taxes: UUID,
        registered_on: datetime,
    ) -> records.RegisteredHoursWorked:
        db_record = models.RegisteredHoursWorked(
            company=str(company),
            worker=str(member),
            transfer_of_work_certificates=str(transfer_of_work_certificates),
            transfer_of_taxes=str(transfer_of_taxes),
            registered_on=registered_on,
        )
        self.db.session.add(db_record)
        self.db.session.flush()
        return self.registered_hours_worked_from_orm(db_record)

    def get_registered_hours_worked(self) -> RegisteredHoursWorkedResult:
        return RegisteredHoursWorkedResult(
            mapper=self.registered_hours_worked_from_orm,
            db=self.db,
            query=self.db.session.query(models.RegisteredHoursWorked),
        )

    @classmethod
    def registered_hours_worked_from_orm(
        cls, db_record: models.RegisteredHoursWorked
    ) -> records.RegisteredHoursWorked:
        return records.RegisteredHoursWorked(
            id=UUID(db_record.id),
            company=UUID(db_record.company),
            member=UUID(db_record.worker),
            transfer_of_work_certificates=UUID(db_record.transfer_of_work_certificates),
            transfer_of_taxes=UUID(db_record.transfer_of_taxes),
            registered_on=db_record.registered_on,
        )

    def create_plan_approval(
        self,
        plan_id: UUID,
        date: datetime,
        transfer_of_credit_p: UUID,
        transfer_of_credit_r: UUID,
        transfer_of_credit_a: UUID,
    ) -> records.PlanApproval:
        approval_orm = models.PlanApproval(
            id=str(uuid4()),
            plan_id=str(plan_id),
            date=date,
            transfer_of_credit_p=str(transfer_of_credit_p),
            transfer_of_credit_r=str(transfer_of_credit_r),
            transfer_of_credit_a=str(transfer_of_credit_a),
        )
        plan_orm = self.db.session.query(models.Plan).filter_by(id=str(plan_id)).first()
        assert plan_orm
        plan_orm.approval = approval_orm
        self.db.session.add(approval_orm)
        self.db.session.flush()
        return self.plan_approval_from_orm(approval_orm)

    @classmethod
    def plan_approval_from_orm(cls, orm: models.PlanApproval) -> records.PlanApproval:
        return records.PlanApproval(
            id=UUID(orm.id),
            plan_id=UUID(orm.plan_id),
            date=orm.date,
            transfer_of_credit_p=UUID(orm.transfer_of_credit_p),
            transfer_of_credit_r=UUID(orm.transfer_of_credit_r),
            transfer_of_credit_a=UUID(orm.transfer_of_credit_a),
        )

    def get_plan_approvals(self) -> PlanApprovalResult:
        return PlanApprovalResult(
            db=self.db,
            query=self.db.session.query(models.PlanApproval),
            mapper=self.plan_approval_from_orm,
        )
