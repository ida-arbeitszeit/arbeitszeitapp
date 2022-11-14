from dataclasses import dataclass

from flask import redirect, render_template, request, url_for
from flask_login import current_user

from arbeitszeit.use_cases import RegisterMemberUseCase
from arbeitszeit_flask.database import MemberRepository
from arbeitszeit_flask.flask_session import FlaskSession
from arbeitszeit_flask.forms import RegisterForm
from arbeitszeit_web.presenters.register_member_presenter import RegisterMemberPresenter
from arbeitszeit_web.register_member import RegisterMemberController


@dataclass
class SignupMemberView:
    register_member: RegisterMemberUseCase
    member_repository: MemberRepository
    controller: RegisterMemberController
    register_member_presenter: RegisterMemberPresenter
    flask_session: FlaskSession

    def handle_request(self):
        register_form = RegisterForm(request.form)
        if request.method == "POST" and register_form.validate():
            return self._handle_valid_post_request(register_form=register_form)
        if current_user.is_authenticated:
            if self.flask_session.is_logged_in_as_member():
                return redirect(url_for("main_member.dashboard"))
            else:
                self.flask_session.logout()

        return render_template("auth/signup_member.html", form=register_form)

    def _handle_valid_post_request(self, register_form: RegisterForm):
        use_case_request = self.controller.create_request(register_form)
        response = self.register_member.register_member(use_case_request)
        view_model = self.register_member_presenter.present_member_registration(
            response, register_form
        )
        if view_model.is_success_view:
            return redirect(url_for("auth.unconfirmed_member"))
        else:
            return render_template("auth/signup_member.html", form=register_form)
