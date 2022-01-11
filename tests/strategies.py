from hypothesis import strategies

from arbeitszeit.user_action import UserAction, UserActionType


@strategies.composite
def user_actions(draw) -> UserAction:
    action_type = draw(strategies.sampled_from(UserActionType))
    reference = draw(strategies.uuids())
    return UserAction(type=action_type, reference=reference)
