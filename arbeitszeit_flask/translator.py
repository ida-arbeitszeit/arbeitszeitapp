from flask_babel import gettext, lazy_gettext, ngettext, pgettext

from arbeitszeit_web.translator import Number, Translator


class FlaskTranslator(Translator):
    def gettext(self, text: str) -> str:
        return gettext(text)

    def pgettext(self, context: str, text: str) -> str:
        return pgettext(context, text)

    def ngettext(self, singular: str, plural: str, n: Number) -> str:
        return ngettext(singular, plural, n)

    def lazy_gettext(self, text: str) -> str:
        return lazy_gettext(text)
