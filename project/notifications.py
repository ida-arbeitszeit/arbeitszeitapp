from flask import flash


class FlaskFlashNotifier:
    def display_info(self, text: str) -> None:
        flash(text, "is-success")

    def display_warning(self, text: str) -> None:
        flash(text, "is-danger")
