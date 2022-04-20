from arbeitszeit_web.user_action import UserAction


class UserActionResolver:
    def resolve_user_action_reference(self, action: UserAction) -> str:
        return " ".join(
            [
                str(action.type),
                str(action.reference),
                "reference",
            ]
        )

    def resolve_user_action_name(self, action: UserAction) -> str:
        return " ".join(
            [
                str(action.type),
                str(action.reference),
                "name",
            ]
        )
