from dataclasses import dataclass

from flask import Response, render_template

from arbeitszeit_web.session import Session, UserRole


@dataclass
class Http404View:
    session: Session

    def get_response(self) -> Response:
        template = self._get_html_template_name()
        return Response(
            render_template(template),
            status=404,
        )

    def _get_html_template_name(self) -> str:
        user_role = self.session.get_user_role()
        assert user_role
        return _TEMPLATE_BY_USER_ROLE[user_role]


_TEMPLATE_BY_USER_ROLE = {
    UserRole.member: "member/404.html",
    UserRole.company: "company/404.html",
    UserRole.accountant: "accountant/404.html",
}
