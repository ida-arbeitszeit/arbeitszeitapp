from dataclasses import dataclass
from typing import List

from arbeitszeit.use_cases.get_member_profile_info import GetMemberProfileInfoResponse
from arbeitszeit_web.translator import Translator


@dataclass
class Workplace:
    name: str
    email: str


@dataclass
class GetMemberProfileInfoViewModel:
    member_id: str
    account_balance: str
    email: str
    workplaces: List[Workplace]
    show_workplaces: bool
    show_workplace_registration_info: bool
    welcome_message: str


@dataclass
class GetMemberProfileInfoPresenter:
    translator: Translator

    def present(
        self, use_case_response: GetMemberProfileInfoResponse
    ) -> GetMemberProfileInfoViewModel:
        return GetMemberProfileInfoViewModel(
            member_id=str(use_case_response.id),
            account_balance=self.translator.gettext(
                "%(num).2f hours" % dict(num=use_case_response.account_balance)
            ),
            email=use_case_response.email,
            workplaces=[
                Workplace(
                    name=workplace.workplace_name,
                    email=workplace.workplace_email,
                )
                for workplace in use_case_response.workplaces
            ],
            show_workplaces=bool(use_case_response.workplaces),
            show_workplace_registration_info=not bool(use_case_response.workplaces),
            welcome_message=self.translator.gettext(
                "Welcome, %s!" % use_case_response.name
            ),
        )
