from arbeitszeit_web.translator import Translator


class FakeTranslator(Translator):
    def gettext(self, text: str) -> str:
        return text + " translated"

    def pgettext(self, context: str, text: str) -> str:
        return text + "translated"
