import random
from decimal import Decimal
from typing import Union
import string
from project.models import Member, Company, Worker, Angebote, Arbeit,\
    Produktionsmittel, Kaeufe, Auszahlungen, KooperationenMitglieder
from sqlalchemy.sql import func, case
from project.extensions import db
from graphviz import Graph
from sqlalchemy.orm import aliased

from arbeitszeit.use_cases import purchase_product
from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.purchase_factory import PurchaseFactory
from arbeitszeit import entities


def id_generator(size=10, chars=string.ascii_uppercase + string.digits):
    """generates money-code for withdrawals."""
    return ''.join(random.SystemRandom().choice(chars) for _ in range(size))


def purchase_orm_from_purchase(purchase: entities.Purchase) -> Kaeufe:
    product_offer = product_offer_to_orm(purchase.product_offer)
    return Kaeufe(
        kauf_date=purchase.purchase_date,
        angebot=product_offer.id,
        type_member=isinstance(purchase.buyer, entities.Member),
        company=(
            company_to_orm(purchase.buyer).id
            if isinstance(purchase.buyer, entities.Company)
            else None
        ),
        member=(
            member_to_orm(purchase.buyer).id
            if isinstance(purchase.buyer, entities.Member)
            else None
        ),
        kaufpreis=float(purchase.price),
    )


def company_to_orm(company: entities.Company) -> Company:
    return Company.query.get(company.id)


def company_from_orm(company_orm: Company) -> entities.Company:
    return entities.Company(
        id=company_orm.id,
        change_credit=lambda amount: setattr(company_orm, "guthaben", company_orm.guthaben + amount)
    )


def product_offer_to_orm(product_offer: entities.ProductOffer) -> Angebote:
    return Angebote.query.get(product_offer.id)


def product_offer_from_orm(offer_orm: Angebote) -> entities.ProductOffer:
    return entities.ProductOffer(
        id=offer_orm.id,
        deactivate_offer_in_db=lambda: setattr(offer_orm, "aktiv", False),
    )


def member_to_orm(member: entities.Member) -> Member:
    return Member.query.get(member.id)


def member_from_orm(member: Member) -> entities.Member:
    return entities.Member(
        id=member.id,
        change_credit=lambda amount: setattr(member, "guthaben", member.guthaben + amount),
    )


def lookup_koop_price(product_offer: entities.ProductOffer) -> Decimal:
    return Decimal(
        SearchProducts().get_offer_by_id(product_offer.id).koop_preis
    )


def lookup_product_provider(
    product_offer: entities.ProductOffer
) -> entities.Company:
    company_orm = db.session.query(Company).\
        join(Angebote).filter(Angebote.id == product_offer.id).first()
    return company_from_orm(company_orm)


class SearchProducts():
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
        subq = db.session.query(
            func.avg(Angebote.preis)).\
            select_from(km).\
            join(Angebote, km.mitglied == Angebote.id).\
            filter(Angebote.aktiv == True).\
            filter(km.kooperation == km2.kooperation).\
            group_by(km.kooperation).\
            as_scalar()

        qry = db.session.query(
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
            case([(km2.kooperation == None, Angebote.preis), ], else_=subq).
            label("koop_preis")
            ).\
            select_from(Angebote).\
            join(Company, Angebote.company == Company.id).\
            outerjoin(km2, Angebote.id == km2.mitglied).\
            group_by(
                Company, Angebote.cr_date, "angebot_name",
                Angebote.beschreibung, Angebote.kategorie,
                Angebote.preis, km2.kooperation)

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
            if search_field == 'Name':
                angebote = self.get_offers().filter(
                    Angebote.name.contains(search_string)).\
                    all()

            elif search_field == 'Beschreibung':
                angebote = self.get_offers().filter(
                    Angebote.beschreibung.contains(search_string)).\
                        all()

            elif search_field == 'Kategorie':
                angebote = self.get_offers().filter(
                    Angebote.kategorie.contains(search_string)).\
                        all()
        else:
            angebote = self.get_offers().filter(Angebote.aktiv == True).all()
        return angebote


class CompositionOfPrices():
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

        first_level = db.session.query(
            angebote1.id.label("angebot1"), angebote1.name.label("name1"),
            angebote1.p_kosten.label("p1"),
            angebote1.v_kosten.label("v1"), angebote1.preis.label("preis1"),
            produktionsmittel1.prozent_gebraucht.label("proz_gebr2"),
            produktionsmittel1.kauf.label("kauf2"),
            kaeufe2.angebot.label("angebot2"), angebote2.name.label("name2"),
            angebote2.preis.label("preis2"),
            (angebote2.preis*(produktionsmittel1.prozent_gebraucht/100))
            .label("kosten2"),
            produktionsmittel2.prozent_gebraucht.label("proz_gebr3"),
            produktionsmittel2.kauf.label("kauf3"),
            kaeufe3.angebot.label("angebot3"), angebote3.name.label("name3"),
            angebote3.preis.label("preis3"),
            (angebote3.preis*(produktionsmittel2.prozent_gebraucht/100)).
            label("kosten3"),
            produktionsmittel3.prozent_gebraucht.label("proz_gebr4"),
            produktionsmittel3.kauf.label("kauf4"),
            kaeufe4.angebot.label("angebot4"), angebote4.name.label("name4"),
            angebote4.preis.label("preis4"),
            (angebote4.preis*(produktionsmittel3.prozent_gebraucht/100)).
            label("kosten4"),
            produktionsmittel4.prozent_gebraucht.label("proz_gebr5"),
            produktionsmittel4.kauf.label("kauf5"),
            kaeufe5.angebot.label("angebot5"), angebote5.name.label("name5"),
            angebote5.preis.label("preis5"),
            (angebote5.preis*(produktionsmittel4.prozent_gebraucht/100)).
            label("kosten5"),
            produktionsmittel5.prozent_gebraucht.label("proz_gebr6"),
            produktionsmittel5.kauf.label("kauf6"))\
            .select_from(angebote1).filter(angebote1.id == angebote_id).\
            outerjoin(
                produktionsmittel1, angebote1.id == produktionsmittel1.angebot)

        second_level = first_level.outerjoin(
            kaeufe2, produktionsmittel1.kauf == kaeufe2.id).\
            outerjoin(angebote2, kaeufe2.angebot == angebote2.id).\
            outerjoin(produktionsmittel2,
                      angebote2.id == produktionsmittel2.angebot)

        third_level = second_level.outerjoin(
            kaeufe3, produktionsmittel2.kauf == kaeufe3.id).\
            outerjoin(angebote3, kaeufe3.angebot == angebote3.id).\
            outerjoin(
                produktionsmittel3, angebote3.id == produktionsmittel3.angebot)

        fourth_level = third_level.outerjoin(
            kaeufe4, produktionsmittel3.kauf == kaeufe4.id).\
            outerjoin(angebote4, kaeufe4.angebot == angebote4.id).\
            outerjoin(
                produktionsmittel4, angebote4.id == produktionsmittel4.angebot)

        fifth_level = fourth_level.outerjoin(
            kaeufe5, produktionsmittel4.kauf == kaeufe5.id).\
            outerjoin(angebote5, kaeufe5.angebot == angebote5.id).\
            outerjoin(
                produktionsmittel5, angebote5.id == produktionsmittel5.angebot)

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
        dot = Graph(comment='Graph zur Preiszusammensetzung', format="svg")
        for cnt, col in enumerate(cols_dict):
            if cnt == 0:  # if first column (should be all the same angebot)
                angebot_0 = list(col[0].keys())[0]
                dot.node(
                    f"{angebot_0}_{cnt}",
                    f"{angebot_0}, "
                    f"Preis: {round(table_of_composition[0].preis1, 2)} Std.")
                dot.node(
                    f"{angebot_0}_v_{cnt}",
                    f"Arbeitskraft: \
{round(table_of_composition[0].v1, 2)} Std.")
                dot.edge(f"{angebot_0}_{cnt}", f"{angebot_0}_v_{cnt}")
            else:  # the following columns
                for j in col:
                    current_angebot = list(j.keys())[0]
                    current_position = list(j.values())[0]
                    if cnt == 1:
                        current_kosten = round(
                            table_of_composition[current_position[0]].
                            kosten2, 2)
                        dot.node(
                            f"{current_angebot}_{cnt}",
                            f"{current_angebot}, \
Kosten: {current_kosten} Std.")
                    elif cnt in [2, 3, 4]:
                        dot.node(
                            f"{current_angebot}_{cnt}", f"{current_angebot}")

                    parent_angebote_list = cols_dict[cnt-1]
                    for par in parent_angebote_list:
                        parent_angebot = list(par.keys())[0]
                        parent_positions = list(par.values())[0]
                        for cur_pos in current_position:
                            if cur_pos in parent_positions:
                                # create edge between parent and current node
                                dot.edge(
                                    f"{parent_angebot}_{cnt-1}",
                                    f"{current_angebot}_{cnt}")
                                break  # only one match is enough
        return dot


# Kaufen

def buy(kaufender_type, angebot, kaeufer_id) -> None:
    """
    buy product.
    """
    datetime_service = DatetimeService()
    buyer_model = Company if kaufender_type == "company" else Member
    buyer_orm = db.session.query(buyer_model).filter(buyer_model.id == kaeufer_id).first()
    buyer: Union[entities.Member, entities.Company] = (
        company_from_orm(buyer_orm)
        if kaufender_type == "company"
        else member_from_orm(buyer_orm)
    )

    product_offer = product_offer_from_orm(angebot)
    purchase_factory = PurchaseFactory()
    purchase = purchase_product(
        datetime_service,
        lookup_koop_price,
        lookup_product_provider,
        product_offer,
        buyer,
        purchase_factory,
    )
    # this needs to be executed to create the actual db model
    purchase_orm = purchase_orm_from_purchase(purchase)
    db.session.add(purchase_orm)
    db.session.commit()


# User

def get_user_by_mail(email):
    """returns first user in User, filtered by email."""
    member = Member.query.filter_by(email=email).first()
    return member


def get_user_by_id(id):
    """returns first user in User, filtered by id."""
    member = Member.query.filter_by(id=id).first()
    return member


def add_new_user(email, name, password):
    """
    adds a new user to User.
    """
    new_user = Member(
        email=email,
        name=name,
        password=password)
    db.session.add(new_user)
    db.session.commit()


def get_purchases(user_id):
    """returns all purchases made by user."""
    purchases = db.session.query(
        Kaeufe.id,
        Angebote.name,
        Angebote.beschreibung,
        func.round(Angebote.preis, 2).
        label("preis")
        ).\
        select_from(Kaeufe).\
        filter_by(member=user_id).\
        join(Angebote, Kaeufe.angebot == Angebote.id).\
        all()
    return purchases


def get_workplaces(user_id):
    """returns all workplaces the user is assigned to."""
    workplaces = db.session.query(Company)\
        .select_from(Worker).\
        filter_by(member_id=user_id).\
        join(Company, Worker.company_id == Company.id).\
        all()
    return workplaces


def withdraw(user_id, amount):
    """
    register new withdrawal and withdraw amount from user's account.
    returns code that can be used like money.
    """
    code = id_generator()
    new_withdrawal = Auszahlungen(
        type_member=True,
        member=user_id,
        betrag=amount,
        code=code)
    db.session.add(new_withdrawal)
    db.session.commit()
    return code

    # betrag vom guthaben des users abziehen
    member = db.session.query(Member).\
        filter(Member.id == user_id).\
        first()
    member.guthaben -= amount
    db.session.commit()


# Company

def get_company_by_mail(email):
    """returns first company in Company, filtered by mail."""
    company = Company.query.filter_by(email=email).first()
    return company


def add_new_company(email, name, password):
    """
    adds a new company to Company.
    """
    new_company = Company(
        email=email,
        name=name,
        password=password)
    db.session.add(new_company)
    db.session.commit()


def get_workers(company_id):
    """get all workers working in a company."""
    workers = Worker.query.filter(Worker.company_id == company_id).all()
    return workers


def get_worker_in_company(worker_id, company_id):
    """get specific worker in a company."""
    worker = Worker.query.filter_by(
        member_id=worker_id, company_id=company_id).\
        first()
    return worker


def get_hours_worked(company_id):
    """get all hours worked in a company."""
    hours_worked = db.session.query(
        Member.id, Member.name,
        func.concat(func.sum(Arbeit.stunden), " Std.").
        label('summe_stunden')
        ).select_from(Angebote).\
        filter(Angebote.company == company_id).\
        join(Arbeit).join(Member).group_by(Member.id).\
        order_by(func.sum(Arbeit.stunden).desc()).all()
    return hours_worked


def get_means_of_prod(company_id):
    """
    returns tuple of active and inactive means of prouction of company.
    """
    produktionsmittel_qry = db.session.query(
        Kaeufe.id,
        Angebote.name,
        Angebote.beschreibung,
        func.round(Kaeufe.kaufpreis, 2).
        label("kaufpreis"),
        func.round(
            func.coalesce(
                func.sum(Produktionsmittel.prozent_gebraucht), 0), 2).
        label("prozent_gebraucht"))\
        .select_from(Kaeufe)\
        .filter(Kaeufe.company == company_id).\
        outerjoin(Produktionsmittel,
                  Kaeufe.id == Produktionsmittel.kauf).\
        join(Angebote, Kaeufe.angebot == Angebote.id).\
        group_by(Kaeufe, Angebote, Produktionsmittel.kauf)

    produktionsmittel_aktiv = produktionsmittel_qry.\
        having(func.coalesce(func.sum(Produktionsmittel.prozent_gebraucht).
               label("prozent_gebraucht"), 0).
               label("prozent_gebraucht") < 100).all()
    produktionsmittel_inaktiv = produktionsmittel_qry.\
        having(func.coalesce(func.sum(Produktionsmittel.prozent_gebraucht).
               label("prozent_gebraucht"), 0).
               label("prozent_gebraucht") == 100).all()

    return (produktionsmittel_aktiv, produktionsmittel_inaktiv)


def delete_product(angebot_id):
    """delete product."""
    angebot = Angebote.query.filter_by(id=angebot_id).first()
    angebot.aktiv = False
    db.session.commit()


# Worker

def get_first_worker(betrieb_id):
    """get first worker in Worker."""
    worker = Worker.query.filter_by(company_id=betrieb_id).first()
    return worker


def add_new_worker_to_company(member_id, company_id):
    """
    adds a new worker to Company.
    """
    new_worker = Worker(
        member_id=member_id,
        company_id=company_id)
    db.session.add(new_worker)
    db.session.commit()


# Search Angebote

def get_offer_by_id(id):
    """get first angebot, filtered by id"""
    angebot = db.session.query(Angebote).\
        filter(Angebote.id == id).first()
    return angebot
