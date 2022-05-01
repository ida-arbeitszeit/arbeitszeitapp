from unittest import TestCase

from arbeitszeit.use_cases import ResendConfirmationMail, ResendConfirmationMailRequest

from .dependency_injection import get_dependency_injector

DEFAULT = dict(
    recipient="receiver@cp.org",
    subject="mail confirmation",
)


class UseCaseTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.use_case = self.injector.get(ResendConfirmationMail)

    def test_that_resending_mail_is_possible(self):
        request = ResendConfirmationMailRequest(**DEFAULT)
        response = self.use_case(request)
        assert not response.is_rejected
