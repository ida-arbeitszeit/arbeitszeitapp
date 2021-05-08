import string
import random
from decimal import Decimal
from flask import Blueprint, render_template, session,\
    redirect, url_for, request, flash
from flask_login import login_required, current_user
from ..extensions import db
from ..models import Angebote, Kaeufe, Nutzer,\
    Betriebe, Arbeiter, Auszahlungen
from ..tables import KaeufeTable, Preiszusammensetzung
from .. import composition_of_prices
from .. import suchen_und_kaufen
from sqlalchemy.sql import func


main_nutzer = Blueprint(
    'main_nutzer', __name__, template_folder='templates',
    static_folder='static'
    )


def id_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.SystemRandom().choice(chars) for _ in range(size))


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

        kaufhistorie = db.session.query(
            Kaeufe.id, Angebote.name, Angebote.beschreibung,
            func.concat(func.round(Angebote.preis, 2), " Std.").
            label("preis")
            ).\
            select_from(Kaeufe).\
            filter_by(nutzer=current_user.id).\
            join(Angebote, Kaeufe.angebot == Angebote.id).\
            all()
        kaufh_table = KaeufeTable(kaufhistorie, no_items="(Noch keine Käufe.)")
        return render_template('meine_kaeufe.html', kaufh_table=kaufh_table)


@main_nutzer.route('/nutzer/suchen', methods=['GET', 'POST'])
@login_required
def suchen():
    return suchen_und_kaufen.such_vorgang("nutzer", request.form)


@main_nutzer.route('/nutzer/details/<int:id>', methods=['GET', 'POST'])
@login_required
def details(id):
    """show details of selected product."""
    table_of_composition = composition_of_prices.get_table_of_composition(id)
    cols_dict = composition_of_prices.\
        get_positions_in_table(table_of_composition)
    dot = composition_of_prices.create_dots(cols_dict, table_of_composition)
    piped = dot.pipe().decode('utf-8')
    table_preiszus = Preiszusammensetzung(table_of_composition)
    angebot_ = suchen_und_kaufen.get_angebote().filter(Angebote.id == id).one()
    preise = (angebot_.preis, angebot_.koop_preis)

    if request.method == 'POST':
        return redirect('/nutzer/suchen')

    return render_template(
        'details_nutzer.html',
        table_preiszus=table_preiszus,
        piped=piped,
        preise=preise)


@main_nutzer.route('/nutzer/kaufen/<int:id>', methods=['GET', 'POST'])
@login_required
def kaufen(id):
    qry = db.session.query(Angebote).filter(
                Angebote.id == id)
    angebot = qry.first()
    if angebot:
        if request.method == 'POST':
            suchen_und_kaufen.kauf_vorgang(
                kaufender_type="nutzer", angebot=angebot,
                kaeufer_id=current_user.id)
            flash(f"Kauf von '{angebot.name}' erfolgreich!")
            return redirect('/nutzer/suchen')

        angebot = suchen_und_kaufen.get_angebote().\
            filter(Angebote.aktiv == True, Angebote.id == id).first()
        return render_template('kaufen_nutzer.html', angebot=angebot)
    else:
        return 'Error loading #{id}'.format(id=id)


@main_nutzer.route('/nutzer/profile')
@login_required
def profile():
    user_type = session["user_type"]
    if user_type == "nutzer":
        arbeitsstellen = db.session.query(Betriebe).select_from(Arbeiter).\
            filter_by(nutzer=current_user.id).\
            join(Betriebe, Arbeiter.betrieb == Betriebe.id).all()

        return render_template('profile_nutzer.html',
                               arbeitsstellen=arbeitsstellen)
    elif user_type == "betrieb":
        return redirect(url_for('auth.zurueck'))


@main_nutzer.route('/nutzer/auszahlung', methods=['GET', 'POST'])
@login_required
def auszahlung():
    if request.method == 'POST':

        betrag = Decimal(request.form["betrag"])
        code = id_generator()

        # neuer eintrag in db-table auszahlungen
        neue_auszahlung = Auszahlungen(
            type_nutzer=True, nutzer=current_user.id, betrag=betrag, code=code)
        db.session.add(neue_auszahlung)
        db.session.commit()

        # betrag vom guthaben des users abziehen
        nutzer = db.session.query(Nutzer).\
            filter(Nutzer.id == current_user.id).\
            first()
        nutzer.guthaben -= betrag
        db.session.commit()

        # Code User anzeigen
        flash(betrag)
        flash(code)

        # Einlösen des Codes auch hier ermöglichen

        return render_template('auszahlung_nutzer.html')

    return render_template('auszahlung_nutzer.html')


@main_nutzer.route('/nutzer/hilfe')
@login_required
def hilfe():
    return render_template('nutzer_hilfe.html')
