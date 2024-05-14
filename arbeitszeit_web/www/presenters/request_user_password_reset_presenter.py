from dataclasses import dataclass

from arbeitszeit.use_cases import request_user_password_reset as use_case

class RequestUserPasswordResetViewModel:
    # @TODO: Does this need to be implemented?
    pass

@dataclass
class RequestUserPasswordResetPresenter:

    def render_response(self, response: use_case.Response) -> RequestUserPasswordResetViewModel:

        raise NotImplemented("not impled")