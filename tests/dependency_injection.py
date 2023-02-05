from arbeitszeit.control_thresholds import ControlThresholds
from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.injector import Binder, ClassProvider, Module
from arbeitszeit.token import (
    CompanyRegistrationMessagePresenter,
    MemberRegistrationMessagePresenter,
)
from arbeitszeit.use_cases.send_accountant_registration_token.accountant_invitation_presenter import (
    AccountantInvitationPresenter,
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
from tests.presenters.test_colors import ColorsTestImpl
from tests.request import FakeRequest
from tests.text_renderer import TextRendererImpl
from tests.token import TokenDeliveryService
from tests.translator import FakeTranslator


class TestingModule(Module):
    def configure(self, binder: Binder) -> None:
        super().configure(binder)
        binder[CompanyRegistrationMessagePresenter] = ClassProvider(  # type: ignore
            TokenDeliveryService
        )
        binder[MemberRegistrationMessagePresenter] = ClassProvider(  # type: ignore
            TokenDeliveryService
        )
        binder[TextRenderer] = ClassProvider(TextRendererImpl)  # type: ignore
        binder[Colors] = ClassProvider(ColorsTestImpl)  # type: ignore
        binder[Plotter] = ClassProvider(FakePlotter)  # type: ignore
        binder[ControlThresholds] = ClassProvider(  # type: ignore
            ControlThresholdsTestImpl
        )
        binder[Translator] = ClassProvider(FakeTranslator)  # type: ignore
        binder[AccountantInvitationPresenter] = ClassProvider(  # type: ignore
            AccountantInvitationPresenterTestImpl
        )
        binder[DatetimeService] = ClassProvider(FakeDatetimeService)  # type: ignore
        binder[UserAddressBook] = ClassProvider(FakeAddressBook)  # type: ignore
        binder[Request] = ClassProvider(FakeRequest)  # type: ignore
