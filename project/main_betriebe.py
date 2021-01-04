from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from flask_login import login_required, current_user
from flask_table import LinkCol, Col
from . import db
from .models import Angebote, Kaeufe, Betriebe, Produktionsmittel
from .forms import ProductSearchForm, ProductForm
from .tables import Results, ProduktionsmittelTable, ProduktionsmittelTable2
from decimal import Decimal

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
    produktionsmittel = db.session.execute(
        "select kaeufe.id, angebote.name, angebote.beschreibung, angebote.preis,\
        COALESCE(produktionsmittel.prozent_gebraucht, 0) prozent_gebraucht from kaeufe left join\
        angebote on kaeufe.angebot=angebote.id left join produktionsmittel\
        on kaeufe.id=produktionsmittel.kauf where kaeufe.betrieb=:param;", {"param":current_user.id}
        )

    table = ProduktionsmittelTable(produktionsmittel, classes=["table", "is-bordered", "is-striped"])
    return render_template('produktionsmittel.html', table=table)


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
            # produktionsmittel aktualisieren
            new_produktionsmittel = Produktionsmittel(angebot=angebot.id,
                    kauf=new_kauf.id, prozent_gebraucht=0)
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



def save_changes(angebot, form, kosten_pm, new=False):
    """
    Save the changes to the database
    """
    angebot.name = form.name.data
    angebot.betrieb = current_user.id
    angebot.beschreibung = form.beschreibung.data
    angebot.preis = Decimal(form.arbeit.data) + kosten_pm

    if new:
        db.session.add(angebot)

    db.session.commit()


@main_betriebe.route('/betriebe/anbieten', methods=['GET', 'POST'])
@login_required
def neues_angebot():
    """
    Ein neues Angebot hinzufügen
    """
    form = ProductForm(request.form)


    if request.method == 'POST' and form.validate():
        angebot = Angebote()

        # create request dictionary
        request_dict = request.form.to_dict()
        print(request_dict)
        # dict with produktionsmittel values
        pm_dict = dict(filter(lambda elem: elem[0][:3] == 'id_', request_dict.items()))
        # pm dict entries that are not zero
        pm_dict_not_zero = dict(filter(lambda elem: Decimal(elem[1]) != 0,pm_dict.items()))
        if pm_dict_not_zero:
            # get list of ids, prozente
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
            print("id_list", id_list)
            print("prozent_list", prozent_list)
            print("preise_list", preise_list)
            kosten_einzeln = []
            for num1, num2 in zip(prozent_list, preise_list):
                kosten_einzeln.append(num1 * num2)
            print("einzelne kosten:", kosten_einzeln)
            kosten_pm = sum(kosten_einzeln)
            print("kosten_gesamt", kosten_pm)

            # Prozent_Gebraucht anpassen!
            # wenn prozent_gebraucht == 100 --> aus produktionsmittelansicht ausschließen



        save_changes(angebot, form, kosten_pm, new=True)
        flash('Angebot erfolgreich gespeichert!')
        return redirect('/betriebe/home')


    produktionsmittel = db.session.execute(
        "select kaeufe.id, angebote.name, angebote.beschreibung, angebote.preis,\
        COALESCE(produktionsmittel.prozent_gebraucht, 0) prozent_gebraucht from kaeufe left join\
        angebote on kaeufe.angebot=angebote.id left join produktionsmittel\
        on kaeufe.id=produktionsmittel.kauf where kaeufe.betrieb=:param;", {"param":current_user.id}
        )

    # creates dict out of resultproxy
    d, a = {}, []
    for rowproxy in produktionsmittel:
        # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
        for column, value in rowproxy.items():
            # build up the dictionary
            d = {**d, **{column: value}}
        a.append(d)

    # creates list of [names, prozent, preis, kaeufe-id]
    produkt_mittel_names = []
    for item in a:
        # produkt_mittel_names.append([item["name"], item["prozent_gebraucht"], item["preis"], item["id"]])
        produkt_mittel_names.append([item["id"], item["name"], item["beschreibung"], item["preis"], item["prozent_gebraucht"]])
    return render_template('neues_angebot.html', form=form, produkt_mittel_names=produkt_mittel_names)
