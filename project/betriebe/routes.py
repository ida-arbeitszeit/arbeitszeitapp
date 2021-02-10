from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from flask_login import login_required, current_user
from .. import db
from ..models import Angebote, Kaeufe, Betriebe, Nutzer, Produktionsmittel, Arbeit, Arbeiter, Auszahlungen,\
    Kooperationen, KooperationenMitglieder
from ..forms import ProductSearchForm
from ..tables import ProduktionsmittelTable, ArbeiterTable1, ArbeiterTable2, Preiszusammensetzung
from ..composition_of_prices import get_table_of_composition, get_positions_in_table, create_dots
from ..such_vorgang import such_vorgang
from ..kauf_vorgang import kauf_vorgang
from decimal import Decimal
import datetime
from sqlalchemy.sql import func


main_betriebe = Blueprint('main_betriebe', __name__, template_folder='templates',
    static_folder='static')


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
    table1 = ArbeiterTable1(arbeiter1, no_items='(Noch keine Mitarbeiter.)')

    arbeiter2 = db.session.query(Nutzer.id, Nutzer.name,
        func.concat(func.sum(Arbeit.stunden), " Std.").label('summe_stunden')).\
        select_from(Angebote).filter(Angebote.betrieb==current_user.id).\
        join(Arbeit).join(Nutzer).group_by(Nutzer.id).order_by(func.sum(Arbeit.stunden).desc()).all()
    table2 = ArbeiterTable2(arbeiter2, no_items='(Noch keine Stunden gearbeitet.)')
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
        func.concat(func.round(Angebote.preis, 2), " Std.").label("preis"),\
        func.concat(func.round(func.coalesce(func.sum(Produktionsmittel.prozent_gebraucht), 0), 2), " %").\
            label("prozent_gebraucht"))\
        .select_from(Kaeufe)\
        .filter(Kaeufe.betrieb==current_user.id).outerjoin(Produktionsmittel,\
        Kaeufe.id==Produktionsmittel.kauf).join(Angebote, Kaeufe.angebot==Angebote.id).\
        group_by(Kaeufe, Angebote, Produktionsmittel.kauf)

    produktionsmittel_aktiv = produktionsmittel_qry.having(func.coalesce(func.sum(Produktionsmittel.prozent_gebraucht).\
    label("prozent_gebraucht"), 0).label("prozent_gebraucht")<100).all()
    produktionsmittel_inaktiv = produktionsmittel_qry.having(func.coalesce(func.sum(Produktionsmittel.prozent_gebraucht).\
    label("prozent_gebraucht"), 0).label("prozent_gebraucht")== 100).all()

    table_aktiv = ProduktionsmittelTable(produktionsmittel_aktiv, no_items="(Keine Produktionsmittel vorhanden.)")
    table_inaktiv = ProduktionsmittelTable(produktionsmittel_inaktiv, no_items="(Noch keine Produktionsmittel verbraucht.)")

    return render_template('produktionsmittel.html', table_aktiv=table_aktiv, table_inaktiv=table_inaktiv)


@main_betriebe.route('/betriebe/suchen', methods=['GET', 'POST'])
@login_required
def suchen():
    return such_vorgang("betriebe", request.form)


@main_betriebe.route('/betriebe/details/<int:id>', methods=['GET', 'POST'])
def details(id):
    table_of_composition =  get_table_of_composition(id)
    cols_dict = get_positions_in_table(table_of_composition)
    dot = create_dots(cols_dict, table_of_composition)
    piped = dot.pipe().decode('utf-8')
    table_preiszus = Preiszusammensetzung(table_of_composition)

    if request.method == 'POST':
        return redirect('/betriebe/suchen')

    return render_template('details_betriebe.html', table_preiszus=table_preiszus, piped=piped)


@main_betriebe.route('/betriebe/kaufen/<int:id>', methods=['GET', 'POST'])
def kaufen(id):
    qry = db.session.query(Angebote).filter(
                Angebote.id==id)
    angebot = qry.first()
    if angebot:
        if request.method == 'POST':
            kauf_vorgang(kaufender_type="betriebe", angebot=angebot, kaeufer_id=current_user.id)
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
        quantity = int(request.form["quantity"])
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
                qry = db.session.query(Kaeufe, Angebote.preis).\
                    join(Angebote, Kaeufe.angebot==Angebote.id).filter(Kaeufe.id == idx).all()
                preise_list.append(Decimal(qry[0][1]))
            kosten_einzeln = []
            for num1, num2 in zip(prozent_list, preise_list):
                kosten_einzeln.append(num1 * num2)
            kosten_pm = sum(kosten_einzeln) / quantity


        if arbeit_dict_not_zero:
            # calculate kosten arbeit
            nutzer_id_list = []
            stunden_list = []
            for key in list(arbeit_dict_not_zero.keys()):
                nutzer_id_list.append(key[7:])
            for value in list(arbeit_dict_not_zero.values()):
                stunden_list.append(Decimal(value))
            assert len(nutzer_id_list) == len(stunden_list)
            kosten_arbeit = sum(stunden_list) / quantity

        # save new angebot(e)
        current_time = datetime.datetime.now()
        for quant in range(quantity):
            new_angebot = Angebote(name=request.form["name"], cr_date=current_time,  betrieb=current_user.id,\
                beschreibung=request.form["beschreibung"], kategorie=request.form["kategorie"], p_kosten=kosten_pm,\
                v_kosten=kosten_arbeit, preis=kosten_arbeit + kosten_pm)
            db.session.add(new_angebot)
            db.session.commit()

            # create rows in table "arbeit"
            if arbeit_dict_not_zero:
                assert len(nutzer_id_list) == len(stunden_list)
                for count, i in enumerate(nutzer_id_list):
                    new_arbeit = Arbeit(angebot=new_angebot.id, nutzer=i,\
                        stunden=stunden_list[count] / quantity, ausbezahlt=False)
                    db.session.add(new_arbeit)
            # new row in produktionsmittel! (um gesamten verbrauch zu erhalten, gruppieren/summieren!)
            if pm_dict_not_zero:
                assert len(kauf_id_list) == len(prozent_list)
                for count, i in enumerate(kauf_id_list):
                    new_produktionsmittel_prd = Produktionsmittel\
                        (angebot=new_angebot.id, kauf=i, prozent_gebraucht=(prozent_list[count]*100 / quantity ))
                    db.session.add(new_produktionsmittel_prd)
            db.session.commit()

        # kosten zusammenfassen und bestätigen lassen!
        flash('Angebot erfolgreich gespeichert!')
        return redirect(url_for("main_betriebe.meine_angebote"))

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


@main_betriebe.route('/betriebe/angebot_verkaufen', methods=['GET', 'POST'])
@login_required
def angebot_verkaufen():
    angebot_id = request.args.get("id")
    angebot = Angebote.query.filter_by(id=angebot_id).first()

    if request.method == 'POST':
        code_input = request.form["code"]
        auszahlung = Auszahlungen.query.filter_by(code=code_input, entwertet=False).first()
        if not auszahlung:
            flash("Code nicht korrekt oder schon entwertet.")
        else:
            value_code = auszahlung.betrag
            if round(angebot.preis, 2) != round(value_code, 2):
                flash("Wert des Codes entspricht nicht dem Preis.")
            else:
                kaufender_type = "nutzer" if auszahlung.type_nutzer else "betriebe"
                kauf_vorgang(kaufender_type=kaufender_type, angebot=angebot, kaeufer_id=auszahlung.nutzer)
                auszahlung.entwertet = True
                db.session.commit()
                flash("Verkauf erfolgreich")
                return redirect(url_for("main_betriebe.meine_angebote"))

    return render_template('angebot_verkaufen.html', angebot=angebot)

@main_betriebe.route('/betriebe/kooperieren', methods=['GET', 'POST'])
@login_required
def kooperieren():

    if request.method == 'POST':

        angebot_id_eigenes = request.form["angebot_id_eigenes"]
        angebot_id_externes = request.form["angebot_id_externes"]

        # do both Angebote exist?
        own = Angebote.query.filter_by(id=angebot_id_eigenes, aktiv=True).first()
        extern = Angebote.query.filter_by(id=angebot_id_externes, aktiv=True).first()
        if not (own and extern):
            # BETTER/TO DO: is it really user's own product?
            flash("Nicht existente Angebot-IDs")
        else:
            # one product can only be in one coop!
            eigene_koop = KooperationenMitglieder.query.filter_by(mitglied=angebot_id_eigenes, aktiv=True).first()
            externe_koop = KooperationenMitglieder.query.filter_by(mitglied=angebot_id_externes, aktiv=True).first()
            if (not eigene_koop and not externe_koop):
                print("neither exists")
                flash("Kooperation wird gestartet.")
                current_time = datetime.datetime.now()
                new_koop = Kooperationen(cr_date=current_time)
                db.session.add(new_koop)
                db.session.commit()
                # add all of the batch, not only specified angebot! (defined by cr_date and name) Muss evtl sicherer werden.
                for i in db.session.query(Angebote).filter_by(cr_date=own.cr_date, name=own.name).all():
                    new_koop_mitglieder_1 = KooperationenMitglieder(kooperation=new_koop.id, mitglied=i.id)
                    db.session.add(new_koop_mitglieder_1)
                for j in db.session.query(Angebote).filter_by(cr_date=extern.cr_date, name=extern.name).all():
                    new_koop_mitglieder_2 = KooperationenMitglieder(kooperation=new_koop.id, mitglied=j.id)
                    db.session.add(new_koop_mitglieder_2)
                db.session.commit()

                # to do here: adapt prices and show products as part of coop!!

            elif eigene_koop and externe_koop:
                print("both exist")
                if eigene_koop.kooperation == externe_koop.kooperation:
                    flash("Die beiden Produkte sind bereits in Kooperation.")
                else:
                    print("both in different coops")
                    flash("Das Produkt des Kooperationspartners\
                        befindet sich in einer Kooperation - die eigene Kooperation\
                        wird verlassen und der neuen beigetreten.")

            elif eigene_koop and not externe_koop:
                print("only eigene exists")
                flash("Du befindest dich bereits in einer Kooperation\
                     - die aktuelle Kooperation wird verlassen und eine neue wird gestartet.")

            elif externe_koop and not eigene_koop:
                print("only externe exists")
                flash("Das Produkt des Kooperationspartners\
                    befindet sich in einer Kooperation - dein Produkt tritt dieser Kooperation bei.")

            # eigenes und externes kooperieren schon --> "bereits kooperation!"
            # eigenes ist schon in einer kooperation --> "kooperation verlassen und wechseln/neue kooperation starten"?
            # externes ist schon in einer kooperation --> dieser koop beitreten?
            # else: "wirklich neue kooperation gründen?"

            #
            # new_arbeiter = Arbeiter(nutzer=request.form['nutzer'], betrieb=current_user.id)
            # db.session.add(new_arbeiter)
            # db.session.commit()

    return render_template('kooperieren.html')


@main_betriebe.route('/betriebe/hilfe')
@login_required
def hilfe():
    return render_template('betriebe_hilfe.html')
