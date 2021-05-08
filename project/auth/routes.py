from flask import Blueprint, render_template, redirect, url_for, request,\
    flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from ..models import Nutzer, Betriebe
from ..extensions import db

auth = Blueprint(
    'auth', __name__, template_folder='templates', static_folder='static')


@auth.route('/')
def start():
    session["user_type"] = None
    return render_template('start.html')


@auth.route('/help')
def help():
    return render_template('start_hilfe.html')


# Nutzer
@auth.route('/nutzer/signup')
def signup_nutzer():
    return render_template('signup_nutzer.html')


@auth.route('/nutzer/signup', methods=['POST'])
def signup_nutzer_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    nutzer = Nutzer.query.filter_by(email=email).first()

    if nutzer:
        flash('Email address already exists')
        return redirect(url_for('auth.signup_nutzer'))

    new_user = Nutzer(
        email=email, name=name,
        password=generate_password_hash(password, method='sha256'))

    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login_nutzer'))


@auth.route('/nutzer/login')
def login_nutzer():
    return render_template('login_nutzer.html')


@auth.route('/nutzer/login', methods=['POST'])
def login_nutzer_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    nutzer = Nutzer.query.filter_by(email=email).first()

    if not nutzer or not check_password_hash(nutzer.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login_nutzer'))

    session["user_type"] = "nutzer"
    login_user(nutzer, remember=remember)
    return redirect(url_for('main_nutzer.profile'))

# Betriebe
@auth.route('/betriebe/login')
def login_betriebe():
    return render_template('login_betriebe.html')


@auth.route('/betriebe/login', methods=['POST'])
def login_betriebe_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    betrieb = Betriebe.query.filter_by(email=email).first()

    if not betrieb or not check_password_hash(betrieb.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login_betriebe'))

    session["user_type"] = "betrieb"
    login_user(betrieb, remember=remember)
    return redirect(url_for('main_betriebe.profile'))


@auth.route('/betriebe/signup')
def signup_betriebe():
    return render_template('signup_betriebe.html')


@auth.route('/betriebe/signup', methods=['POST'])
def signup_betriebe_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    betrieb = Betriebe.query.filter_by(email=email).first()

    if betrieb:
        flash('Email address already exists')
        return redirect(url_for('auth.signup_betriebe'))

    new_betrieb = Betriebe(
        email=email, name=name,
        password=generate_password_hash(password, method='sha256'))
    db.session.add(new_betrieb)
    db.session.commit()

    return redirect(url_for('auth.login_betriebe'))


# logout
@auth.route('/zurueck')
def zurueck():
    session["user_type"] = None
    logout_user()
    return redirect(url_for('auth.start'))


@auth.route('/logout')
@login_required
def logout():
    session["user_type"] = None
    logout_user()
    return redirect(url_for('auth.start'))
