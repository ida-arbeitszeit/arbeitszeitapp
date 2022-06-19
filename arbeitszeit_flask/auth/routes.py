from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required

from arbeitszeit.use_cases import ResendConfirmationMail, ResendConfirmationMailRequest
from arbeitszeit.use_cases.log_in_company import LogInCompanyUseCase
from arbeitszeit.use_cases.log_in_member import LogInMemberUseCase
from arbeitszeit_flask import database
from arbeitszeit_flask.database import commit_changes
from arbeitszeit_flask.dependency_injection import (
    CompanyModule,
    MemberModule,
    with_injection,
)
from arbeitszeit_flask.flask_session import FlaskSession
from arbeitszeit_flask.forms import LoginForm
from arbeitszeit_flask.next_url import save_next_url_in_session
from arbeitszeit_flask.template import AnonymousUserTemplateRenderer
from arbeitszeit_flask.token import FlaskTokenService
from arbeitszeit_flask.views.signup_accountant_view import SignupAccountantView
from arbeitszeit_flask.views.signup_company_view import SignupCompanyView
from arbeitszeit_flask.views.signup_member_view import SignupMemberView
from arbeitszeit_web.presenters.log_in_company_presenter import LogInCompanyPresenter
from arbeitszeit_web.presenters.log_in_member_presenter import LogInMemberPresenter

auth = Blueprint("auth", __name__, template_folder="templates", static_folder="static")


@auth.route("/")
@with_injection()
def start(template_renderer: AnonymousUserTemplateRenderer):
    save_next_url_in_session(request)
    return template_renderer.render_template("auth/start.html")


@auth.route("/help")
@with_injection()
def help(template_renderer: AnonymousUserTemplateRenderer):
    return template_renderer.render_template("auth/start_hilfe.html")


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
    def redirect_invalid_request():
        flash("Der Bestätigungslink ist ungültig oder ist abgelaufen.")
        return redirect(url_for("auth.unconfirmed_member"))

    token_service = FlaskTokenService()
    try:
        email = token_service.confirm_token(token)
    except Exception:
        return redirect_invalid_request()
    if email is None:
        return redirect_invalid_request()
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
def login_member(
    flask_session: FlaskSession,
    presenter: LogInMemberPresenter,
    use_case: LogInMemberUseCase,
):
    login_form = LoginForm(request.form)
    if request.method == "POST" and login_form.validate():
        email = login_form.data["email"]
        password = login_form.data["password"]
        response = use_case.log_in_member(
            LogInMemberUseCase.Request(
                email=email,
                password=password,
            )
        )
        view_model = presenter.present_login_process(response, login_form)
        if view_model.redirect_url:
            return redirect(view_model.redirect_url)
        else:
            render_template("auth/login_member.html", form=login_form)

    if current_user.is_authenticated:
        if flask_session.is_logged_in_as_member():
            return redirect(url_for("main_member.dashboard"))
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
def login_company(
    flask_session: FlaskSession,
    log_in_use_case: LogInCompanyUseCase,
    log_in_presenter: LogInCompanyPresenter,
):
    login_form = LoginForm(request.form)
    if request.method == "POST" and login_form.validate():
        email = login_form.data["email"]
        password = login_form.data["password"]

        use_case_request = LogInCompanyUseCase.Request(
            email_address=email,
            password=password,
        )
        use_case_response = log_in_use_case.log_in_company(use_case_request)
        view_model = log_in_presenter.present_login_process(
            response=use_case_response,
            form=login_form,
        )
        if view_model.redirect_url:
            return redirect(view_model.redirect_url)
        return render_template("auth/login_company.html", form=login_form)

    if current_user.is_authenticated:
        if flask_session.is_logged_in_as_company():
            return redirect(url_for("main_company.dashboard"))
        else:
            flask_session.logout()

    return render_template("auth/login_company.html", form=login_form)


@auth.route("/company/signup", methods=["GET", "POST"])
@commit_changes
@with_injection(modules=[CompanyModule()])
def signup_company(view: SignupCompanyView):
    return view.handle_request(request)


@auth.route("/company/confirm/<token>")
@commit_changes
def confirm_email_company(token):
    def redirect_invalid_request():
        flash("Der Bestätigungslink ist ungültig oder ist abgelaufen.")
        return redirect(url_for("auth.unconfirmed_company"))

    token_service = FlaskTokenService()
    try:
        email = token_service.confirm_token(token)
    except Exception:
        return redirect_invalid_request()
    if email is None:
        return redirect_invalid_request()
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


@auth.route("/accountant/signup/<token>", methods=["GET", "POST"])
@commit_changes
@with_injection()
def signup_accountant(token: str, view: SignupAccountantView):
    return view.handle_request(token)


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
