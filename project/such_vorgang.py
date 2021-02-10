from .forms import ProductSearchForm
from .models import Angebote, Betriebe, KooperationenMitglieder
from . import db
from sqlalchemy import text
from sqlalchemy.sql import func, case
from sqlalchemy.orm import aliased
from flask import render_template, redirect, request, flash


def such_vorgang(suchender_type, request_form):
    if suchender_type == "betriebe":
        redirect_dir = '/betriebe/suchen'
        render_dir = 'suchen_betriebe.html'
    elif suchender_type == "nutzer":
        redirect_dir = '/nutzer/suchen'
        render_dir = 'suchen_nutzer.html'

    search = ProductSearchForm(request_form)

    # grouping by all kind of attributes of angebote, aggregating ID with min() --> only
    # 1 angebot of the same kind is shown.

    # qry = db.session.query(func.min(Angebote.id).label("id"), Angebote.name.label("angebot_name"),\
    #     Betriebe.name.label("betrieb_name"), Betriebe.email,\
    #     Angebote.beschreibung, Angebote.kategorie, Angebote.preis,
    #     func.count(Angebote.id).label("vorhanden"), KooperationenMitglieder.kooperation).\
    #     select_from(Angebote).\
    #     join(Betriebe, Angebote.betrieb==Betriebe.id).\
    #     outerjoin(KooperationenMitglieder, Angebote.id==KooperationenMitglieder.mitglied).\
    #     filter(Angebote.aktiv == True).\
    #     group_by(Angebote.cr_date, "angebot_name", "betrieb_name",
    #         Betriebe.email, Angebote.beschreibung, Angebote.kategorie,
    #         Angebote.preis, KooperationenMitglieder.kooperation)
    # results = qry.all()


    km = aliased(KooperationenMitglieder)
    km2 = aliased(KooperationenMitglieder)

    # AS_SCALAR, NOT SUBQUERY!
    subq = db.session.query(func.avg(Angebote.preis)).\
        select_from(km).\
        join(Angebote, km.mitglied == Angebote.id).\
        filter(Angebote.aktiv == True).\
        filter(km.kooperation == km2.kooperation).\
        group_by(km.kooperation).as_scalar()

    qry = db.session.query\
        (
        func.min(Angebote.id).label("id"), Angebote.name.label("angebot_name"),\
        Betriebe.name.label("betrieb_name"), Betriebe.email,\
        Angebote.beschreibung, Angebote.kategorie, Angebote.preis,
        func.count(Angebote.id).label("vorhanden"), km2.kooperation,
        case([(km2.kooperation == None, Angebote.preis),],
            else_ = subq).label("koop_preis")
        ).\
        select_from(Angebote).\
        join(Betriebe, Angebote.betrieb==Betriebe.id).\
        outerjoin(km2, Angebote.id==km2.mitglied).\
        filter(Angebote.aktiv == True).\
        group_by(Angebote.cr_date, "angebot_name", "betrieb_name",
            Betriebe.email, Angebote.beschreibung, Angebote.kategorie,
            Angebote.preis, km2.kooperation)

    results = qry.all()

    if request.method == 'POST':
        results = []
        search_string = search.data['search']

        if search_string:
            if search.data['select'] == 'Name':
                results = qry.filter(Angebote.name.contains(search_string)).all()

            elif search.data['select'] == 'Beschreibung':
                results = qry.filter(Angebote.beschreibung.contains(search_string)).all()

            elif search.data['select'] == 'Kategorie':
                results = qry.filter(Angebote.kategorie.contains(search_string)).all()

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
