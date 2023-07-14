from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol

from flask import render_template

from arbeitszeit.use_cases.list_available_languages import ListAvailableLanguagesUseCase
from arbeitszeit_web.www.presenters.list_available_languages_presenter import (
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


class AccountantTemplateIndex:
    def get_template_by_name(self, name: str) -> str:
        return f"accountant/{name}.html"


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


@dataclass
class UserTemplateRenderer:
    inner_renderer: TemplateRenderer

    def render_template(
        self, name: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        return self.inner_renderer.render_template(name, context)
