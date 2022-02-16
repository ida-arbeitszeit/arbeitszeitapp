from flask_babel import gettext, lazy_gettext, pgettext

from arbeitszeit_web.translator import Translator


class FlaskTranslator(Translator):
    def gettext(self, text: str) -> str:
        return gettext(text)

    def pgettext(self, context: str, text: str) -> str:
        return pgettext(context, text)

    def lazy_gettext(self, text: str) -> str:
        return lazy_gettext(text)
