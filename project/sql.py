from .models import Nutzer, Betriebe, Arbeiter, Angebote, Arbeit,\
    Produktionsmittel, Kaeufe
from sqlalchemy.sql import func
from .extensions import db


# User

def get_user_by_mail(email):
    """returns first user in User, filtered by email."""
    nutzer = Nutzer.query.filter_by(email=email).first()
    return nutzer


def get_user_by_id(id):
    """returns first user in User, filtered by id."""
    nutzer = Nutzer.query.filter_by(id=id).first()
    return nutzer


def add_new_user(email, name, password):
    """
    adds a new user to User.
    """
    new_user = Nutzer(
        email=email,
        name=name,
        password=password)
    db.session.add(new_user)
    db.session.commit()


# Company

def get_company_by_mail(email):
    """returns first company in Company, filtered by mail."""
    betrieb = Betriebe.query.filter_by(email=email).first()
    return betrieb


def add_new_company(email, name, password):
    """
    adds a new company to Company.
    """
    new_company = Betriebe(
        email=email,
        name=name,
        password=password)
    db.session.add(new_company)
    db.session.commit()


def get_workers(betrieb_id):
    """get all workers working in a company."""
    workers = db.session.query(Nutzer.id, Nutzer.name).\
        select_from(Arbeiter).join(Nutzer).\
        filter(Arbeiter.betrieb == betrieb_id).group_by(Nutzer.id).all()
    return workers


def get_worker_in_company(worker_id, company_id):
    """get specific worker in a company."""
    arbeiter = Arbeiter.query.filter_by(
        nutzer=worker_id, betrieb=company_id).\
        first()
    return arbeiter


def get_hours_worked(betrieb_id):
    """get all hours worked in a company."""
    hours_worked = db.session.query(
        Nutzer.id, Nutzer.name,
        func.concat(func.sum(Arbeit.stunden), " Std.").
        label('summe_stunden')
        ).select_from(Angebote).\
        filter(Angebote.betrieb == betrieb_id).\
        join(Arbeit).join(Nutzer).group_by(Nutzer.id).\
        order_by(func.sum(Arbeit.stunden).desc()).all()
    return hours_worked


# Worker

def get_worker_first(betrieb_id):
    """get first worker in Worker."""
    worker = Arbeiter.query.filter_by(betrieb=betrieb_id).first()
    return worker


def add_new_worker_to_company(nutzer_id, betrieb_id):
    """
    adds a new worker to Company.
    """
    new_worker = Arbeiter(
        nutzer=nutzer_id,
        betrieb=betrieb_id)
    db.session.add(new_worker)
    db.session.commit()


# Means of production

def get_means_of_prod(betrieb_id):
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
        .filter(Kaeufe.betrieb == betrieb_id).\
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


# Angebote

def get_angebot_by_id(id):
    """get first angebot, filtered by id"""
    angebot = db.session.query(Angebote).\
        filter(Angebote.id == id).first()
    return angebot
