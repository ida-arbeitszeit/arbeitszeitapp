from flask import Blueprint
from flask import Response as FlaskResponse
from flask import flash, redirect, render_template, request, session, url_for
from flask_login import login_required

from arbeitszeit.interactors.confirm_company import ConfirmCompanyInteractor
from arbeitszeit.interactors.confirm_member import ConfirmMemberInteractor
from arbeitszeit.interactors.log_in_accountant import LogInAccountantInteractor
from arbeitszeit.interactors.log_in_company import LogInCompanyInteractor
from arbeitszeit.interactors.log_in_member import LogInMemberInteractor
from arbeitszeit.interactors.resend_confirmation_mail import (
    ResendConfirmationMailInteractor,
)
from arbeitszeit.interactors.start_page import StartPageInteractor
from arbeitszeit_db import commit_changes
from arbeitszeit_flask.class_based_view import as_flask_view
from arbeitszeit_flask.dependency_injection import with_injection
from arbeitszeit_flask.flask_session import FlaskSession
from arbeitszeit_flask.forms import LoginForm
from arbeitszeit_flask.types import Response
from arbeitszeit_flask.views.signup_accountant_view import SignupAccountantView
from arbeitszeit_flask.views.signup_company_view import SignupCompanyView
from arbeitszeit_flask.views.signup_member_view import SignupMemberView
from arbeitszeit_web.www.authentication import CompanyAuthenticator, MemberAuthenticator
from arbeitszeit_web.www.controllers.confirm_company_controller import (
    ConfirmCompanyController,
)
from arbeitszeit_web.www.controllers.confirm_member_controller import (
    ConfirmMemberController,
)
from arbeitszeit_web.www.controllers.log_in_accountant_controller import (
    LogInAccountantController,
)
from arbeitszeit_web.www.presenters.log_in_accountant_presenter import (
    LogInAccountantPresenter,
)
from arbeitszeit_web.www.presenters.log_in_company_presenter import (
    LogInCompanyPresenter,
)
from arbeitszeit_web.www.presenters.log_in_member_presenter import LogInMemberPresenter
from arbeitszeit_web.www.presenters.start_page_presenter import StartPagePresenter

auth = Blueprint("auth", __name__)


@auth.route("/")
@with_injection()
def start(
    start_page: StartPageInteractor,
    start_page_presenter: StartPagePresenter,
):
    response = start_page.show_start_page()
    view_model = start_page_presenter.show_start_page(response)
    return render_template("auth/start.html", view_model=view_model)


@auth.route("/help")
@with_injection()
def help():
    return render_template("auth/help.html")


@auth.route("/language=<language>")
def set_language(language: str):
    redirection_url = request.headers.get("Referer") or url_for("auth.start")
    session["language"] = language
    return redirect(redirection_url)


@auth.route("/unconfirmed-member")
@with_injection()
@login_required
def unconfirmed_member(authenticator: MemberAuthenticator):
    if authenticator.is_unconfirmed_member():
        return render_template("auth/unconfirmed_member.html")
    return redirect(url_for("auth.start"))


@auth.route("/signup-member", methods=["GET", "POST"])
@as_flask_view()
class signup_member(SignupMemberView): ...


@auth.route("/confirm-member/<token>")
@commit_changes
@with_injection()
def confirm_email_member(
    token: str, interactor: ConfirmMemberInteractor, controller: ConfirmMemberController
) -> Response:
    interactor_request = controller.process_request(token)
    if interactor_request is not None:
        response = interactor.confirm_member(request=interactor_request)
        if response.is_confirmed:
            return redirect(url_for("auth.login_member"))
    flash("Der Bestätigungslink ist ungültig oder ist abgelaufen.")
    return redirect(url_for("auth.unconfirmed_member"))


@auth.route("/login-member", methods=["GET", "POST"])
@with_injection()
@commit_changes
def login_member(
    flask_session: FlaskSession,
    presenter: LogInMemberPresenter,
    interactor: LogInMemberInteractor,
):
    login_form = LoginForm(request.form)
    if request.method == "POST" and login_form.validate():
        email = login_form.data["email"]
        password = login_form.data["password"]
        response = interactor.log_in_member(
            LogInMemberInteractor.Request(
                email=email,
                password=password,
            )
        )
        view_model = presenter.present_login_process(response, login_form)
        if view_model.redirect_url:
            return redirect(view_model.redirect_url)
        else:
            return FlaskResponse(
                render_template("auth/login_member.html", form=login_form), status=401
            )

    if flask_session.is_current_user_authenticated():
        if flask_session.is_logged_in_as_member():
            return redirect(url_for("main_member.dashboard"))
        else:
            flask_session.logout()

    return render_template("auth/login_member.html", form=login_form)


@auth.route("/member/resend")
@with_injection()
@login_required
def resend_confirmation_member(
    interactor: ResendConfirmationMailInteractor,
    session: FlaskSession,
):
    current_user = session.get_current_user()
    assert current_user
    request = interactor.Request(user=current_user)
    response = interactor.resend_confirmation_mail(request)
    if response.is_token_sent:
        flash("Eine neue Bestätigungsmail wurde gesendet.")
    else:
        flash("Bestätigungsmail konnte nicht gesendet werden!")
    return redirect(url_for("auth.unconfirmed_member"))


@auth.route("/company/unconfirmed")
@with_injection()
@login_required
def unconfirmed_company(authenticator: CompanyAuthenticator):
    if authenticator.is_unconfirmed_company():
        return render_template("auth/unconfirmed_company.html")
    return redirect(url_for("auth.start"))


@auth.route("/company/login", methods=["GET", "POST"])
@with_injection()
@commit_changes
def login_company(
    flask_session: FlaskSession,
    log_in_interactor: LogInCompanyInteractor,
    log_in_presenter: LogInCompanyPresenter,
):
    login_form = LoginForm(request.form)
    if request.method == "POST" and login_form.validate():
        email = login_form.data["email"]
        password = login_form.data["password"]

        interactor_request = LogInCompanyInteractor.Request(
            email_address=email,
            password=password,
        )
        interactor_response = log_in_interactor.log_in_company(interactor_request)
        view_model = log_in_presenter.present_login_process(
            response=interactor_response,
            form=login_form,
        )
        if view_model.redirect_url:
            return redirect(view_model.redirect_url)
        return FlaskResponse(
            render_template("auth/login_company.html", form=login_form), status=401
        )

    if flask_session.is_current_user_authenticated():
        if flask_session.is_logged_in_as_company():
            return redirect(url_for("main_company.dashboard"))
        else:
            flask_session.logout()

    return render_template("auth/login_company.html", form=login_form)


@auth.route("/company/signup", methods=["GET", "POST"])
@as_flask_view()
class signup_company(SignupCompanyView): ...


@auth.route("/company/confirm/<token>")
@commit_changes
@with_injection()
def confirm_email_company(
    token,
    confirm_company_interactor: ConfirmCompanyInteractor,
    session: FlaskSession,
    controller: ConfirmCompanyController,
) -> Response:
    interactor_request = controller.process_request(token=token)
    if interactor_request:
        response = confirm_company_interactor.confirm_company(
            request=interactor_request
        )
        if response.is_confirmed:
            assert response.user_id
            session.login_company(response.user_id)
            flash("Das Konto wurde bestätigt. Danke!")
            return redirect(url_for("auth.login_company"))
    flash("Der Bestätigungslink ist ungültig oder ist abgelaufen.")
    return redirect(url_for("auth.unconfirmed_company"))


@auth.route("/company/resend")
@with_injection()
@login_required
def resend_confirmation_company(
    interactor: ResendConfirmationMailInteractor, flask_session: FlaskSession
):
    current_user = flask_session.get_current_user()
    assert current_user
    request = interactor.Request(user=current_user)
    response = interactor.resend_confirmation_mail(request)
    if response.is_token_sent:
        flash("Eine neue Bestätigungsmail wurde gesendet.")
    else:
        flash("Bestätigungsmail konnte nicht gesendet werden!")
    return redirect(url_for("auth.unconfirmed_company"))


@auth.route("/accountant/signup/<token>", methods=["GET", "POST"])
@as_flask_view()
class signup_accountant(SignupAccountantView): ...


@auth.route("/accountant/login", methods=["GET", "POST"])
@commit_changes
@with_injection()
def login_accountant(
    controller: LogInAccountantController,
    interactor: LogInAccountantInteractor,
    presenter: LogInAccountantPresenter,
):
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        interactor_request = controller.process_login_form(form)
        interactor_response = interactor.log_in_accountant(interactor_request)
        view_model = presenter.present_login_process(
            form=form, response=interactor_response
        )
        if view_model.redirect_url is not None:
            return redirect(view_model.redirect_url)
        return FlaskResponse(
            render_template("auth/login_accountant.html", form=form), status=401
        )
    return render_template("auth/login_accountant.html", form=form)


@auth.route("/logout")
@with_injection()
@login_required
def logout(flask_session: FlaskSession):
    flask_session.logout()
    return redirect(url_for("auth.start"))
