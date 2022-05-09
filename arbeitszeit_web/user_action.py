from dataclasses import dataclass
from typing import Dict, Protocol

from arbeitszeit.user_action import UserAction, UserActionType
from arbeitszeit_web.translator import Translator

from .url_index import CoopSummaryUrlIndex, InviteUrlIndex


class UserActionResolver(Protocol):
    def resolve_user_action_reference(self, action: UserAction) -> str:
        ...

    def resolve_user_action_name(self, action: UserAction) -> str:
        ...


@dataclass
class UserActionResolverImpl:
    invite_url_index: InviteUrlIndex
    coop_url_index: CoopSummaryUrlIndex
    translator: Translator

    def resolve_user_action_name(self, action: UserAction) -> str:
        user_action_to_label: Dict[UserActionType, str] = {
            UserActionType.answer_invite: self.translator.gettext(
                "Accept or decline to join company"
            ),
            UserActionType.answer_cooperation_request: self.translator.gettext(
                "Accept or decline request for cooperation"
            ),
        }
        return user_action_to_label[action.type]

    def resolve_user_action_reference(self, action: UserAction) -> str:
        if action.type == UserActionType.answer_invite:
            return self.invite_url_index.get_invite_url(action.reference)
        return self.coop_url_index.get_coop_summary_url(action.reference)
