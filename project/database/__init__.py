from __future__ import annotations
from datetime import date, datetime
from functools import wraps

import random
from typing import Optional, Union, Type
import string
from enum import Enum
from sqlalchemy.sql import func
from injector import Injector, inject

from arbeitszeit.use_cases import (
    PurchaseProduct,
    approve_plan,
    granting_credit,
    register_transaction,
    adjust_balance,
)
from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit import entities
from project.models import (
    Member,
    Company,
    Kaeufe,
    Withdrawal,
    Plan,
    SocialAccounting,
    Offer,
    Account,
)
from project.extensions import db

from .repositories import (
    CompanyRepository,
    MemberRepository,
    PlanRepository,
    ProductOfferRepository,
    TransactionRepository,
    AccountRepository,
)

_injector = Injector()


def with_injection(original_function):
    """When you wrap a function, make sure that the parameters to be
    injected come after the the parameters that the caller should
    provide.
    """

    @wraps(original_function)
    def wrapped_function(*args, **kwargs):
        return _injector.call_with_injection(
            inject(original_function), args=args, kwargs=kwargs
        )

    return wrapped_function


def commit_changes():
    db.session.commit()


def id_generator(size=10, chars=string.ascii_uppercase + string.digits):
    """generates money-code for withdrawals."""
    return "".join(random.SystemRandom().choice(chars) for _ in range(size))


@with_injection
def lookup_product_provider(
    product_offer: entities.ProductOffer,
    company_repository: CompanyRepository,
) -> entities.Company:
    offer_orm = Offer.query.filter_by(id=product_offer.id).first()
    plan_orm = offer_orm.plan
    company_orm = plan_orm.company
    return company_repository.object_from_orm(company_orm)


# Kaufen


class PurposesOfPurchases(Enum):
    means_of_prod = "means_of_prod"
    raw_materials = "raw_materials"


@with_injection
def buy(
    kaufender_type,
    offer: Offer,
    amount: int,
    purpose: PurposesOfPurchases,
    kaeufer_id,
    purchase_product: PurchaseProduct,
    company_repository: CompanyRepository,
    member_repository: MemberRepository,
    product_offer_repository: ProductOfferRepository,
    transaction_repository: TransactionRepository,
) -> None:
    """
    buy product.
    """
    # register purchase
    buyer_model: Union[Type[Company], Type[Member]] = (
        Company if kaufender_type == "company" else Member
    )
    buyer_orm = (
        db.session.query(buyer_model).filter(buyer_model.id == kaeufer_id).first()
    )
    buyer: Union[entities.Member, entities.Company] = (
        company_repository.object_from_orm(buyer_orm)
        if kaufender_type == "company"
        else member_repository.object_from_orm(buyer_orm)
    )
    product_offer = product_offer_repository.object_from_orm(offer)

    purchase_product(
        product_offer,
        amount,
        purpose,
        buyer,
    )

    # reduce balance of buyer account
    price = product_offer.price_per_unit
    price_total = price * amount
    if isinstance(buyer, Member):
        adjust_balance(
            buyer.account,
            -price_total,
        )
    else:
        if purpose == "means_of_prod":
            adjust_balance(
                buyer.accounts.filter_by(account_type, "p").first(),
                -price_total,
            )
        else:
            adjust_balance(
                buyer.accounts.filter_by(account_type, "r").first(),
                -price_total,
            )

    # increase balance of seller prd account
    adjust_balance(product_offer.provider.product_account, price_total)
    commit_changes()

    # register transactions
    if isinstance(buyer, entities.Member):
        account_from = buyer.account
    else:
        if purpose == "means_of_prod":
            account_from = buyer.accounts.filter_by(account_type="p").first()
        else:
            account_from = buyer.accounts.filter_by(account_type="r").first()

    send_to = product_offer.provider.product_account

    transaction = register_transaction(
        account_from=account_from,
        account_to=send_to,
        amount=product_offer.price_per_unit * amount,
        purpose=f"Angebot-Id: {offer.id}",
    )
    transaction_repository.add(transaction)
    commit_changes()


@with_injection
def planning(
    planner_id,
    plan_details,
    social_accounting_id,
) -> Plan:
    """
    create plan.
    """

    (
        costs_p,
        costs_r,
        costs_a,
        prd_name,
        prd_unit,
        prd_amount,
        description,
        timeframe,
    ) = plan_details

    plan_orm = Plan(
        plan_creation_date=datetime.now(),
        planner=planner_id,
        costs_p=costs_p,
        costs_r=costs_r,
        costs_a=costs_a,
        prd_name=prd_name,
        prd_unit=prd_unit,
        prd_amount=prd_amount,
        description=description,
        timeframe=timeframe,
        social_accounting=social_accounting_id,
    )

    db.session.add(plan_orm)
    commit_changes()
    return plan_orm


@with_injection
def seek_approval(
    plan_orm: Plan,
    plan_repository: PlanRepository,
) -> Plan:
    """Company seeks plan approval from Social Accounting."""
    datetime_service = DatetimeService()
    plan = plan_repository.object_from_orm(plan_orm)
    plan = approve_plan(
        datetime_service,
        plan,
    )
    commit_changes()
    plan_orm = plan_repository.object_to_orm(plan)
    return plan_orm


@with_injection
def grant_credit(
    plan_orm: Plan,
    plan_repository: PlanRepository,
    account_repository: AccountRepository,
    transaction_repository: TransactionRepository,
) -> None:
    """Social Accounting grants credit after plan has been approved."""
    assert plan_orm.approved == True
    plan = plan_repository.object_from_orm(plan_orm)
    social_accounting_account_orm = Account.query.filter_by(
        account_type="accounting"
    ).first()
    social_accounting_account = account_repository.object_from_orm(
        social_accounting_account_orm
    )
    granting_credit(plan)

    # register transactions
    transaction_1 = register_transaction(
        account_from=social_accounting_account,
        account_to=plan.planner.means_account,
        amount=plan.costs_p,
        purpose=f"Plan-Id: {plan.id}",
    )
    transaction_repository.add(transaction_1)

    transaction_2 = register_transaction(
        account_from=social_accounting_account,
        account_to=plan.planner.raw_material_account,
        amount=plan.costs_r,
        purpose=f"Plan-Id: {plan.id}",
    )
    transaction_repository.add(transaction_2)

    transaction_3 = register_transaction(
        account_from=social_accounting_account,
        account_to=plan.planner.work_account,
        amount=plan.costs_a,
        purpose=f"Plan-Id: {plan.id}",
    )
    transaction_repository.add(transaction_3)

    prd = plan.costs_p + plan.costs_r + plan.costs_a

    transaction_4 = register_transaction(
        account_from=social_accounting_account,
        account_to=plan.planner.product_account,
        amount=-prd,
        purpose=f"Plan-Id: {plan.id}",
    )
    transaction_repository.add(transaction_4)
    commit_changes()


@with_injection
def send_wages(
    sender_orm: Company,
    receiver_orm: Member,
    amount,
    company_repository: CompanyRepository,
    member_repository: MemberRepository,
    transaction_repository: TransactionRepository,
):
    sender = company_repository.object_from_orm(sender_orm)
    sender_account = sender.work_account
    receiver = member_repository.object_from_orm(receiver_orm)
    receiver_account = receiver.account
    # adjust balance of both
    adjust_balance(sender_account, -amount)
    adjust_balance(receiver_account, amount)
    # register transaction
    transaction = register_transaction(sender_account, receiver_account, amount, "Lohn")
    transaction_repository.add(transaction)
    commit_changes()


# User


def get_user_by_mail(email) -> Member:
    """returns first user in User, filtered by email."""
    member = Member.query.filter_by(email=email).first()
    return member


def get_user_by_id(id) -> Member:
    """returns first user in User, filtered by id."""
    member = Member.query.filter_by(id=id).first()
    return member


def add_new_user(email, name, password) -> None:
    """
    adds a new user to User.
    """
    new_user = Member(email=email, name=name, password=password)
    db.session.add(new_user)
    db.session.commit()
    return new_user


def add_new_account_for_member(member_id):
    new_account = Account(
        account_owner_member=member_id,
        account_type="member",
    )
    db.session.add(new_account)
    db.session.commit()


def get_purchases(user_id) -> list:
    """returns all purchases made by user."""
    purchases = (
        db.session.query(
            Kaeufe.id,
            Offer.name,
            Offer.description,
            func.round(Kaeufe.kaufpreis, 2).label("preis"),
        )
        .select_from(Kaeufe)
        .filter_by(member=user_id)
        .join(Offer, Kaeufe.angebot == Offer.id)
        .all()
    )
    return purchases


def get_workplaces(member_id) -> list:
    """returns all workplaces the user is assigned to."""
    member = Member.query.filter_by(id=member_id).first()
    workplaces = member.workplaces.all()
    return workplaces


def withdraw(user_id, amount) -> str:
    """
    register new withdrawal and withdraw amount from user's account.
    returns code that can be used like money.
    """
    code = id_generator()
    new_withdrawal = Withdrawal(
        type_member=True, member=user_id, betrag=amount, code=code
    )
    db.session.add(new_withdrawal)
    db.session.commit()

    # betrag vom guthaben des users abziehen
    member = db.session.query(Member).filter(Member.id == user_id).first()
    member.guthaben -= amount
    db.session.commit()

    return code


# Company


def get_company_by_mail(email) -> Company:
    """returns first company in Company, filtered by mail."""
    company = Company.query.filter_by(email=email).first()
    return company


def add_new_company(email, name, password) -> Company:
    """
    adds a new company to Company.
    """
    new_company = Company(email=email, name=name, password=password)
    db.session.add(new_company)
    db.session.commit()
    return new_company


def add_new_accounts_for_company(company_id):
    for type in ["p", "r", "a", "prd"]:
        new_account = Account(
            account_owner_company=company_id,
            account_type=type,
        )
        db.session.add(new_account)
        db.session.commit()


def get_workers(company_id) -> list:
    """get all workers working in a company."""
    company = Company.query.filter_by(id=company_id).first()
    workers = company.workers.all()
    return workers


def get_worker_in_company(worker_id, company_id) -> Union[Member, None]:
    """get specific worker in a company, if exists."""
    company = Company.query.filter_by(id=company_id).first()
    worker = company.workers.filter_by(id=worker_id).first()
    return worker


def delete_product(offer_id) -> None:
    """delete product."""
    offer = Offer.query.filter_by(id=offer_id).first()
    offer.active = False
    db.session.commit()


# Worker


def add_new_worker_to_company(member_id, company_id) -> None:
    """
    Add member as workers to Company.
    """
    worker = Member.query.filter_by(id=member_id).first()
    company = Company.query.filter_by(id=company_id).first()
    company.workers.append(worker)
    db.session.commit()


# Search Offers


def get_offer_by_id(id) -> Offer:
    """get offer, filtered by id"""
    offer = Offer.query.filter_by(id=id).first()
    return offer


# create one social accounting with id=1
def create_social_accounting_in_db() -> None:
    social_accounting = SocialAccounting.query.filter_by(id=1).first()
    if not social_accounting:
        social_accounting = SocialAccounting(id=1)
        db.session.add(social_accounting)
        db.session.commit()


def add_new_account_for_social_accounting():
    account = Account.query.filter_by(account_owner_social_accounting=1).first()
    if not account:
        account = Account(
            account_owner_social_accounting=1,
            account_type="accounting",
        )
        db.session.add(account)
        db.session.commit()
