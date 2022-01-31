from arbeitszeit.use_cases import ResendConfirmationMail, ResendConfirmationMailRequest

from .dependency_injection import injection_test

DEFAULT = dict(
    recipient="receiver@cp.org",
    subject="mail confirmation",
)


@injection_test
def test_that_resending_mail_is_possible(
    use_case: ResendConfirmationMail,
):
    request = ResendConfirmationMailRequest(**DEFAULT)
    response = use_case(request)
    assert not response.is_rejected
