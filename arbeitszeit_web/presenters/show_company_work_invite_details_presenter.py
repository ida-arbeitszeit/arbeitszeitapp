from dataclasses import dataclass
from typing import Optional

from arbeitszeit.use_cases import ShowCompanyWorkInviteDetailsResponse
from arbeitszeit_web.url_index import AnswerCompanyWorkInviteUrlIndex


@dataclass
class ShowCompanyWorkInviteDetailsPresenter:
    @dataclass
    class ViewModel:
        answer_invite_url: str

    url_index: AnswerCompanyWorkInviteUrlIndex

    def render_response(
        self, response: ShowCompanyWorkInviteDetailsResponse
    ) -> Optional[ViewModel]:
        if (details := response.details) is not None:
            return self.ViewModel(
                answer_invite_url=self.url_index.get_answer_company_work_invite_url(
                    details.invite_id
                )
            )
        else:
            return None
