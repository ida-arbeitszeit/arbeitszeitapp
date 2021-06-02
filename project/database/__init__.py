from __future__ import annotations
from datetime import date, datetime
from functools import wraps

import random
from decimal import Decimal
from typing import Optional, Union, Type
import string
from sqlalchemy.sql import func, case
from graphviz import Graph
from sqlalchemy.orm import aliased
from injector import Injector, inject

from arbeitszeit.use_cases import (
    PurchaseProduct,
    seeking_approval,
    granting_credit,
)
from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.purchase_factory import PurchaseFactory
from arbeitszeit import entities
from project.models import (
    Member,
    Company,
    Angebote,
    Arbeit,
    Produktionsmittel,
    Kaeufe,
    Withdrawal,
    KooperationenMitglieder,
    Plan,
    SocialAccounting,
    TransactionsAccountingToCompany,
    TransactionsCompanyToMember,
    TransactionsCompanyToCompany,
    Offer,
)
from project.extensions import db

from .repositories import (
    CompanyRepository,
    MemberRepository,
    PlanRepository,
    ProductOfferRepository,
    PurchaseRepository,
    TransactionRepository,
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


def social_accounting_from_orm(
    social_accounting: SocialAccounting,
) -> entities.SocialAccounting:
    return entities.SocialAccounting(id=social_accounting.id)


def social_accounting_to_orm(
    social_accounting: entities.SocialAccounting,
) -> SocialAccounting:
    return SocialAccounting.query.get(social_accounting.id)


def get_social_accounting_by_id(id: int) -> Optional[entities.SocialAccounting]:
    social_accounting_orm = SocialAccounting.query.filter_by(id=id).first()
    return (
        social_accounting_from_orm(social_accounting_orm)
        if social_accounting_orm
        else None
    )


@with_injection
def lookup_product_provider(
    product_offer: entities.ProductOffer,
    company_repository: CompanyRepository,
) -> entities.Company:
    offer_orm = Offer.query.filter_by(id=product_offer.id).first()
    plan_orm = offer_orm.plan
    company_orm = plan_orm.company
    return company_repository.object_from_orm(company_orm)


class SearchProducts:
    """
    All SQL-requests around searching in the catalog.
    Returns non-mutable _collections.result-Objects.
    """

    def get_offers(self):
        """
        returns BaseQuery object with all products available
        (grouped results, active or not),
        with several columns, including the coop-price.
        """

        km = aliased(KooperationenMitglieder)
        km2 = aliased(KooperationenMitglieder)

        # subquery returns koop-preis
        subq = (
            db.session.query(func.avg(Angebote.preis))
            .select_from(km)
            .join(Angebote)
            .filter(Angebote.aktiv == True, km.kooperation == km2.kooperation)
            .group_by(km.kooperation)
            .as_scalar()
        )

        qry = (
            db.session.query(
                func.min(Angebote.id).label("id"),
                Angebote.name.label("angebot_name"),
                func.min(Angebote.p_kosten).label("p_kosten"),
                func.min(Angebote.v_kosten).label("v_kosten"),
                Company.name.label("company_name"),
                Company.id.label("company_id"),
                Company.email,
                Angebote.beschreibung,
                Angebote.kategorie,
                Angebote.preis,
                func.count(Angebote.id).label("vorhanden"),
                km2.kooperation,
                case(
                    [
                        (km2.kooperation == None, Angebote.preis),
                    ],
                    else_=subq,
                ).label("koop_preis"),
            )
            .select_from(Angebote)
            .join(Company, Angebote.company == Company.id)
            .outerjoin(km2, Angebote.id == km2.mitglied)
            .group_by(
                Company,
                Angebote.cr_date,
                "angebot_name",
                Angebote.beschreibung,
                Angebote.kategorie,
                Angebote.preis,
                km2.kooperation,
            )
        )

        return qry

    def get_offer_by_id(self, angebote_id):
        """returns one angebot filtered by angebote_id."""
        return self.get_offers().filter(Angebote.id == angebote_id).one()

    def get_active_offers(self, search_string="", search_field=""):
        """
        returns all aktive angebote.
        search string and search field may be optionally specified.
        """
        if search_string or search_field:
            if search_field == "Name":
                angebote = (
                    self.get_offers()
                    .filter(Angebote.name.contains(search_string))
                    .all()
                )

            elif search_field == "Beschreibung":
                angebote = (
                    self.get_offers()
                    .filter(Angebote.beschreibung.contains(search_string))
                    .all()
                )

            elif search_field == "Kategorie":
                angebote = (
                    self.get_offers()
                    .filter(Angebote.kategorie.contains(search_string))
                    .all()
                )
        else:
            angebote = self.get_offers().filter(Angebote.aktiv == True).all()
        return angebote


class CompositionOfPrices:
    """
    All SQL-requests around the topic of (graphical) representations of
    the composition of prices.
    """

    def get_table_of_composition(self, angebote_id):
        """
        makes a sql request to the db, gives back the composition of price
        (preiszusammensetzung) in table format of the specified Angebot.
        """
        angebote1 = aliased(Angebote)
        angebote2 = aliased(Angebote)
        angebote3 = aliased(Angebote)
        angebote4 = aliased(Angebote)
        angebote5 = aliased(Angebote)

        produktionsmittel1 = aliased(Produktionsmittel)
        produktionsmittel2 = aliased(Produktionsmittel)
        produktionsmittel3 = aliased(Produktionsmittel)
        produktionsmittel4 = aliased(Produktionsmittel)
        produktionsmittel5 = aliased(Produktionsmittel)

        kaeufe2 = aliased(Kaeufe)
        kaeufe3 = aliased(Kaeufe)
        kaeufe4 = aliased(Kaeufe)
        kaeufe5 = aliased(Kaeufe)

        first_level = (
            db.session.query(
                angebote1.id.label("angebot1"),
                angebote1.name.label("name1"),
                angebote1.p_kosten.label("p1"),
                angebote1.v_kosten.label("v1"),
                angebote1.preis.label("preis1"),
                produktionsmittel1.prozent_gebraucht.label("proz_gebr2"),
                produktionsmittel1.kauf.label("kauf2"),
                kaeufe2.angebot.label("angebot2"),
                angebote2.name.label("name2"),
                angebote2.preis.label("preis2"),
                (angebote2.preis * (produktionsmittel1.prozent_gebraucht / 100)).label(
                    "kosten2"
                ),
                produktionsmittel2.prozent_gebraucht.label("proz_gebr3"),
                produktionsmittel2.kauf.label("kauf3"),
                kaeufe3.angebot.label("angebot3"),
                angebote3.name.label("name3"),
                angebote3.preis.label("preis3"),
                (angebote3.preis * (produktionsmittel2.prozent_gebraucht / 100)).label(
                    "kosten3"
                ),
                produktionsmittel3.prozent_gebraucht.label("proz_gebr4"),
                produktionsmittel3.kauf.label("kauf4"),
                kaeufe4.angebot.label("angebot4"),
                angebote4.name.label("name4"),
                angebote4.preis.label("preis4"),
                (angebote4.preis * (produktionsmittel3.prozent_gebraucht / 100)).label(
                    "kosten4"
                ),
                produktionsmittel4.prozent_gebraucht.label("proz_gebr5"),
                produktionsmittel4.kauf.label("kauf5"),
                kaeufe5.angebot.label("angebot5"),
                angebote5.name.label("name5"),
                angebote5.preis.label("preis5"),
                (angebote5.preis * (produktionsmittel4.prozent_gebraucht / 100)).label(
                    "kosten5"
                ),
                produktionsmittel5.prozent_gebraucht.label("proz_gebr6"),
                produktionsmittel5.kauf.label("kauf6"),
            )
            .select_from(angebote1)
            .filter(angebote1.id == angebote_id)
            .outerjoin(produktionsmittel1, angebote1.id == produktionsmittel1.angebot)
        )

        second_level = (
            first_level.outerjoin(kaeufe2, produktionsmittel1.kauf == kaeufe2.id)
            .outerjoin(angebote2, kaeufe2.angebot == angebote2.id)
            .outerjoin(produktionsmittel2, angebote2.id == produktionsmittel2.angebot)
        )

        third_level = (
            second_level.outerjoin(kaeufe3, produktionsmittel2.kauf == kaeufe3.id)
            .outerjoin(angebote3, kaeufe3.angebot == angebote3.id)
            .outerjoin(produktionsmittel3, angebote3.id == produktionsmittel3.angebot)
        )

        fourth_level = (
            third_level.outerjoin(kaeufe4, produktionsmittel3.kauf == kaeufe4.id)
            .outerjoin(angebote4, kaeufe4.angebot == angebote4.id)
            .outerjoin(produktionsmittel4, angebote4.id == produktionsmittel4.angebot)
        )

        fifth_level = (
            fourth_level.outerjoin(kaeufe5, produktionsmittel4.kauf == kaeufe5.id)
            .outerjoin(angebote5, kaeufe5.angebot == angebote5.id)
            .outerjoin(produktionsmittel5, angebote5.id == produktionsmittel5.angebot)
        )

        table_of_composition = fifth_level
        return table_of_composition

    def get_positions_in_table(self, base_query):
        """
        takes a 'flask_sqlalchemy.BaseQuery' and creates list of dictionaries
        that stores the info, in which row and column of the database table
        the angebote are positioned
        """
        col1, col2, col3, col4, col5 = [], [], [], [], []
        for row in base_query:
            col1.append(row.name1)
            col2.append(row.name2)
            col3.append(row.name3)
            col4.append(row.name4)
            col5.append(row.name5)
        list_of_cols = [col1, col2, col3, col4, col5]

        cols_dict = []
        for r in range(len(list_of_cols)):
            list1 = []
            for c, i in enumerate(list_of_cols[r]):
                keys_in_list1 = []
                for j in list1:
                    if j.keys():
                        keys_in_list1.append(list(j.keys())[0])

                if i in list(keys_in_list1):
                    for item in list1:
                        if list(item.keys())[0] == i:
                            item[i].append(c)
                elif i is None:
                    pass
                else:
                    list1.append({i: [c]})
            cols_dict.append(list1)
        return cols_dict

    def create_dots(self, cols_dict, table_of_composition):
        """
        creates dot nodes and edges based on position of angebote in cols_dict/
        the database table. If angebot x is in the same row and next
        column of angebot y, x is child of y and will be connected with an
        edge.
        """
        dot = Graph(comment="Graph zur Preiszusammensetzung", format="svg")
        for cnt, col in enumerate(cols_dict):
            if cnt == 0:  # if first column (should be all the same angebot)
                angebot_0 = list(col[0].keys())[0]
                dot.node(
                    f"{angebot_0}_{cnt}",
                    f"{angebot_0}, "
                    f"Preis: {round(table_of_composition[0].preis1, 2)} Std.",
                )
                dot.node(
                    f"{angebot_0}_v_{cnt}",
                    f"Arbeitskraft: \
{round(table_of_composition[0].v1, 2)} Std.",
                )
                dot.edge(f"{angebot_0}_{cnt}", f"{angebot_0}_v_{cnt}")
            else:  # the following columns
                for j in col:
                    current_angebot = list(j.keys())[0]
                    current_position = list(j.values())[0]
                    if cnt == 1:
                        current_kosten = round(
                            table_of_composition[current_position[0]].kosten2, 2
                        )
                        dot.node(
                            f"{current_angebot}_{cnt}",
                            f"{current_angebot}, \
Kosten: {current_kosten} Std.",
                        )
                    elif cnt in [2, 3, 4]:
                        dot.node(f"{current_angebot}_{cnt}", f"{current_angebot}")

                    parent_angebote_list = cols_dict[cnt - 1]
                    for par in parent_angebote_list:
                        parent_angebot = list(par.keys())[0]
                        parent_positions = list(par.values())[0]
                        for cur_pos in current_position:
                            if cur_pos in parent_positions:
                                # create edge between parent and current node
                                dot.edge(
                                    f"{parent_angebot}_{cnt-1}",
                                    f"{current_angebot}_{cnt}",
                                )
                                break  # only one match is enough
        return dot


# Kaufen


@with_injection
def buy(
    kaufender_type,
    offer: Offer,
    amount,
    purpose,
    kaeufer_id,
    purchase_product: PurchaseProduct,
    company_repository: CompanyRepository,
    member_repository: MemberRepository,
    product_offer_repository: ProductOfferRepository,
    purchase_repository: PurchaseRepository,
) -> None:
    """
    buy product.
    """
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
    # change: make it work on object level
    if kaufender_type == "company":
        transaction_orm = TransactionsCompanyToCompany(
            date=datetime.now(),
            account_owner=kaeufer_id,
            receiver_id=offer.plan.planner,
            owner_account_type="p" if purpose == "means_of_prod" else "r",
            receiver_account_type="prd",
            amount=amount
            * (offer.plan.costs_p + offer.plan.costs_r + offer.plan.costs_a),
            purpose=f"Angebot-Id: {offer.id}",
        )
        db.session.add(transaction_orm)

    commit_changes()


@with_injection
def planning(
    planner_id,
    plan_details,
    social_accounting_id,
    company_repository: CompanyRepository,
    plan_repository: PlanRepository,
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

    plan_repository.add(plan_orm)
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
    plan = seeking_approval(
        datetime_service,
        plan,
    )
    commit_changes()
    plan_orm = plan_repository.object_to_orm(plan)
    return plan_orm


@with_injection
def grant_credit(
    plan: Plan,
    plan_repository: PlanRepository,
) -> None:
    """Social Accounting grants credit after plan has been approved."""
    assert plan.approved == True
    # plan = plan_repository.object_from_orm(plan)
    # plan = granting_credit(plan)
    # plan = plan_repository.object_to_orm(plan)

    costs_p = plan.costs_p
    costs_r = plan.costs_r
    costs_a = plan.costs_a
    prd = costs_p + costs_r + costs_a
    planner = plan.company

    # adjust company balances
    planner.balance_p += costs_p
    planner.balance_r += costs_r
    planner.balance_a += costs_a
    planner.balance_prd -= prd
    commit_changes()

    # add four type of accounting transactions to db
    for cost_tuple in [("p", costs_p), ("r", costs_r), ("a", costs_a), ("prd", -prd)]:
        if cost_tuple[1] == 0:
            continue
        db.session.add(
            TransactionsAccountingToCompany(
                date=datetime.now(),
                account_owner=plan.social_accounting,
                receiver_id=planner.id,
                receiver_account_type=cost_tuple[0],
                amount=cost_tuple[1],
                purpose=f"Plan-Id: {plan.id}",
            )
        )
    commit_changes()


@with_injection
def send_wages(
    sender_orm: Company,
    receiver_orm: Member,
    amount,
    company_repository: CompanyRepository,
    member_repository: MemberRepository,
):
    transaction_orm = TransactionsCompanyToMember(
        date=datetime.now(),
        account_owner=sender_orm.id,
        receiver_id=receiver_orm.id,
        amount=amount,
        purpose="Lohn",
    )
    db.session.add(transaction_orm)
    commit_changes()

    sender = company_repository.object_from_orm(sender_orm)
    sender.reduce_credit(amount, "balance_a")
    receiver = member_repository.object_from_orm(receiver_orm)
    receiver.increase_credit(amount)
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


def get_purchases(user_id) -> list:
    """returns all purchases made by user."""
    purchases = (
        db.session.query(
            Kaeufe.id,
            Angebote.name,
            Angebote.beschreibung,
            func.round(Angebote.preis, 2).label("preis"),
        )
        .select_from(Kaeufe)
        .filter_by(member=user_id)
        .join(Angebote, Kaeufe.angebot == Angebote.id)
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


def add_new_company(email, name, password) -> None:
    """
    adds a new company to Company.
    """
    new_company = Company(email=email, name=name, password=password)
    db.session.add(new_company)
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


def get_hours_worked(company_id) -> list:
    """get all hours worked in a company, grouped by workers."""
    hours_worked = (
        db.session.query(
            Member.id, Member.name, func.sum(Arbeit.stunden).label("summe_stunden")
        )
        .select_from(Angebote)
        .filter(Angebote.company == company_id)
        .join(Arbeit)
        .join(Member)
        .group_by(Member.id)
        .order_by(func.sum(Arbeit.stunden).desc())
        .all()
    )
    return hours_worked


def get_means_of_prod(company_id) -> tuple:
    """
    returns tuple of active and inactive means of prouction of company.
    """
    produktionsmittel_qry = (
        db.session.query(
            Kaeufe.id,
            Angebote.name,
            Angebote.beschreibung,
            func.round(Kaeufe.kaufpreis, 2).label("kaufpreis"),
            func.round(
                func.coalesce(func.sum(Produktionsmittel.prozent_gebraucht), 0), 2
            ).label("prozent_gebraucht"),
        )
        .select_from(Kaeufe)
        .filter(Kaeufe.company == company_id)
        .outerjoin(Produktionsmittel, Kaeufe.id == Produktionsmittel.kauf)
        .join(Angebote, Kaeufe.angebot == Angebote.id)
        .group_by(Kaeufe, Angebote, Produktionsmittel.kauf)
    )

    produktionsmittel_aktiv = produktionsmittel_qry.having(
        func.coalesce(
            func.sum(Produktionsmittel.prozent_gebraucht).label("prozent_gebraucht"), 0
        ).label("prozent_gebraucht")
        < 100
    ).all()
    produktionsmittel_inaktiv = produktionsmittel_qry.having(
        func.coalesce(
            func.sum(Produktionsmittel.prozent_gebraucht).label("prozent_gebraucht"), 0
        ).label("prozent_gebraucht")
        == 100
    ).all()

    return (produktionsmittel_aktiv, produktionsmittel_inaktiv)


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


# Search Angebote


def get_offer_by_id(id) -> Angebote:
    """get offer, filtered by id"""
    offer = Angebote.query.filter_by(id=id).first()
    return offer


# create one social accounting with id=1
def create_social_accounting_in_db() -> None:
    social_accounting = SocialAccounting.query.filter_by(id=1).first()
    if not social_accounting:
        social_accounting = SocialAccounting(id=1)
        db.session.add(social_accounting)
        db.session.commit()
