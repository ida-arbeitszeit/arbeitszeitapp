from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from flask_login import login_required, current_user
from flask_table import LinkCol
from . import db
from .models import Angebote, Kaeufe, Nutzer, Betriebe, Arbeit
from .forms import ProductSearchForm

main_nutzer = Blueprint('main_nutzer', __name__)


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


@main_nutzer.route('/nutzer/suchen', methods=['GET', 'POST'])
@login_required
def suchen():
    search = ProductSearchForm(request.form)
    if request.method == 'POST':
        results = []
        search_string = search.data['search']

        if search_string:
            if search.data['select'] == 'Name':
                qry = db.session.query(Angebote.id, Angebote.name, Betriebe.name, Betriebe.email,\
                    Angebote.beschreibung, Angebote.kategorie, Angebote.preis).select_from(Angebote).\
                    join(Betriebe, Angebote.betrieb==Betriebe.id).filter(Angebote.aktiv == True,\
                    Angebote.name.contains(search_string)).\
                    order_by(Angebote.id)
                results = qry.all()

            elif search.data['select'] == 'Beschreibung':
                qry = db.session.query(Angebote.id, Angebote.name, Betriebe.name, Betriebe.email,\
                    Angebote.beschreibung, Angebote.kategorie, Angebote.preis).select_from(Angebote).\
                    join(Betriebe, Angebote.betrieb==Betriebe.id).filter(Angebote.aktiv == True,\
                    Angebote.beschreibung.contains(search_string)).\
                    order_by(Angebote.id)
                results = qry.all()

            elif search.data['select'] == 'Kategorie':
                qry = db.session.query(Angebote.id, Angebote.name, Betriebe.name, Betriebe.email,\
                    Angebote.beschreibung, Angebote.kategorie, Angebote.preis).select_from(Angebote).\
                    join(Betriebe, Angebote.betrieb==Betriebe.id).filter(Angebote.aktiv == True,\
                    Angebote.kategorie.contains(search_string)).\
                    order_by(Angebote.id)
                results = qry.all()

            else:
                qry = db.session.query(Angebote.id, Angebote.name, Betriebe.name, Betriebe.email,\
                    Angebote.beschreibung, Angebote.kategorie, Angebote.preis).select_from(Angebote).\
                    join(Betriebe, Angebote.betrieb==Betriebe.id).filter(Angebote.aktiv == True).\
                    order_by(Angebote.id)
                results = qry.all()
        else:
            qry = db.session.query(Angebote.id, Angebote.name, Betriebe.name, Betriebe.email,\
                Angebote.beschreibung, Angebote.kategorie, Angebote.preis).select_from(Angebote).\
                join(Betriebe, Angebote.betrieb==Betriebe.id).filter(Angebote.aktiv == True).\
                order_by(Angebote.id)
            results = qry.all()

        if not results:
            flash('Keine Ergebnisse!')
            return redirect('/nutzer/suchen')
        else:
            return render_template('suchen_nutzer.html', form=search, results=results)

    return render_template('suchen_nutzer.html', form=search)


@main_nutzer.route('/nutzer/kaufen/<int:id>', methods=['GET', 'POST'])
def kaufen(id):
    qry = db.session.query(Angebote).filter(
                Angebote.id==id)
    angebot = qry.first()
    if angebot:
        if request.method == 'POST':
            # kauefe aktualisieren
            new_kauf = Kaeufe(angebot = angebot.id,
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
        return render_template('profile_nutzer.html')
    elif user_type == "betrieb":
        return redirect(url_for('auth.zurueck'))
