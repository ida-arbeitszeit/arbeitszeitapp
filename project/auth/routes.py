from flask import Blueprint, render_template, redirect, url_for, request,\
    flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from project import database

auth = Blueprint(
    'auth', __name__, template_folder='templates', static_folder='static')


@auth.route('/')
def start():
    session["user_type"] = None
    return render_template('start.html')


@auth.route('/help')
def help():
    return render_template('start_hilfe.html')


# Member
@auth.route('/member/signup')
def signup_member():
    return render_template('signup_member.html')


@auth.route('/member/signup', methods=['POST'])
def signup_member_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    member = database.get_user_by_mail(email=email)

    if member:
        flash('Email address already exists')
        return redirect(url_for('auth.signup_member'))

    database.add_new_user(
        email=email,
        name=name,
        password=generate_password_hash(password, method='sha256')
    )

    return redirect(url_for('auth.login_member'))


@auth.route('/member/login')
def login_member():
    return render_template('login_member.html')


@auth.route('/member/login', methods=['POST'])
def login_member_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    member = database.get_user_by_mail(email)

    if not member or not check_password_hash(member.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login_member'))

    session["user_type"] = "member"
    login_user(member, remember=remember)
    return redirect(url_for('main_member.profile'))


# Betriebe
@auth.route('/betriebe/login')
def login_betriebe():
    return render_template('login_betriebe.html')


@auth.route('/betriebe/login', methods=['POST'])
def login_betriebe_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    betrieb = database.get_company_by_mail(email)

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

    betrieb = database.get_company_by_mail(email)

    if betrieb:
        flash('Email address already exists')
        return redirect(url_for('auth.signup_betriebe'))

    database.add_new_company(
        email=email,
        name=name,
        password=generate_password_hash(password, method='sha256'))

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
