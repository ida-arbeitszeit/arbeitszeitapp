import datetime
from .models import Nutzer, Betriebe, Kaeufe, Arbeit
from . import db

def kauf_vorgang(kaufender_type, angebot, kaeufer_id):
    # kauefe aktualisieren
    if kaufender_type == "betriebe":
        kaufender = Betriebe
        new_kauf = Kaeufe(kauf_date = datetime.datetime.now(), angebot = angebot.id,
                type_nutzer = False, betrieb = kaeufer_id,
                nutzer = None)
        db.session.add(new_kauf)
        db.session.commit()
    elif kaufender_type == "nutzer":
        kaufender = Nutzer
        new_kauf = Kaeufe(kauf_date = datetime.datetime.now(), angebot = angebot.id,
                type_nutzer = True, betrieb = None,
                nutzer = kaeufer_id)
        db.session.add(new_kauf)
        db.session.commit()

    # angebote aktualisieren (aktiv = False)
    angebot.aktiv = False
    db.session.commit()
    # guthaben self verringern
    kaeufer = db.session.query(kaufender).filter(kaufender.id == kaeufer_id).first()
    kaeufer.guthaben -= angebot.preis
    db.session.commit()

    # guthaben der arbeiter erhöhen, wenn ausbezahlt = false
    arbeit_in_produkt = Arbeit.query.filter_by(angebot=angebot.id, ausbezahlt=False).all()
    for arb in arbeit_in_produkt:
        Nutzer.query.filter_by(id=arb.nutzer).first().guthaben += arb.stunden
        arb.ausbezahlt = True
        db.session.commit()

    # guthaben des anbietenden betriebes erhöhen
    anbietender_betrieb_id = angebot.betrieb
    anbietender_betrieb = Betriebe.query.filter_by(id=anbietender_betrieb_id).first()
    anbietender_betrieb.guthaben += angebot.p_kosten
    db.session.commit()
