from arbeitszeit.control_thresholds import ControlThresholds
from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.injector import AliasProvider, Binder, Module
from arbeitszeit.presenters import (
    AccountantInvitationPresenter,
    CompanyRegistrationMessagePresenter,
    MemberRegistrationMessagePresenter,
)
from arbeitszeit_web.colors import Colors
from arbeitszeit_web.email import UserAddressBook
from arbeitszeit_web.plotter import Plotter
from arbeitszeit_web.request import Request
from arbeitszeit_web.text_renderer import TextRenderer
from arbeitszeit_web.translator import Translator
from tests.accountant_invitation_presenter import AccountantInvitationPresenterTestImpl
from tests.control_thresholds import ControlThresholdsTestImpl
from tests.datetime_service import FakeDatetimeService
from tests.email import FakeAddressBook
from tests.plotter import FakePlotter
from tests.request import FakeRequest
from tests.text_renderer import TextRendererImpl
from tests.token import TokenDeliveryService
from tests.translator import FakeTranslator
from tests.www.presenters.test_colors import ColorsTestImpl


class TestingModule(Module):
    def configure(self, binder: Binder) -> None:
        super().configure(binder)
        binder[CompanyRegistrationMessagePresenter] = AliasProvider(  # type: ignore
            TokenDeliveryService
        )
        binder[MemberRegistrationMessagePresenter] = AliasProvider(  # type: ignore
            TokenDeliveryService
        )
        binder[TextRenderer] = AliasProvider(TextRendererImpl)  # type: ignore
        binder[Colors] = AliasProvider(ColorsTestImpl)  # type: ignore
        binder[Plotter] = AliasProvider(FakePlotter)  # type: ignore
        binder[ControlThresholds] = AliasProvider(  # type: ignore
            ControlThresholdsTestImpl
        )
        binder[Translator] = AliasProvider(FakeTranslator)  # type: ignore
        binder[AccountantInvitationPresenter] = AliasProvider(  # type: ignore
            AccountantInvitationPresenterTestImpl
        )
        binder[DatetimeService] = AliasProvider(FakeDatetimeService)  # type: ignore
        binder[UserAddressBook] = AliasProvider(FakeAddressBook)  # type: ignore
        binder[Request] = AliasProvider(FakeRequest)  # type: ignore
