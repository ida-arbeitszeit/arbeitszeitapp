from uuid import UUID

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required

from arbeitszeit.use_cases.confirm_company import ConfirmCompanyUseCase
from arbeitszeit.use_cases.confirm_member import ConfirmMemberUseCase
from arbeitszeit.use_cases.log_in_accountant import LogInAccountantUseCase
from arbeitszeit.use_cases.log_in_company import LogInCompanyUseCase
from arbeitszeit.use_cases.log_in_member import LogInMemberUseCase
from arbeitszeit.use_cases.resend_confirmation_mail import ResendConfirmationMailUseCase
from arbeitszeit.use_cases.start_page import StartPageUseCase
from arbeitszeit_flask.database import commit_changes
from arbeitszeit_flask.database.repositories import CompanyRepository, MemberRepository
from arbeitszeit_flask.dependency_injection import (
    CompanyModule,
    MemberModule,
    with_injection,
)
from arbeitszeit_flask.flask_session import FlaskSession
from arbeitszeit_flask.forms import LoginForm
from arbeitszeit_flask.template import AnonymousUserTemplateRenderer
from arbeitszeit_flask.types import Response
from arbeitszeit_flask.views.signup_accountant_view import SignupAccountantView
from arbeitszeit_flask.views.signup_company_view import SignupCompanyView
from arbeitszeit_flask.views.signup_member_view import SignupMemberView
from arbeitszeit_web.controllers.log_in_accountant_controller import (
    LogInAccountantController,
)
from arbeitszeit_web.presenters.log_in_accountant_presenter import (
    LogInAccountantPresenter,
)
from arbeitszeit_web.presenters.log_in_company_presenter import LogInCompanyPresenter
from arbeitszeit_web.presenters.log_in_member_presenter import LogInMemberPresenter
from arbeitszeit_web.presenters.start_page_presenter import StartPagePresenter

auth = Blueprint("auth", __name__, template_folder="templates", static_folder="static")


@auth.route("/")
@with_injection()
def start(
    template_renderer: AnonymousUserTemplateRenderer,
    start_page: StartPageUseCase,
    start_page_presenter: StartPagePresenter,
):
    response = start_page.show_start_page()
    view_model = start_page_presenter.show_start_page(response)
    return template_renderer.render_template(
        "auth/start.html", context=dict(view_model=view_model)
    )


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
@with_injection()
@login_required
def unconfirmed_member(member_repository: MemberRepository):
    if (
        member_repository.get_members()
        .with_id(UUID(current_user.id))
        .that_are_confirmed()
    ):
        return redirect(url_for("auth.start"))
    return render_template("auth/unconfirmed_member.html")


@auth.route("/member/signup", methods=["GET", "POST"])
@with_injection(modules=[MemberModule()])
@commit_changes
def signup_member(view: SignupMemberView):
    return view.handle_request()


@auth.route("/member/confirm/<token>")
@commit_changes
@with_injection()
def confirm_email_member(token: str, use_case: ConfirmMemberUseCase) -> Response:
    response = use_case.confirm_member(request=use_case.Request(token=token))
    if not response.is_confirmed:
        flash("Der Bestätigungslink ist ungültig oder ist abgelaufen.")
        return redirect(url_for("auth.unconfirmed_member"))
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
def resend_confirmation_member(use_case: ResendConfirmationMailUseCase):
    assert (
        current_user.user.email
    )  # current user object must have email because it is logged in

    request = use_case.Request(user=UUID(current_user.id))
    response = use_case.resend_confirmation_mail(request)
    if response.is_token_sent:
        flash("Eine neue Bestätigungsmail wurde gesendet.")
    else:
        flash("Bestätigungsmail konnte nicht gesendet werden!")
    return redirect(url_for("auth.unconfirmed_member"))


# Company
@auth.route("/company/unconfirmed")
@with_injection()
@login_required
def unconfirmed_company(company_repository: CompanyRepository):
    if company_repository.is_company_confirmed(UUID(current_user.id)):
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
@with_injection()
def confirm_email_company(
    token, confirm_company_use_case: ConfirmCompanyUseCase, session: FlaskSession
):
    request = ConfirmCompanyUseCase.Request(token)
    response = confirm_company_use_case.confirm_company(request)
    if not response.is_confirmed:
        flash("Der Bestätigungslink ist ungültig oder ist abgelaufen.")
        return redirect(url_for("auth.unconfirmed_company"))
    else:
        assert response.user_id
        session.login_company(response.user_id)
        flash("Das Konto wurde bestätigt. Danke!")
        return redirect(url_for("auth.login_company"))


@auth.route("/company/resend")
@with_injection(modules=[CompanyModule()])
@login_required
def resend_confirmation_company(use_case: ResendConfirmationMailUseCase):
    assert (
        current_user.user.email
    )  # current user object must have email because it is logged in

    request = use_case.Request(user=UUID(current_user.id))
    response = use_case.resend_confirmation_mail(request)
    if response.is_token_sent:
        flash("Eine neue Bestätigungsmail wurde gesendet.")
    else:
        flash("Bestätigungsmail konnte nicht gesendet werden!")
    return redirect(url_for("auth.unconfirmed_company"))


@auth.route("/accountant/signup/<token>", methods=["GET", "POST"])
@commit_changes
@with_injection()
def signup_accountant(token: str, view: SignupAccountantView):
    return view.handle_request(token)


@auth.route("/accountant/login", methods=["GET", "POST"])
@commit_changes
@with_injection()
def login_accountant(
    controller: LogInAccountantController,
    use_case: LogInAccountantUseCase,
    presenter: LogInAccountantPresenter,
):
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        use_case_request = controller.process_login_form(form)
        use_case_response = use_case.log_in_accountant(use_case_request)
        view_model = presenter.present_login_process(
            form=form, response=use_case_response
        )
        if view_model.redirect_url is not None:
            return redirect(view_model.redirect_url)
    return render_template("auth/login_accountant.html", form=form)


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
