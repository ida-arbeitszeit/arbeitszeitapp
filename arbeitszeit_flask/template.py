from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol

from flask import render_template
from injector import inject

from arbeitszeit.use_cases import CheckForUnreadMessages
from arbeitszeit.use_cases.list_available_languages import ListAvailableLanguagesUseCase
from arbeitszeit_web.check_for_unread_message import (
    CheckForUnreadMessagesController,
    CheckForUnreadMessagesPresenter,
)
from arbeitszeit_web.presenters.list_available_languages_presenter import (
    ListAvailableLanguagesPresenter,
)


class TemplateRenderer(Protocol):
    def render_template(
        self, name: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        ...


class TemplateIndex(Protocol):
    def get_template_by_name(self, name: str) -> str:
        ...


class MemberTemplateIndex:
    def get_template_by_name(self, name: str) -> str:
        return f"member/{name}.html"


class CompanyTemplateIndex:
    def get_template_by_name(self, name: str) -> str:
        return f"company/{name}.html"


class FlaskTemplateRenderer:
    _EMPTY_CONTEXT: Dict[str, Any] = dict()

    def render_template(
        self, name: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        return render_template(name, **(context or self._EMPTY_CONTEXT))


@dataclass
class AnonymousUserTemplateRenderer:
    inner_renderer: TemplateRenderer
    list_languages_use_case: ListAvailableLanguagesUseCase
    list_languages_presenter: ListAvailableLanguagesPresenter

    def render_template(
        self, name: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        if context is None:
            context = dict()
        use_case_request = self.list_languages_use_case.Request()
        use_case_response = self.list_languages_use_case.list_available_languages(
            use_case_request
        )
        view_model = self.list_languages_presenter.present_available_languages_list(
            use_case_response
        )
        context["languages"] = view_model
        return self.inner_renderer.render_template(name, context)


@inject
@dataclass
class UserTemplateRenderer:
    inner_renderer: TemplateRenderer
    check_unread_messages_use_case: CheckForUnreadMessages
    check_unread_messages_controller: CheckForUnreadMessagesController
    check_unread_messages_presenter: CheckForUnreadMessagesPresenter

    def render_template(
        self, name: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        enriched_context = self._add_message_indicator_to_context(context or dict())
        return self.inner_renderer.render_template(name, enriched_context)

    def _add_message_indicator_to_context(
        self, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        try:
            request = self.check_unread_messages_controller.create_use_case_request()
        except ValueError:
            view_model = self.check_unread_messages_presenter.anonymous_view_model()
        else:
            response = self.check_unread_messages_use_case(request)
            view_model = self.check_unread_messages_presenter.present(response)
        return dict(context, message_indicator=view_model)


@dataclass
class MemberRegistrationEmailTemplateImpl:
    def render_to_html(self, confirmation_url: str) -> str:
        return render_template("auth/activate.html", confirm_url=confirmation_url)
