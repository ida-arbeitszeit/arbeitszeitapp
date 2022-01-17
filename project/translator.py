from flask_babel import gettext

from arbeitszeit_web.translator import Translator


class FlaskTranslator(Translator):
    def trans_(self, text: str) -> str:
        return gettext(text)
