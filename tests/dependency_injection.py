from arbeitszeit.control_thresholds import ControlThresholds
from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.email_notifications import EmailSender
from arbeitszeit.injector import AliasProvider, Binder, CallableProvider, Module
from arbeitszeit.password_hasher import PasswordHasher
from arbeitszeit_web.colors import Colors
from arbeitszeit_web.plotter import Plotter
from arbeitszeit_web.request import Request
from arbeitszeit_web.text_renderer import TextRenderer
from arbeitszeit_web.translator import Translator
from tests.control_thresholds import ControlThresholdsTestImpl
from tests.datetime_service import FakeDatetimeService
from tests.email_notifications import EmailSenderTestImpl
from tests.password_hasher import PasswordHasherImpl
from tests.plotter import FakePlotter
from tests.request import FakeRequest
from tests.text_renderer import TextRendererImpl
from tests.translator import FakeTranslator
from tests.www.presenters.test_colors import ColorsTestImpl


class TestingModule(Module):
    def configure(self, binder: Binder) -> None:
        super().configure(binder)
        binder[EmailSender] = AliasProvider(EmailSenderTestImpl)
        binder[TextRenderer] = AliasProvider(TextRendererImpl)
        binder[Colors] = AliasProvider(ColorsTestImpl)
        binder[Plotter] = AliasProvider(FakePlotter)
        binder[ControlThresholds] = AliasProvider(ControlThresholdsTestImpl)
        binder[Translator] = AliasProvider(FakeTranslator)
        binder[DatetimeService] = AliasProvider(FakeDatetimeService)
        binder[Request] = AliasProvider(FakeRequest)
        binder[FakeRequest] = CallableProvider(
            self.provide_fake_request, is_singleton=True
        )
        binder[PasswordHasher] = AliasProvider(PasswordHasherImpl)

    @classmethod
    def provide_fake_request(self) -> FakeRequest:
        return FakeRequest()
