"""
Definition of database tables.

The table name is automatically set by Flask-SQLAlchemy unless overridden.
It’s derived from the class name converted to lowercase and
with “CamelCase” converted to “camel_case”.
"""

from flask_login import UserMixin
from . import db


class Nutzer(UserMixin, db.Model):
    # primary keys are required by SQLAlchemy
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(1000), nullable=False)
    guthaben = db.Column(db.Numeric(), default=0, nullable=False)


class Betriebe(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(1000), nullable=False)
    guthaben = db.Column(db.Numeric(), default=0)
    fik = db.Column(db.Numeric(), nullable=False, default=1)

    def __repr__(self):
        return "<Betriebe(email='%s', name='%s', guthaben='%s', fik='%s')>" % (
                             self.email, self.name, self.guthaben, self.fik)


class Angebote(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cr_date = db.Column(db.DateTime, nullable=False)
    name = db.Column(db.String(1000), nullable=False)
    betrieb = db.Column(
        db.Integer, db.ForeignKey("betriebe.id"), nullable=False)
    beschreibung = db.Column(db.String(1000), nullable=False)
    kategorie = db.Column(db.String(50), nullable=False)
    p_kosten = db.Column(db.Numeric(), nullable=False)
    v_kosten = db.Column(db.Numeric(), nullable=False)
    preis = db.Column(db.Numeric(), nullable=False)
    aktiv = db.Column(db.Boolean, nullable=False, default=True)

    def __repr__(self):
        return "<Angebote(cr_date='%s', name='%s', betrieb='%s', \
beschreibung='%s', kategorie='%s', \
p_kosten='%s', v_kosten='%s', preis='%s', aktiv='%s')>" % (
                             self.cr_date, self.name, self.betrieb,
                             self.beschreibung,
                             self.kategorie, self.p_kosten, self.v_kosten,
                             self.preis, self.aktiv)


class Kaeufe(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kauf_date = db.Column(db.DateTime, nullable=False)
    angebot = db.Column(
        db.Integer, db.ForeignKey("angebote.id"), nullable=False)
    type_nutzer = db.Column(db.Boolean, nullable=False)
    betrieb = db.Column(
        db.Integer, db.ForeignKey("betriebe.id"), nullable=True)
    nutzer = db.Column(db.Integer, db.ForeignKey("nutzer.id"), nullable=True)
    kaufpreis = db.Column(db.Numeric(), nullable=False)


class Arbeit(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    angebot = db.Column(
        db.Integer, db.ForeignKey("angebote.id"), nullable=False)
    nutzer = db.Column(db.Integer, db.ForeignKey("nutzer.id"), nullable=False)
    stunden = db.Column(db.Numeric(), nullable=False)
    # ausbezahlt = db.Column(db.Boolean, nullable=False, default=False)


class Arbeiter(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nutzer = db.Column(db.Integer, db.ForeignKey("nutzer.id"), nullable=False)
    betrieb = db.Column(
        db.Integer, db.ForeignKey("betriebe.id"), nullable=False)


class Produktionsmittel(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    angebot = db.Column(
        db.Integer, db.ForeignKey("angebote.id"), nullable=False)
    kauf = db.Column(db.Integer, db.ForeignKey("kaeufe.id"), nullable=False)
    prozent_gebraucht = db.Column(db.Numeric(), nullable=False)

    def __repr__(self):
        return "<Produktionsmittel(angebot='%s', kauf='%s', \
prozent_gebraucht='%s')>" % (
                             self.angebot, self.kauf, self.prozent_gebraucht)


class Bewertungen(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # either betrieb or nutzer:
    type_nutzer = db.Column(db.Boolean, nullable=False)
    betrieb = db.Column(
        db.Integer, db.ForeignKey("betriebe.id"), nullable=True)
    nutzer = db.Column(db.Integer, db.ForeignKey("nutzer.id"), nullable=True)
    kauf = db.Column(db.Integer, db.ForeignKey("kaeufe.id"), nullable=False)
    bewertung = db.Column(db.Integer, nullable=False)


class Auszahlungen(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type_nutzer = db.Column(db.Boolean, nullable=False)
    nutzer = db.Column(db.Integer, db.ForeignKey("nutzer.id"), nullable=False)
    betrag = db.Column(db.Numeric(), nullable=False)
    code = db.Column(db.String(100), nullable=False)
    entwertet = db.Column(db.Boolean, nullable=False, default=False)


class Kooperationen(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cr_date = db.Column(db.DateTime, nullable=False)
    aktiv = db.Column(db.Boolean, nullable=False, default=True)


class KooperationenMitglieder(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kooperation = db.Column(
        db.Integer, db.ForeignKey("kooperationen.id"), nullable=False)
    mitglied = db.Column(
        db.Integer, db.ForeignKey("angebote.id"), nullable=False)
    aktiv = db.Column(db.Boolean, nullable=False, default=True)
