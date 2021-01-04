from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from flask_login import login_required, current_user
from flask_table import LinkCol, Col
from . import db
from .models import Angebote, Kaeufe, Betriebe, PMVerbrauchGesamt, PMVerbrauchProdukt
from .forms import ProductSearchForm
from .tables import Results, ProduktionsmittelTable
from decimal import Decimal
from sqlalchemy.sql.functions import coalesce

main_betriebe = Blueprint('main_betriebe', __name__)

@main_betriebe.route('/betriebe/home')
def index():
    try:
        user_type = session["user_type"]
    except:
        user_type = "betrieb"

    if user_type == "nutzer":
        return redirect(url_for('auth.zurueck'))
    else:
        session["user_type"] = "betrieb"
        return render_template('index_betriebe.html')

@main_betriebe.route('/betriebe/profile')
@login_required
def profile():
    user_type = session["user_type"]
    if user_type == "betrieb":
        return render_template('profile_betriebe.html')
    elif user_type == "nutzer":
        return redirect(url_for('auth.zurueck'))


@main_betriebe.route('/betriebe/produktionsmittel')
@login_required
def produktionsmittel():
    produktionsmittel_qry = db.session.query(Kaeufe.id, Angebote.name, Angebote.beschreibung,\
        Angebote.preis, coalesce(PMVerbrauchGesamt.prozent_gebraucht, 0).label("prozent_gebraucht")).\
        outerjoin(Angebote, Kaeufe.angebot==Angebote.id).outerjoin(PMVerbrauchGesamt,\
        Kaeufe.id==PMVerbrauchGesamt.kauf).filter(Kaeufe.betrieb==current_user.id)

    produktionsmittel_aktiv = produktionsmittel_qry.filter(PMVerbrauchGesamt.prozent_gebraucht < 100).all()
    produktionsmittel_inaktiv = produktionsmittel_qry.filter(PMVerbrauchGesamt.prozent_gebraucht == 100).all()

    table_aktiv = ProduktionsmittelTable(produktionsmittel_aktiv, classes=["table", "is-bordered", "is-striped"])
    table_inaktiv = ProduktionsmittelTable(produktionsmittel_inaktiv, classes=["table", "is-bordered", "is-striped"])
    return render_template('produktionsmittel.html', table_aktiv=table_aktiv, table_inaktiv=table_inaktiv)


@main_betriebe.route('/betriebe/suchen', methods=['GET', 'POST'])
@login_required
def suchen():
    search = ProductSearchForm(request.form)
    if request.method == 'POST':
        results = []
        search_string = search.data['search']

        if search_string:
            if search.data['select'] == 'Name':
                qry = db.session.query(Angebote).filter(Angebote.aktiv == True,
                        Angebote.name.contains(search_string))
                results = qry.all()
            elif search.data['select'] == 'Beschreibung':
                qry = db.session.query(Angebote).filter(Angebote.aktiv == True,
                        Angebote.name.contains(search_string))
                results = qry.all()
            else:
                qry = db.session.query(Angebote).filter(Angebote.aktiv == True)
                results = qry.all()
        else:
            qry = db.session.query(Angebote).filter(Angebote.aktiv == True)
            results = qry.all()

        if not results:
            flash('Keine Ergebnisse!')
            return redirect('/nutzer/suchen')
        else:
            table = Results(results, classes=["table", "is-bordered", "is-striped"])
            table.add_column("kaufen", LinkCol("Kaufen", 'main_betriebe.kaufen', url_kwargs=dict(id='id')))
            return render_template('suchen_betriebe.html', form=search, table=table)

    return render_template('suchen_betriebe.html', form=search)



@main_betriebe.route('/betriebe/kaufen/<int:id>', methods=['GET', 'POST'])
def kaufen(id):
    qry = db.session.query(Angebote).filter(
                Angebote.id==id)
    angebot = qry.first()
    if angebot:
        if request.method == 'POST':
            # kauefe aktualisieren
            new_kauf = Kaeufe(angebot = angebot.id,
                    type_nutzer = False, betrieb = current_user.id,
                    nutzer = None)
            db.session.add(new_kauf)
            db.session.commit()
            # angebote aktualisieren (aktiv = False)
            angebot.aktiv = False
            db.session.commit()
            # produktionsmittel (Verbrauch Gesamt) aktualisieren
            new_produktionsmittel = PMVerbrauchGesamt(kauf=new_kauf.id, prozent_gebraucht=0)
            db.session.add(new_produktionsmittel)
            db.session.commit()
            # guthaben self aktualisieren
            betrieb = db.session.query(Betriebe).filter(Betriebe.id == current_user.id).first()
            betrieb.guthaben -= angebot.preis
            db.session.commit()
            # guthaben des arbeiters aktualisieren
            # XX
            flash(f"Kauf von '{angebot.name}' erfolgreich!")
            return redirect('/betriebe/suchen')

        return render_template('kaufen_betriebe.html', angebot=angebot)
    else:
        return 'Error loading #{id}'.format(id=id)



@main_betriebe.route('/betriebe/anbieten', methods=['GET', 'POST'])
@login_required
def neues_angebot():
    """
    Ein neues Angebot hinzufügen
    """
    produktionsmittel_aktiv = db.session.query(Kaeufe.id, Angebote.name, Angebote.beschreibung,\
        Angebote.preis, coalesce(PMVerbrauchGesamt.prozent_gebraucht, 0).label("prozent_gebraucht"), PMVerbrauchGesamt.id).\
        outerjoin(Angebote, Kaeufe.angebot==Angebote.id).outerjoin(PMVerbrauchGesamt,\
        Kaeufe.id==PMVerbrauchGesamt.kauf).filter(Kaeufe.betrieb==current_user.id, PMVerbrauchGesamt.prozent_gebraucht < 100).all()

    if request.method == 'POST':
        # create request dictionary
        request_dict = request.form.to_dict()
        # dict with produktionsmittel values
        pm_dict = dict(filter(lambda elem: elem[0][:3] == 'id_', request_dict.items()))
        # pm dict entries that are not zero
        pm_dict_not_zero = dict(filter(lambda elem: Decimal(elem[1]) != 0,pm_dict.items()))
        kosten_pm = 0
        if pm_dict_not_zero:
            # calculate produktionsmittelkosten
            id_list = []
            prozent_list = []
            for key in list(pm_dict_not_zero.keys()):
                id_list.append(key[3:])
            for value in list(pm_dict_not_zero.values()):
                prozent_list.append(Decimal(value)/100)
            # preise
            preise_list = []
            for idx in id_list:
                qry = db.session.query(Kaeufe, Angebote.preis).join(Angebote, Kaeufe.angebot==Angebote.id).filter(Kaeufe.id == idx).all()
                preise_list.append(Decimal(qry[0][1]))
            kosten_einzeln = []
            for num1, num2 in zip(prozent_list, preise_list):
                kosten_einzeln.append(num1 * num2)
            kosten_pm = sum(kosten_einzeln)
            # update prodmittel gebraucht (gesamt) in prozent
            assert len(id_list) == len(prozent_list)
            for count, i in enumerate(id_list):
                prdmittel = db.session.query(PMVerbrauchGesamt).filter(PMVerbrauchGesamt.kauf == i).first()
                prdmittel.prozent_gebraucht += prozent_list[count]*100
                db.session.commit()
                print("prozent_gebraucht gesamt updated!")

        # save new angebot
        new_angebot = Angebote(name=request.form["name"], betrieb=current_user.id,\
            beschreibung=request.form["beschreibung"], preis=Decimal(request.form["arbeit"]) + kosten_pm)
        db.session.add(new_angebot)
        db.session.commit()

        if pm_dict_not_zero:
            # create prdmittel gebraucht (Produkt) in prozent
            assert len(id_list) == len(prozent_list)
            for count, i in enumerate(id_list):
                new_produktionsmittel_prd = PMVerbrauchProdukt(angebot=new_angebot.id, kauf=i, prozent_gebraucht=prozent_list[count]*100)
                db.session.add(new_produktionsmittel_prd)
                db.session.commit()

        flash('Angebot erfolgreich gespeichert!')
        return redirect('/betriebe/home')

    return render_template('neues_angebot.html', produktionsmittel_aktiv=produktionsmittel_aktiv)
