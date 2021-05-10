import string
import random
from decimal import Decimal
from flask import Blueprint, render_template, session,\
    redirect, url_for, request, flash
from flask_login import login_required, current_user
from ..tables import KaeufeTable, Preiszusammensetzung
from ..forms import ProductSearchForm
from .. import sql


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

        purchases = sql.get_purchases(current_user.id)
        kaufh_table = KaeufeTable(purchases, no_items="(Noch keine Käufe.)")
        return render_template('meine_kaeufe.html', kaufh_table=kaufh_table)


@main_nutzer.route('/nutzer/suchen', methods=['GET', 'POST'])
@login_required
def suchen():
    """search products in catalog."""
    search_form = ProductSearchForm(request.form)
    srch = sql.SearchProducts()
    results = srch.get_angebote_aktiv()

    if request.method == 'POST':
        results = []
        search_string = search_form.data['search']
        search_field = search_form.data['select']  # Name, Beschr., Kategorie

        if search_string:
            results = srch.get_angebote_aktiv(search_string, search_field)
        else:
            results = srch.get_angebote_aktiv()

        if not results:
            flash('Keine Ergebnisse!')
        else:
            return render_template(
                'suchen_nutzer.html', form=search_form, results=results)

    return render_template(
        'suchen_nutzer.html', form=search_form, results=results)


@main_nutzer.route('/nutzer/details/<int:id>', methods=['GET', 'POST'])
@login_required
def details(id):
    """show details of selected product."""
    comp = sql.CompositionOfPrices()
    table_of_composition = comp.get_table_of_composition(id)
    cols_dict = comp.get_positions_in_table(table_of_composition)
    dot = comp.create_dots(cols_dict, table_of_composition)
    piped = dot.pipe().decode('utf-8')
    table_preiszus = Preiszusammensetzung(table_of_composition)
    srch = sql.SearchProducts()
    angebot_ = srch.get_angebot_by_id(id)
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
    srch = sql.SearchProducts()
    angebot = srch.get_angebot_by_id(id)
    if request.method == 'POST':  # if user buys
        sql.kaufen(
            kaufender_type="nutzer",
            angebot=sql.get_angebot_by_id(id),
            kaeufer_id=current_user.id)
        flash(f"Kauf von '{angebot.angebot_name}' erfolgreich!")
        return redirect('/nutzer/suchen')

    return render_template('kaufen_nutzer.html', angebot=angebot)


@main_nutzer.route('/nutzer/profile')
@login_required
def profile():
    user_type = session["user_type"]
    if user_type == "nutzer":
        workplaces = sql.get_workplaces(current_user.id)
        return render_template('profile_nutzer.html',
                               arbeitsstellen=workplaces)
    elif user_type == "betrieb":
        return redirect(url_for('auth.zurueck'))


@main_nutzer.route('/nutzer/auszahlung', methods=['GET', 'POST'])
@login_required
def auszahlung():
    if request.method == 'POST':
        amount = Decimal(request.form["betrag"])
        code = id_generator()
        sql.new_withdrawal(current_user.id, amount, code)
        # Show code to user
        flash(amount)
        flash(code)
        return render_template('auszahlung_nutzer.html')

    return render_template('auszahlung_nutzer.html')


@main_nutzer.route('/nutzer/hilfe')
@login_required
def hilfe():
    return render_template('nutzer_hilfe.html')
