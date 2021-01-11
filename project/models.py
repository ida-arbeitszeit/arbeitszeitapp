from flask_login import UserMixin
from .app import db

class Nutzer(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
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

class Angebote(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000), nullable=False)
    betrieb = db.Column(db.Integer, db.ForeignKey("betriebe.id"), nullable=False)
    beschreibung = db.Column(db.String(1000), nullable=False)
    kategorie = db.Column(db.String(50), nullable=False)
    p_kosten = db.Column(db.Numeric(), nullable=False)
    v_kosten = db.Column(db.Numeric(), nullable=False)
    preis = db.Column(db.Numeric(), nullable=False)
    aktiv = db.Column(db.Boolean, nullable=False, default=True)

class Kaeufe(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    angebot = db.Column(db.Integer, db.ForeignKey("angebote.id"), nullable=False)
    type_nutzer = db.Column(db.Boolean, nullable=False)
    betrieb = db.Column(db.Integer, db.ForeignKey("betriebe.id"), nullable=True)
    nutzer = db.Column(db.Integer, db.ForeignKey("nutzer.id"), nullable=True)

class Arbeit(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    angebot = db.Column(db.Integer, db.ForeignKey("angebote.id"), nullable=False)
    nutzer = db.Column(db.Integer, db.ForeignKey("nutzer.id"), nullable=False)
    stunden = db.Column(db.Numeric(), nullable=False)
    ausbezahlt = db.Column(db.Boolean, nullable=False, default=False)

class Arbeiter(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nutzer = db.Column(db.Integer, db.ForeignKey("nutzer.id"), nullable=False)
    betrieb = db.Column(db.Integer, db.ForeignKey("betriebe.id"), nullable=False)

class Produktionsmittel(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    angebot = db.Column(db.Integer, db.ForeignKey("angebote.id"), nullable=False)
    kauf = db.Column(db.Integer, db.ForeignKey("kaeufe.id"), nullable=False)
    prozent_gebraucht = db.Column(db.Numeric(), nullable=False)

class Bewertungen(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type_nutzer = db.Column(db.Boolean, nullable=False) # either betrieb or nutzer
    betrieb = db.Column(db.Integer, db.ForeignKey("betriebe.id"), nullable=True)
    nutzer = db.Column(db.Integer, db.ForeignKey("nutzer.id"), nullable=True)
    kauf = db.Column(db.Integer, db.ForeignKey("kaeufe.id"), nullable=False)
    bewertung = db.Column(db.Integer, nullable=False)
