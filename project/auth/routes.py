from datetime import datetime

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
from werkzeug.security import check_password_hash

from arbeitszeit.errors import CompanyAlreadyExists, MemberAlreadyExists
from arbeitszeit.use_cases import RegisterCompany, RegisterMember, SendExtMessage
from arbeitszeit_web.send_email import SendEmailController
from project import database
from project.database import MemberRepository, commit_changes
from project.dependency_injection import with_injection
from project.forms import LoginForm, RegisterForm
from project.next_url import get_next_url_from_session, save_next_url_in_session
from project.token import confirm_token, generate_confirmation_token

auth = Blueprint("auth", __name__, template_folder="templates", static_folder="static")


@auth.route("/")
def start():
    if "user_type" not in session:
        session["user_type"] = None
    save_next_url_in_session(request)
    return render_template("start.html")


@auth.route("/help")
def help():
    return render_template("start_hilfe.html")


@auth.route("/unconfirmed")
@login_required
def unconfirmed_user():
    if current_user.confirmed:
        return redirect(url_for("auth.start"))
    return render_template("unconfirmed.html")


# Member
@auth.route("/member/signup", methods=["GET", "POST"])
@with_injection
@commit_changes
def signup_member(
    register_member: RegisterMember,
    send_email_controller: SendEmailController,
    send_ext_message: SendExtMessage,
    member_repository: MemberRepository,
):
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
        member = member_repository.get_member_orm_by_mail(email)
        session["user_type"] = "member"
        login_user(member)

        # send confirmation mail
        subject = "Bitte bestätige dein Konto"
        token = generate_confirmation_token(member.email)
        confirm_url = url_for("auth.confirm_email", token=token, _external=True)
        html = render_template("activate.html", confirm_url=confirm_url)
        send_email_request = send_email_controller(
            sender_email=current_app.config["MAIL_DEFAULT_SENDER"],
            receiver_email=member.email,
            title=subject,
            content_html=html,
        )
        send_ext_message_response = send_ext_message(send_email_request)
        if send_ext_message_response.is_rejected:
            flash("Bestätigungsmail konnte nicht gesendet werden!")
        return redirect(url_for("auth.unconfirmed_user"))

    return render_template("signup_member.html", form=register_form)


@auth.route("/member/confirm/<token>")
@commit_changes
def confirm_email(token):
    try:
        email = confirm_token(token)
    except Exception:
        flash("Der Bestätigungslink ist ungültig oder ist abgelaufen.")
        return redirect(url_for("auth.unconfirmed_user"))
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
            next = get_next_url_from_session()
            return redirect(next or url_for("main_member.profile"))

    if current_user.is_authenticated:
        if session.get("user_type") == "member":
            return redirect(url_for("main_member.profile"))
        else:
            session["user_type"] = None
            logout_user()

    return render_template("login_member.html", form=login_form)


@auth.route("/resend")
@with_injection
@login_required
def resend_confirmation(
    send_email_controller: SendEmailController, send_ext_message: SendExtMessage
):
    assert (
        current_user.email
    )  # current user object must have email because it is logged in
    subject = "Bitte bestätige dein Konto"
    token = generate_confirmation_token(current_user.email)
    confirm_url = url_for("auth.confirm_email", token=token, _external=True)
    html = render_template("activate.html", confirm_url=confirm_url)
    send_email_request = send_email_controller(
        sender_email=current_app.config["MAIL_DEFAULT_SENDER"],
        receiver_email=current_user.email,
        title=subject,
        content_html=html,
    )
    send_ext_message_response = send_ext_message(send_email_request)
    if send_ext_message_response.is_rejected:
        flash("Bestätigungsmail konnte nicht gesendet werden!")
    else:
        flash("Eine neue Bestätigungsmail wurde gesendet.")
    return redirect(url_for("auth.unconfirmed_user"))


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
