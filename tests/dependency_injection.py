from arbeitszeit.control_thresholds import ControlThresholds
from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.injector import AliasProvider, Binder, Module
from arbeitszeit_web.colors import Colors
from arbeitszeit_web.plotter import Plotter
from arbeitszeit_web.request import Request
from arbeitszeit_web.text_renderer import TextRenderer
from arbeitszeit_web.translator import Translator
from tests.control_thresholds import ControlThresholdsTestImpl
from tests.datetime_service import FakeDatetimeService
from tests.plotter import FakePlotter
from tests.request import FakeRequest
from tests.text_renderer import TextRendererImpl
from tests.translator import FakeTranslator
from tests.www.presenters.test_colors import ColorsTestImpl


class TestingModule(Module):
    def configure(self, binder: Binder) -> None:
        super().configure(binder)
        binder[TextRenderer] = AliasProvider(TextRendererImpl)
        binder[Colors] = AliasProvider(ColorsTestImpl)
        binder[Plotter] = AliasProvider(FakePlotter)
        binder[ControlThresholds] = AliasProvider(ControlThresholdsTestImpl)
        binder[Translator] = AliasProvider(FakeTranslator)
        binder[DatetimeService] = AliasProvider(FakeDatetimeService)
        binder[Request] = AliasProvider(FakeRequest)
