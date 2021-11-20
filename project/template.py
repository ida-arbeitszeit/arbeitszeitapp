from dataclasses import dataclass
from typing import Any, Dict, Optional

from flask import render_template
from injector import inject

from arbeitszeit.use_cases import CheckForUnreadMessages
from arbeitszeit_web.check_for_unread_message import (
    CheckForUnreadMessagesController,
    CheckForUnreadMessagesPresenter,
)
from arbeitszeit_web.session import Session
from arbeitszeit_web.template import TemplateRenderer


class FlaskTemplateRenderer:
    _EMPTY_CONTEXT: Dict[str, Any] = dict()

    def render_template(
        self, name: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        return render_template(name, **(context or self._EMPTY_CONTEXT))


@inject
@dataclass
class UserTemplateRenderer:
    inner_renderer: TemplateRenderer
    session: Session
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
        user_id = self.session.get_current_user()
        if user_id is None:
            view_model = self.check_unread_messages_presenter.anonymous_view_model()
        else:
            request = self.check_unread_messages_controller.create_use_case_request(
                user_id
            )
            response = self.check_unread_messages_use_case(request)
            view_model = self.check_unread_messages_presenter.present(response)
        return dict(context, message_indicator=view_model)
