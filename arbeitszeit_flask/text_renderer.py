from flask import render_template


class TextRendererImpl:
    def render_member_registration_message(self, *, confirmation_url: str) -> str:
        return render_template(
            "auth/activate.html",
            confirm_url=confirmation_url,
        )

    def render_company_registration_message(self, *, confirmation_url: str) -> str:
        return render_template(
            "auth/activate.html",
            confirm_url=confirmation_url,
        )
