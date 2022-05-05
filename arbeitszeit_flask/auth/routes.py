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
from flask_login import current_user, login_required
from werkzeug.security import check_password_hash

from arbeitszeit.use_cases import (
    RegisterCompany,
    ResendConfirmationMail,
    ResendConfirmationMailRequest,
)
from arbeitszeit_flask import database
from arbeitszeit_flask.database import commit_changes
from arbeitszeit_flask.dependency_injection import (
    CompanyModule,
    MemberModule,
    with_injection,
)
from arbeitszeit_flask.flask_session import FlaskSession
from arbeitszeit_flask.forms import LoginForm, RegisterForm
from arbeitszeit_flask.next_url import (
    get_next_url_from_session,
    save_next_url_in_session,
)
from arbeitszeit_flask.token import FlaskTokenService
from arbeitszeit_flask.views.signup_member_view import SignupMemberView
from arbeitszeit_web.register_company import RegisterCompanyController

auth = Blueprint("auth", __name__, template_folder="templates", static_folder="static")


@auth.route("/")
def start():
    save_next_url_in_session(request)
    return render_template("auth/start.html", languages=current_app.config["LANGUAGES"])


@auth.route("/help")
def help():
    return render_template("auth/start_hilfe.html")


@auth.route("/language=<language>")
def set_language(language=None):
    session["language"] = language
    return redirect(url_for("auth.start"))


# Member
@auth.route("/member/unconfirmed")
@login_required
def unconfirmed_member():
    if current_user.confirmed_on is not None:
        return redirect(url_for("auth.start"))
    return render_template("auth/unconfirmed_member.html")


@auth.route("/member/signup", methods=["GET", "POST"])
@with_injection(modules=[MemberModule()])
@commit_changes
def signup_member(view: SignupMemberView):
    return view.handle_request()


@auth.route("/member/confirm/<token>")
@commit_changes
def confirm_email_member(token):
    try:
        token_service = FlaskTokenService()
        email = token_service.confirm_token(token)
    except Exception:
        flash("Der Bestätigungslink ist ungültig oder ist abgelaufen.")
        return redirect(url_for("auth.unconfirmed_member"))
    member = database.get_user_by_mail(email)
    if member.confirmed_on is not None:
        flash("Konto ist bereits bestätigt.")
    else:
        member.confirmed_on = datetime.now()
        flash("Das Konto wurde bestätigt. Danke!")
    return redirect(url_for("auth.login_member"))


@auth.route("/member/login", methods=["GET", "POST"])
@with_injection()
@commit_changes
def login_member(flask_session: FlaskSession):
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
            flask_session.login_member(email, remember=remember)
            next = get_next_url_from_session()
            return redirect(next or url_for("main_member.profile"))

    if current_user.is_authenticated:
        if flask_session.is_logged_in_as_member():
            return redirect(url_for("main_member.profile"))
        else:
            flask_session.logout()

    return render_template("auth/login_member.html", form=login_form)


@auth.route("/member/resend")
@with_injection(modules=[MemberModule()])
@login_required
def resend_confirmation_member(use_case: ResendConfirmationMail):
    assert (
        current_user.email
    )  # current user object must have email because it is logged in

    request = ResendConfirmationMailRequest(
        subject="Bitte bestätige dein Konto",
        recipient=current_user.email,
    )
    response = use_case(request)
    if response.is_rejected:
        flash("Bestätigungsmail konnte nicht gesendet werden!")
    else:
        flash("Eine neue Bestätigungsmail wurde gesendet.")

    return redirect(url_for("auth.unconfirmed_member"))


# Company
@auth.route("/company/unconfirmed")
@login_required
def unconfirmed_company():
    if current_user.confirmed_on is not None:
        return redirect(url_for("auth.start"))
    return render_template("auth/unconfirmed_company.html")


@auth.route("/company/login", methods=["GET", "POST"])
@with_injection()
@commit_changes
def login_company(flask_session: FlaskSession):
    login_form = LoginForm(request.form)
    if request.method == "POST" and login_form.validate():
        email = login_form.data["email"]
        password = login_form.data["password"]
        remember = True if login_form.data["remember"] else False

        company = database.get_company_by_mail(email)
        if not company:
            login_form.email.errors.append(
                "Emailadresse nicht korrekt. Bist du schon registriert?"
            )
        elif not check_password_hash(company.password, password):
            login_form.password.errors.append("Passwort nicht korrekt")
        else:
            flask_session.login_company(email, remember=remember)
            next = get_next_url_from_session()
            return redirect(next or url_for("main_company.profile"))

    if current_user.is_authenticated:
        if flask_session.is_logged_in_as_company():
            return redirect(url_for("main_company.profile"))
        else:
            flask_session.logout()

    return render_template("auth/login_company.html", form=login_form)


@auth.route("/company/signup", methods=["GET", "POST"])
@commit_changes
@with_injection(modules=[CompanyModule()])
def signup_company(
    register_company: RegisterCompany,
    controller: RegisterCompanyController,
    flask_session: FlaskSession,
):
    register_form = RegisterForm(request.form)
    if request.method == "POST" and register_form.validate():
        use_case_request = controller.create_request(
            register_form,
        )
        response = register_company(use_case_request)
        if response.is_rejected:
            if (
                response.rejection_reason
                == RegisterCompany.Response.RejectionReason.company_already_exists
            ):
                register_form.email.errors.append("Emailadresse existiert bereits")
                return render_template("auth/signup_company.html", form=register_form)

        email = register_form.data["email"]
        flask_session.login_company(email)
        return redirect(url_for("auth.unconfirmed_company"))

    if current_user.is_authenticated:
        if flask_session.is_logged_in_as_company():
            return redirect(url_for("main_company.profile"))
        else:
            flask_session.logout()

    return render_template("auth/signup_company.html", form=register_form)


@auth.route("/company/confirm/<token>")
@commit_changes
def confirm_email_company(token):
    try:
        token_service = FlaskTokenService()
        email = token_service.confirm_token(token)
    except Exception:
        flash("Der Bestätigungslink ist ungültig oder ist abgelaufen.")
        return redirect(url_for("auth.unconfirmed_company"))
    company = database.get_company_by_mail(email)
    if company.confirmed_on is not None:
        flash("Konto ist bereits bestätigt.")
    else:
        company.confirmed_on = datetime.now()
        flash("Das Konto wurde bestätigt. Danke!")
    return redirect(url_for("auth.login_company"))


@auth.route("/company/resend")
@with_injection(modules=[CompanyModule()])
@login_required
def resend_confirmation_company(use_case: ResendConfirmationMail):
    assert (
        current_user.email
    )  # current user object must have email because it is logged in

    request = ResendConfirmationMailRequest(
        subject="Bitte bestätige dein Konto",
        recipient=current_user.email,
    )
    response = use_case(request)
    if response.is_rejected:
        flash("Bestätigungsmail konnte nicht gesendet werden!")
    else:
        flash("Eine neue Bestätigungsmail wurde gesendet.")

    return redirect(url_for("auth.unconfirmed_company"))


# logout
@auth.route("/zurueck")
@with_injection()
def zurueck(flask_session: FlaskSession):
    flask_session.logout()
    return redirect(url_for("auth.start"))


@auth.route("/logout")
@with_injection()
@login_required
def logout(flask_session: FlaskSession):
    flask_session.logout()
    return redirect(url_for("auth.start"))
