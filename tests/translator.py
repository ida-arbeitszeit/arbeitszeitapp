from arbeitszeit_web.translator import Number, Translator


class FakeTranslator(Translator):
    def gettext(self, text: str) -> str:
        return text + " translated"

    def pgettext(self, context: str, text: str) -> str:
        return text + "translated"

    def ngettext(self, singular: str, plural: str, n: Number) -> str:
        if n == 1:
            return self.gettext(singular) % {"num": n}
        else:
            return self.gettext(plural) % {"num": n}
