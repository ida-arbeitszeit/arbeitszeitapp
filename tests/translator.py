from arbeitszeit_web.translator import Translator


class FakeTranslator(Translator):
    def trans_(self, text: str) -> str:
        return text
