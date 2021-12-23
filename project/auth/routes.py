from datetime import datetime
from urllib.parse import urlparse

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user
from is_safe_url import is_safe_url
from werkzeug.security import check_password_hash

from arbeitszeit.errors import CompanyAlreadyExists, MemberAlreadyExists
from arbeitszeit.use_cases import RegisterCompany, RegisterMember
from project import database
from project.database import commit_changes
from project.dependency_injection import with_injection
from project.email import send_email
from project.forms import LoginForm, RegisterForm
from project.token import confirm_token, generate_confirmation_token

auth = Blueprint("auth", __name__, template_folder="templates", static_folder="static")


@auth.route("/")
def start():
    hostname = urlparse(request.base_url).hostname
    if "user_type" not in session:
        session["user_type"] = None
    next = request.args.get("next")
    if next is not None and is_safe_url(next, {hostname}):
        session["next"] = next
    return render_template("start.html")


@auth.route("/help")
def help():
    return render_template("start_hilfe.html")


# Member
@auth.route("/member/signup", methods=["GET", "POST"])
@commit_changes
@with_injection
def signup_member(register_member: RegisterMember):
    register_form = RegisterForm(request.form)
    if request.method == "POST" and register_form.validate():
        email = register_form.data["email"]
        name = register_form.data["name"]
        password = register_form.data["password"]
        try:
            register_member(email, name, password)
        except MemberAlreadyExists:
            register_form.email.errors.append("Emailadresse existiert bereits")
            return render_template("signup_member.html", form=register_form)

        member = database.get_user_by_mail(email)

        token = generate_confirmation_token(
            member.email,
            current_app.config["SECRET_KEY"],
            current_app.config["SECURITY_PASSWORD_SALT"],
        )
        confirm_url = url_for("auth.confirm_email", token=token, _external=True)
        html = render_template("activate.html", confirm_url=confirm_url)
        subject = "Bitte bestätige dein Konto"
        send_email(member.email, subject, html)

        return redirect(url_for("auth.unconfirmed_member"))

    return render_template("signup_member.html", form=register_form)


@auth.route("/member/unconfirmed")
def unconfirmed_member():
    return render_template("unconfirmed_member.html")


@auth.route("/member/confirm/<token>")
@commit_changes
def confirm_email(token):
    try:
        email = confirm_token(
            token,
            current_app.config["SECRET_KEY"],
            current_app.config["SECURITY_PASSWORD_SALT"],
        )
    except Exception:
        flash("Der Bestätigungslink ist ungültig oder ist abgelaufen.")
        return redirect(url_for("auth.unconfirmed_member"))
    member = database.get_user_by_mail(email)
    if member.confirmed:
        flash("Konto ist bereits bestätigt.")
    else:
        member.confirmed = True
        member.confirmed_on = datetime.now()
        flash("Das Konto wurde bestätigt. Danke!")
    return redirect(url_for("auth.login_member"))


@auth.route("/member/login", methods=["GET", "POST"])
@commit_changes
def login_member():
    login_form = LoginForm(request.form)
    if request.method == "POST" and login_form.validate():
        email = login_form.data["email"]
        password = login_form.data["password"]
        remember = True if login_form.data["remember"] else False

        member = database.get_user_by_mail(email)
        if not member:
            login_form.email.errors.append(
                "Emailadresse nicht korrekt. Bist du schon registriert?"
            )
        elif not check_password_hash(member.password, password):
            login_form.password.errors.append("Passwort nicht korrekt")
        else:
            session["user_type"] = "member"
            login_user(member, remember=remember)
            try:
                next = session.pop("next")
            except KeyError:
                next = None
            return redirect(next or url_for("main_member.profile"))

    if current_user.is_authenticated:
        if session.get("user_type") == "member":
            return redirect(url_for("main_member.profile"))
        else:
            session["user_type"] = None
            logout_user()

    return render_template("login_member.html", form=login_form)


@auth.route("/resend")
@login_required
def resend_confirmation():

    token = generate_confirmation_token(
        current_user.email,
        current_app.config["SECRET_KEY"],
        current_app.config["SECURITY_PASSWORD_SALT"],
    )
    confirm_url = url_for("auth.confirm_email", token=token, _external=True)
    html = render_template("activate.html", confirm_url=confirm_url)
    subject = "Bitte bestätige dein Konto"
    send_email(current_user.email, subject, html)

    flash("Eine neue Bestätigungsmail wurde gesendet.")
    return redirect(url_for("auth.unconfirmed_member"))


# Company
@auth.route("/company/login", methods=["GET", "POST"])
@commit_changes
def login_company():
    login_form = LoginForm(request.form)
    if request.method == "POST" and login_form.validate():
        email = login_form.data["email"]
        password = login_form.data["password"]
        remember = True if login_form.data["remember"] else False

        company = database.get_company_by_mail(email)
        if not company:
            login_form.email.errors.append("Emailadresse nicht korrekt")
        elif not check_password_hash(company.password, password):
            login_form.password.errors.append("Passwort nicht korrekt")
        else:
            session["user_type"] = "company"
            login_user(company, remember=remember)
            return redirect(url_for("main_company.profile"))

    if current_user.is_authenticated:
        if session.get("user_type") == "company":
            return redirect(url_for("main_company.profile"))
        else:
            session["user_type"] = None
            logout_user()

    return render_template("login_company.html", form=login_form)


@auth.route("/company/signup", methods=["GET", "POST"])
@commit_changes
@with_injection
def signup_company(register_company: RegisterCompany):
    register_form = RegisterForm(request.form)
    if request.method == "POST" and register_form.validate():
        email = register_form.data["email"]
        name = register_form.data["name"]
        password = register_form.data["password"]
        try:
            register_company(email, name, password)
            return redirect(url_for("auth.login_company"))
        except CompanyAlreadyExists:
            register_form.email.errors.append("Emailadresse existiert bereits")

    return render_template("signup_company.html", form=register_form)


# logout
@auth.route("/zurueck")
def zurueck():
    session["user_type"] = None
    logout_user()
    return redirect(url_for("auth.start"))


@auth.route("/logout")
@login_required
def logout():
    session["user_type"] = None
    logout_user()
    return redirect(url_for("auth.start"))
