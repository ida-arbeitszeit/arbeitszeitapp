from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from flask_login import login_required, current_user
from .. import db
from ..models import Angebote, Kaeufe, Betriebe, Nutzer, Produktionsmittel, Arbeit, Arbeiter
from ..forms import ProductSearchForm
from ..tables import ProduktionsmittelTable, ArbeiterTable1, ArbeiterTable2, Preiszusammensetzung
from decimal import Decimal
from sqlalchemy.sql import func
from sqlalchemy.orm import aliased
from graphviz import Digraph


main_betriebe = Blueprint('main_betriebe', __name__, template_folder='templates',
    static_folder='static')


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
        arbeiter = Arbeiter.query.filter_by(betrieb=current_user.id).first()
        if arbeiter:
            having_workers = True
        else:
            having_workers = False
        return render_template('profile_betriebe.html', having_workers=having_workers)
    elif user_type == "nutzer":
        return redirect(url_for('auth.zurueck'))


@main_betriebe.route('/betriebe/arbeit', methods=['GET', 'POST'])
@login_required
def arbeit():
    arbeiter1 = db.session.query(Nutzer.id, Nutzer.name).\
        select_from(Arbeiter).join(Nutzer).filter(Arbeiter.betrieb==current_user.id).group_by(Nutzer.id).all()
    table1 = ArbeiterTable1(arbeiter1)

    arbeiter2 = db.session.query(Nutzer.id, Nutzer.name, func.sum(Arbeit.stunden).label('summe_stunden')).\
        select_from(Angebote).filter(Angebote.betrieb==current_user.id).join(Arbeit).join(Nutzer).group_by(Nutzer.id).all()
    table2 = ArbeiterTable2(arbeiter2)
    fik = Betriebe.query.filter_by(id=current_user.id).first().fik

    if request.method == 'POST':
        # check if nutzer exists, if not flash warning
        if not Nutzer.query.filter_by(id=request.form['nutzer']).first():
            flash("Nutzer existiert nicht.")
            return redirect(url_for('main_betriebe.arbeit'))

        # check if nutzer is already arbeiter in betrieb
        req_arbeiter = Arbeiter.query.filter_by(nutzer=request.form['nutzer'], betrieb=current_user.id).first()
        # if so, flash warning
        if req_arbeiter:
            flash("Nutzer ist bereits in diesem Betrieb beschäftigt.")
        else:
            new_arbeiter = Arbeiter(nutzer=request.form['nutzer'], betrieb=current_user.id)
            db.session.add(new_arbeiter)
            db.session.commit()
        return redirect(url_for('main_betriebe.arbeit'))

    return render_template("arbeit.html", table1=table1, table2=table2, fik=fik)


@main_betriebe.route('/betriebe/produktionsmittel')
@login_required
def produktionsmittel():
    produktionsmittel_qry = db.session.query(Kaeufe.id, Angebote.name, Angebote.beschreibung,\
        Angebote.preis, func.coalesce(func.sum(Produktionsmittel.prozent_gebraucht).\
        label("prozent_gebraucht"), 0).label("prozent_gebraucht")).select_from(Kaeufe)\
        .filter(Kaeufe.betrieb==current_user.id).outerjoin(Produktionsmittel,\
        Kaeufe.id==Produktionsmittel.kauf).join(Angebote, Kaeufe.angebot==Angebote.id).\
        group_by(Kaeufe, Angebote, Produktionsmittel.kauf)

    produktionsmittel_aktiv = produktionsmittel_qry.having(func.coalesce(func.sum(Produktionsmittel.prozent_gebraucht).\
    label("prozent_gebraucht"), 0).label("prozent_gebraucht")<100).all()
    produktionsmittel_inaktiv = produktionsmittel_qry.having(func.coalesce(func.sum(Produktionsmittel.prozent_gebraucht).\
    label("prozent_gebraucht"), 0).label("prozent_gebraucht")== 100).all()

    table_aktiv = ProduktionsmittelTable(produktionsmittel_aktiv)
    table_inaktiv = ProduktionsmittelTable(produktionsmittel_inaktiv)



    angebote1 = aliased(Angebote)
    angebote2 = aliased(Angebote)
    angebote3 = aliased(Angebote)
    angebote4 = aliased(Angebote)

    produktionsmittel1 = aliased(Produktionsmittel)
    produktionsmittel2 = aliased(Produktionsmittel)
    produktionsmittel3 = aliased(Produktionsmittel)
    produktionsmittel4 = aliased(Produktionsmittel)

    kaeufe2 = aliased(Kaeufe)
    kaeufe3 = aliased(Kaeufe)
    kaeufe4 = aliased(Kaeufe)

    first_level = db.session.query(
        angebote1.id.label("angebot1"), angebote1.name.label("name1"), angebote1.p_kosten.label("p1"),
        angebote1.v_kosten.label("v1"), angebote1.preis.label("preis1"), produktionsmittel1.prozent_gebraucht.label("proz_gebr2"),
        produktionsmittel1.kauf.label("kauf2"),
        kaeufe2.angebot.label("angebot2"), angebote2.name.label("name2"),
        angebote2.preis.label("preis2"), (angebote2.preis*(produktionsmittel1.prozent_gebraucht/100)).label("kosten2"),
        produktionsmittel2.prozent_gebraucht.label("proz_gebr3"), produktionsmittel2.kauf.label("kauf3"),
        kaeufe3.angebot.label("angebot3"), angebote3.name.label("name3"),
        angebote3.preis.label("preis3"), (angebote3.preis*(produktionsmittel2.prozent_gebraucht/100)).label("kosten3"),
        produktionsmittel3.prozent_gebraucht.label("proz_gebr4"), produktionsmittel3.kauf.label("kauf4"),
        kaeufe4.angebot.label("angebot4"), angebote4.name.label("name4"),
        angebote4.preis.label("preis4"), (angebote4.preis*(produktionsmittel3.prozent_gebraucht/100)).label("kosten4"),
        produktionsmittel4.prozent_gebraucht.label("proz_gebr5"), produktionsmittel4.kauf.label("kauf5"))\
            .select_from(angebote1).filter(angebote1.id==10).outerjoin\
            (produktionsmittel1, angebote1.id==produktionsmittel1.angebot)

    second_level = first_level.outerjoin(kaeufe2, produktionsmittel1.kauf==kaeufe2.id).outerjoin(angebote2, kaeufe2.angebot==angebote2.id).\
        outerjoin(produktionsmittel2, angebote2.id == produktionsmittel2.angebot)

    third_level = second_level.outerjoin(kaeufe3, produktionsmittel2.kauf==kaeufe3.id).outerjoin(angebote3, kaeufe3.angebot==angebote3.id).\
        outerjoin(produktionsmittel3, angebote3.id == produktionsmittel3.angebot)

    fourth_level = third_level.outerjoin(kaeufe4, produktionsmittel3.kauf==kaeufe4.id).outerjoin(angebote4, kaeufe4.angebot==angebote4.id).\
        outerjoin(produktionsmittel4, angebote4.id == produktionsmittel4.angebot)



    print("-----")
    print(fourth_level.count())

    col4, col3, col2, col1 = [], [], [], []

    for row in fourth_level:
        print(row.name1, row.name2, row.name3, row.name4)
        col1.append(row.name1)
        col2.append(row.name2)
        col3.append(row.name3)
        col4.append(row.name4)

    list_of_cols = [col1, col2, col3, col4]

    cols_dict = []

    for r in range(fourth_level.count()):
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
            elif i == None:
                pass
            else:
                list1.append({i:[c]})
        cols_dict.append(list1)


    print(">>>>>")
    for i in cols_dict:
        print(i)

    print(">>>>>")
    for cnt, col in enumerate(cols_dict):
        if cnt == 0: # if first column (should be the same angebot, anyway)
            pass
        else: # the following columns
            print("cnt:", cnt)
            for j in col:
                current_angebot = list(j.keys())[0]
                current_position = list(j.values())[0]
                print(current_angebot, current_position)
                parent_angebote_list = cols_dict[cnt-1]
                print("parent_angebote_list", parent_angebote_list)
                for par in parent_angebote_list:
                    parent_angebot = list(par.keys())[0]
                    parent_positions = list(par.values())[0]
                    print("-", parent_angebot, parent_positions)
                    for cur_pos in current_position:
                        if cur_pos in parent_positions:
                            print("MATCH", parent_angebot, current_angebot)
                            break # only one match is enough

        print(">")

        print("<<<<<")


    # [int(s) for s in string_of_numbers.split(',')]




    table_preiszus = Preiszusammensetzung(fourth_level)
    return render_template('produktionsmittel.html', table_aktiv=table_aktiv, table_inaktiv=table_inaktiv, table_preiszus=table_preiszus)


@main_betriebe.route('/betriebe/suchen', methods=['GET', 'POST'])
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
            return redirect('/betriebe/suchen')
        else:
            return render_template('suchen_betriebe.html', form=search, results=results)

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
            # guthaben self aktualisieren
            kaufender_betrieb = db.session.query(Betriebe).filter(Betriebe.id == current_user.id).first()
            kaufender_betrieb.guthaben -= angebot.preis
            db.session.commit()
            # guthaben der arbeiter erhöhen
            arbeit_in_produkt = Arbeit.query.filter_by(angebot=angebot.id).all()
            for arb in arbeit_in_produkt:
                Nutzer.query.filter_by(id=arb.nutzer).first().guthaben += arb.stunden
                arb.ausbezahlt = True
                db.session.commit()

            # guthaben des anbietenden betriebes erhöhen
            anbietender_betrieb_id = angebot.betrieb
            anbietender_betrieb = Betriebe.query.filter_by(id=anbietender_betrieb_id).first()
            anbietender_betrieb.guthaben += angebot.p_kosten

            flash(f"Kauf von '{angebot.name}' erfolgreich!")
            return redirect('/betriebe/suchen')

        return render_template('kaufen_betriebe.html', angebot=angebot)
    else:
        return 'Error loading #{id}'.format(id=id)


@main_betriebe.route('/betriebe/anbieten_info', methods=['GET', 'POST'])
@login_required
def anbieten_info():
    """
    infos zum anbieten von produkten
    """
    return render_template('anbieten_info.html')


@main_betriebe.route('/betriebe/anbieten', methods=['GET', 'POST'])
@login_required
def neues_angebot():
    """
    Ein neues Angebot hinzufügen
    """
    produktionsmittel_aktiv = db.session.query(Kaeufe.id, Angebote.name, Angebote.beschreibung,\
        Angebote.preis, func.coalesce(func.sum(Produktionsmittel.prozent_gebraucht).\
        label("prozent_gebraucht"), 0).label("prozent_gebraucht")).select_from(Kaeufe)\
        .filter(Kaeufe.betrieb==current_user.id).outerjoin(Produktionsmittel,\
        Kaeufe.id==Produktionsmittel.kauf).join(Angebote, Kaeufe.angebot==Angebote.id).\
        group_by(Kaeufe, Angebote, Produktionsmittel.kauf).\
        having(func.coalesce(func.sum(Produktionsmittel.prozent_gebraucht).\
        label("prozent_gebraucht"), 0).label("prozent_gebraucht")<100).all()

    arbeiter_all = db.session.query(Nutzer.id, Nutzer.name).select_from(Arbeiter)\
        .join(Nutzer, Arbeiter.nutzer==Nutzer.id).filter(Arbeiter.betrieb==current_user.id).all()

    if request.method == 'POST':
        # create request dictionary
        request_dict = request.form.to_dict()
        # arbeit
        # dict with arbeit values
        arbeit_dict = dict(filter(lambda elem: elem[0][:7] == 'nutzer_', request_dict.items()))
        # arbeit dict entries that are not zero
        arbeit_dict_not_zero = dict(filter(lambda elem: Decimal(elem[1]) != 0, arbeit_dict.items()))
        kosten_arbeit = 0

        # produktionsmittel
        # dict with produktionsmittel values
        pm_dict = dict(filter(lambda elem: elem[0][:3] == 'id_', request_dict.items()))
        # pm dict entries that are not zero
        pm_dict_not_zero = dict(filter(lambda elem: Decimal(elem[1]) != 0,pm_dict.items()))
        kosten_pm = 0
        if pm_dict_not_zero:
            # calculate kosten pm
            # turning pm-dict into two lists
            kauf_id_list = []
            prozent_list = []
            for key in list(pm_dict_not_zero.keys()):
                kauf_id_list.append(key[3:])
            for value in list(pm_dict_not_zero.values()):
                prozent_list.append(Decimal(value)/100)
            # preise
            preise_list = []
            for idx in kauf_id_list:
                qry = db.session.query(Kaeufe, Angebote.preis).join(Angebote, Kaeufe.angebot==Angebote.id).filter(Kaeufe.id == idx).all()
                preise_list.append(Decimal(qry[0][1]))
            kosten_einzeln = []
            for num1, num2 in zip(prozent_list, preise_list):
                kosten_einzeln.append(num1 * num2)
            kosten_pm = sum(kosten_einzeln)


        if arbeit_dict_not_zero:
            # calculate kosten arbeit
            nutzer_id_list = []
            stunden_list = []
            for key in list(arbeit_dict_not_zero.keys()):
                nutzer_id_list.append(key[7:])
            for value in list(arbeit_dict_not_zero.values()):
                stunden_list.append(Decimal(value))
            print(nutzer_id_list, stunden_list)
            assert len(nutzer_id_list) == len(stunden_list)
            kosten_arbeit = sum(stunden_list)

        # save new angebot
        new_angebot = Angebote(name=request.form["name"], betrieb=current_user.id,\
            beschreibung=request.form["beschreibung"], kategorie=request.form["kategorie"], p_kosten=kosten_pm,\
            v_kosten=kosten_arbeit, preis=kosten_arbeit + kosten_pm)
        db.session.add(new_angebot)
        db.session.commit()


        # create rows in table "arbeit"
        if arbeit_dict_not_zero:
            assert len(nutzer_id_list) == len(stunden_list)
            for count, i in enumerate(nutzer_id_list):
                new_arbeit = Arbeit(angebot=new_angebot.id, nutzer=i,\
                    stunden=stunden_list[count], ausbezahlt=False)
                db.session.add(new_arbeit)
                db.session.commit()

        # new row in produktionsmittel! (um gesamten verbrauch zu erhalten, gruppieren/summieren!)
        if pm_dict_not_zero:
            assert len(kauf_id_list) == len(prozent_list)
            for count, i in enumerate(kauf_id_list):
                new_produktionsmittel_prd = Produktionsmittel\
                    (angebot=new_angebot.id, kauf=i, prozent_gebraucht=prozent_list[count]*100)
                db.session.add(new_produktionsmittel_prd)
                db.session.commit()

        # kosten zusammenfassen und bestätigen lassen!
        flash('Angebot erfolgreich gespeichert!')
        return redirect('/betriebe/home')

    categ = ["Auto, Rad & Boot", "Dienstleistungen", "Elektronik", "Familie, Kind & Baby",
    "Freizeit & Hobby", "Haus & Garten", "Haustiere", "Mode & Beauty", "Nahrungsmittel", "Musik, Filme und Bücher",
    "Nachbarschaftshilfe", "Unterricht und Kurse"]

    return render_template('neues_angebot.html', produktionsmittel_aktiv=produktionsmittel_aktiv, arbeiter_all=arbeiter_all, categ=categ)


@main_betriebe.route('/betriebe/meine_angebote')
@login_required
def meine_angebote():
    aktuelle_angebote = Angebote.query.filter_by(aktiv=True, betrieb=current_user.id).all()
    vergangene_angebote = Angebote.query.filter_by(aktiv=False, betrieb=current_user.id).all()
    return render_template('meine_angebote.html', aktuelle_angebote=aktuelle_angebote, vergangene_angebote=vergangene_angebote)


@main_betriebe.route('/betriebe/angebot_loeschen', methods=['GET', 'POST'])
@login_required
def angebot_loeschen():
    angebot_id = request.args.get("id")
    angebot = Angebote.query.filter_by(id=angebot_id).first()
    if request.method == 'POST':
        if request.form["verbraucht"] == "ja":
            # alle Arbeiter automatisch ausbezahlen. Die Produktionsmittel bleiben als verbraucht markiert.
            arbeit_in_produkt = Arbeit.query.filter_by(angebot=angebot.id).all()
            for arb in arbeit_in_produkt:
                assert arb.ausbezahlt == False
                Nutzer.query.filter_by(id=arb.nutzer).first().guthaben += arb.stunden
                arb.ausbezahlt = True
        else:
            # Produktionsmittel wieder freigegeben und geleistete Arbeit auf Null setzen
            pm_in_produkt = Produktionsmittel.query.filter_by(angebot=angebot.id).all()
            for pm in pm_in_produkt:
                pm.prozent_gebraucht = 0
            arbeit_in_produkt = Arbeit.query.filter_by(angebot=angebot.id).all()
            for arb in arbeit_in_produkt:
                arb.stunden = 0
                arb.ausbezahlt = True

        angebot.aktiv = False
        db.session.commit()
        flash("Löschen des Angebots erfolgreich.")
        return redirect(url_for('main_betriebe.meine_angebote'))

    return render_template('angebot_loeschen.html', angebot=angebot)
