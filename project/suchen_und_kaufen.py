"""SQL-requests around searching and buying products."""

import datetime
from flask import render_template, redirect, request, flash
from . import db
from .forms import ProductSearchForm
from .models import Angebote, Betriebe, KooperationenMitglieder, Nutzer, Kaeufe
from sqlalchemy.sql import func, case
from sqlalchemy.orm import aliased


def get_angebote():
    """
    search products.

    returns all products available (grouped results, active or not),
    with several columns, including the coop-price.
    """

    km = aliased(KooperationenMitglieder)
    km2 = aliased(KooperationenMitglieder)

    # AS_SCALAR, NOT SUBQUERY!
    subq = db.session.query(func.avg(Angebote.preis)).\
        select_from(km).\
        join(Angebote, km.mitglied == Angebote.id).\
        filter(Angebote.aktiv == True).\
        filter(km.kooperation == km2.kooperation).\
        group_by(km.kooperation).as_scalar()

    qry = db.session.query(
        func.min(Angebote.id).label("id"),
        Angebote.name.label("angebot_name"),
        func.min(Angebote.p_kosten).label("p_kosten"),
        func.min(Angebote.v_kosten).label("v_kosten"),
        Betriebe.name.label("betrieb_name"),
        Betriebe.id.label("betrieb_id"), Betriebe.email,
        Angebote.beschreibung, Angebote.kategorie, Angebote.preis,
        func.count(Angebote.id).label("vorhanden"), km2.kooperation,
        case([(km2.kooperation == None, Angebote.preis), ], else_=subq).
        label("koop_preis")
        ).\
        select_from(Angebote).\
        join(Betriebe, Angebote.betrieb == Betriebe.id).\
        outerjoin(km2, Angebote.id == km2.mitglied).\
        group_by(
            Betriebe, Angebote.cr_date, "angebot_name",
            Angebote.beschreibung, Angebote.kategorie,
            Angebote.preis, km2.kooperation)

    return qry


def such_vorgang(suchender_type, request_form):
    """
    search products.

    returns html pages with search results
    """

    if suchender_type == "betriebe":
        redirect_dir = '/betriebe/suchen'
        render_dir = 'suchen_betriebe.html'
    elif suchender_type == "nutzer":
        redirect_dir = '/nutzer/suchen'
        render_dir = 'suchen_nutzer.html'

    search = ProductSearchForm(request_form)

    qry = get_angebote().filter(Angebote.aktiv == True)
    results = qry.all()

    if request.method == 'POST':
        results = []
        search_string = search.data['search']

        if search_string:
            if search.data['select'] == 'Name':
                results = qry.filter(Angebote.name.contains(search_string)).\
                    all()

            elif search.data['select'] == 'Beschreibung':
                results = qry.filter(
                    Angebote.beschreibung.contains(search_string)).\
                        all()

            elif search.data['select'] == 'Kategorie':
                results = qry.filter(
                    Angebote.kategorie.contains(search_string)).\
                        all()

            else:
                results = qry.all()
        else:
            results = qry.all()

        if not results:
            flash('Keine Ergebnisse!')
            return redirect(redirect_dir)
        else:
            return render_template(render_dir, form=search, results=results)

    return render_template(render_dir, form=search, results=results)


def kauf_vorgang(kaufender_type, angebot, kaeufer_id):
    """
    buy product.
    """
    # aktuellen (koop-)preis erhalten:
    koop = db.session.query(KooperationenMitglieder).join(Angebote).\
        filter(Angebote.id == angebot.id, Angebote.aktiv == angebot.aktiv).\
        first()
    if not koop:
        preis = angebot.preis
    else:
        preis = db.session.query(func.avg(Angebote.preis)).\
            select_from(KooperationenMitglieder).\
            join(Angebote).\
            filter(Angebote.aktiv == True).\
            filter(KooperationenMitglieder.kooperation == koop.kooperation).\
            group_by(KooperationenMitglieder.kooperation).scalar()

    # kauefe aktualisieren
    if kaufender_type == "betriebe":
        kaufender = Betriebe
        new_kauf = Kaeufe(kauf_date=datetime.datetime.now(),
                          angebot=angebot.id,
                          type_nutzer=False, betrieb=kaeufer_id,
                          nutzer=None, kaufpreis=preis)
        db.session.add(new_kauf)
        db.session.commit()
    elif kaufender_type == "nutzer":
        kaufender = Nutzer
        new_kauf = Kaeufe(kauf_date=datetime.datetime.now(),
                          angebot=angebot.id,
                          type_nutzer=True, betrieb=None,
                          nutzer=kaeufer_id, kaufpreis=preis)
        db.session.add(new_kauf)
        db.session.commit()

    # angebote aktiv = False
    angebot.aktiv = False
    db.session.commit()

    # guthaben käufer verringern
    kaeufer = db.session.query(kaufender).\
        filter(kaufender.id == kaeufer_id).first()
    kaeufer.guthaben -= preis
    db.session.commit()

    # guthaben des anbietenden betriebes erhöhen
    anbietender_betrieb_id = angebot.betrieb
    anbietender_betrieb = Betriebe.query.filter_by(
        id=anbietender_betrieb_id).first()
    anbietender_betrieb.guthaben += preis  # angebot.p_kosten
    db.session.commit()
