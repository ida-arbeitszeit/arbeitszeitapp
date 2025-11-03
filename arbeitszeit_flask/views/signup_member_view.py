from dataclasses import dataclass

import flask
from flask import redirect, render_template, request, url_for

from arbeitszeit.interactors.register_member import RegisterMemberInteractor
from arbeitszeit_db import commit_changes
from arbeitszeit_flask.flask_session import FlaskSession
from arbeitszeit_flask.forms import RegisterForm
from arbeitszeit_flask.types import Response
from arbeitszeit_web.www.controllers.register_member_controller import (
    RegisterMemberController,
)
from arbeitszeit_web.www.presenters.register_member_presenter import (
    RegisterMemberPresenter,
)


@dataclass
class SignupMemberView:
    register_member: RegisterMemberInteractor
    controller: RegisterMemberController
    register_member_presenter: RegisterMemberPresenter
    flask_session: FlaskSession

    def GET(self):
        if self.flask_session.is_current_user_authenticated():
            if self.flask_session.is_logged_in_as_member():
                return redirect(url_for("main_member.dashboard"))
            else:
                self.flask_session.logout()
        register_form = RegisterForm(request.form)
        return render_template("auth/signup_member.html", form=register_form)

    @commit_changes
    def POST(self) -> Response:
        register_form = RegisterForm(request.form)
        if register_form.validate():
            return self._handle_valid_post_request(register_form=register_form)
        elif self.flask_session.is_current_user_authenticated():
            if self.flask_session.is_logged_in_as_member():
                return redirect(url_for("main_member.dashboard"))
            else:
                self.flask_session.logout()
        return flask.Response(
            render_template("auth/signup_member.html", form=register_form), 400
        )

    def _handle_valid_post_request(self, register_form: RegisterForm):
        interactor_request = self.controller.create_request(register_form)
        response = self.register_member.register_member(interactor_request)
        view_model = self.register_member_presenter.present_member_registration(
            response, register_form
        )
        if view_model.redirect_to:
            return redirect(view_model.redirect_to)
        else:
            return render_template("auth/signup_member.html", form=register_form)
