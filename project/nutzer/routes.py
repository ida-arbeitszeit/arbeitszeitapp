from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from flask_login import login_required, current_user
from .. import db
from ..models import Angebote, Kaeufe, Nutzer, Betriebe, Arbeit, Arbeiter, Auszahlungen
from ..forms import ProductSearchForm
from ..tables import KaeufeTable, ArbeitsstellenTable, Preiszusammensetzung
from ..composition_of_prices import get_table_of_composition, get_positions_in_table, create_dots
from sqlalchemy.sql import func
import datetime
import string
import random


main_nutzer = Blueprint('main_nutzer', __name__, template_folder='templates',
    static_folder='static')


def id_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.SystemRandom().choice(chars) for _ in range(size))


@main_nutzer.route('/nutzer/home')
def index():
    try:
        user_type = session["user_type"]
    except:
        user_type = "nutzer"

    if user_type == "betrieb":
        return redirect(url_for('auth.zurueck'))
    else:
        session["user_type"] = "nutzer"
        return render_template('index_nutzer.html')


@main_nutzer.route('/nutzer/kaeufe')
@login_required
def meine_kaeufe():
    try:
        user_type = session["user_type"]
    except:
        user_type = "nutzer"

    if user_type == "betrieb":
        return redirect(url_for('auth.zurueck'))
    else:
        session["user_type"] = "nutzer"

        kaufhistorie = db.session.query(Kaeufe.id, Angebote.name, Angebote.beschreibung,\
            func.concat(func.round(Angebote.preis, 2), " Std.").label("preis")
            ).\
            select_from(Kaeufe).\
            filter_by(nutzer=current_user.id).\
            join(Angebote, Kaeufe.angebot==Angebote.id).all()
        kaufh_table = KaeufeTable(kaufhistorie, no_items="(Noch keine Käufe.)")
        return render_template('meine_kaeufe.html', kaufh_table=kaufh_table)


@main_nutzer.route('/nutzer/suchen', methods=['GET', 'POST'])
@login_required
def suchen():
    search = ProductSearchForm(request.form)
    # grouping by all kind of attributes of angebote, aggregating ID with min() --> only
    # 1 angebot of the same kind is shown.
    qry = db.session.query(func.min(Angebote.id).label("id"), Angebote.name.label("angebot_name"),\
        Betriebe.name.label("betrieb_name"), Betriebe.email,\
        Angebote.beschreibung, Angebote.kategorie, Angebote.preis,
        func.count(Angebote.id).label("vorhanden")).select_from(Angebote).\
        join(Betriebe, Angebote.betrieb==Betriebe.id).filter(Angebote.aktiv == True).\
        group_by(Angebote.cr_date, "angebot_name", "betrieb_name",
            Betriebe.email, Angebote.beschreibung, Angebote.kategorie, Angebote.preis)
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
            return redirect('/nutzer/suchen')
        else:
            return render_template('suchen_nutzer.html', form=search, results=results)

    return render_template('suchen_nutzer.html', form=search, results=results)


@main_nutzer.route('/nutzer/details/<int:id>', methods=['GET', 'POST'])
def details(id):

    table_of_composition =  get_table_of_composition(id)
    cols_dict = get_positions_in_table(table_of_composition)
    dot = create_dots(cols_dict, table_of_composition)
    piped = dot.pipe().decode('utf-8')
    table_preiszus = Preiszusammensetzung(table_of_composition)

    if request.method == 'POST':
        return redirect('/nutzer/suchen')

    return render_template('details_nutzer.html', table_preiszus=table_preiszus, piped=piped)


@main_nutzer.route('/nutzer/kaufen/<int:id>', methods=['GET', 'POST'])
def kaufen(id):
    qry = db.session.query(Angebote).filter(
                Angebote.id==id)
    angebot = qry.first()
    if angebot:
        if request.method == 'POST':
            # kauefe aktualisieren
            new_kauf = Kaeufe(kauf_date = datetime.datetime.now(), angebot = angebot.id,
                    type_nutzer = True, betrieb = None,
                    nutzer = current_user.id)
            db.session.add(new_kauf)
            db.session.commit()
            # angebote aktualisieren (aktiv = False)
            angebot.aktiv = False
            db.session.commit()
            # guthaben self aktualisieren
            nutzer = db.session.query(Nutzer).filter(Nutzer.id == current_user.id).first()
            nutzer.guthaben -= angebot.preis
            db.session.commit()

            # guthaben des arbeiters erhöhen, wenn ausbezahlt = false
            arbeit_in_produkt = Arbeit.query.filter_by(angebot=angebot.id, ausbezahlt=False).all()
            for arb in arbeit_in_produkt:
                Nutzer.query.filter_by(id=arb.nutzer).first().guthaben += arb.stunden
                arb.ausbezahlt = True
                db.session.commit()

            # guthaben des anbietenden betriebes erhöhen
            anbietender_betrieb_id = angebot.betrieb
            anbietender_betrieb = Betriebe.query.filter_by(id=anbietender_betrieb_id).first()
            anbietender_betrieb.guthaben += angebot.preis

            # guthaben des anbietenden betriebes verringern, wenn ausbezahlt = false
            for arb in arbeit_in_produkt:
                anbietender_betrieb.guthaben -= arb.stunden
                db.session.commit()

            flash(f"Kauf von '{angebot.name}' erfolgreich!")
            return redirect('/nutzer/suchen')

        return render_template('kaufen_nutzer.html', angebot=angebot)
    else:
        return 'Error loading #{id}'.format(id=id)


@main_nutzer.route('/nutzer/profile')
@login_required
def profile():
    user_type = session["user_type"]
    if user_type == "nutzer":
        arbeitsstellen = db.session.query(Betriebe.name).select_from(Arbeiter).\
            filter_by(nutzer=current_user.id).join(Betriebe, Arbeiter.betrieb==Betriebe.id).all()
        if arbeitsstellen:
            arbeitsstellen_table = ArbeitsstellenTable(arbeitsstellen)
        else:
            arbeitsstellen_table = None

        return render_template('profile_nutzer.html', arbeitsstellen_table=arbeitsstellen_table)
    elif user_type == "betrieb":
        return redirect(url_for('auth.zurueck'))

@main_nutzer.route('/nutzer/auszahlung', methods=['GET', 'POST'])
@login_required
def auszahlung():
    if request.method == 'POST':

        betrag = request.form["betrag"]
        code = id_generator()

        # neuer eintrag in db-table auszahlungen
        neue_auszahlung = Auszahlungen(nutzer=current_user.id, betrag=betrag, code=code)
        db.session.add(neue_auszahlung)
        db.session.commit()

        # betrag vom guthaben des users abziehen

        # Code User anzeigen

        # Einlösen und Entwertung des Codes ermöglichen (hier und beim Verkäufer)

        # implement Auszahlung for betriebe?!
        
        return render_template('auszahlung_nutzer.html')

    return render_template('auszahlung_nutzer.html')

@main_nutzer.route('/nutzer/hilfe')
@login_required
def hilfe():
    return render_template('nutzer_hilfe.html')
