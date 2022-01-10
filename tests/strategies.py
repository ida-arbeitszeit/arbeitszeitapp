from hypothesis import strategies

from arbeitszeit.user_action import UserAction, UserActionType

from .user_action import FakeUserAction


@strategies.composite
def user_actions(draw) -> UserAction:
    action_type = draw(strategies.sampled_from(UserActionType))
    reference = draw(strategies.uuids())
    return FakeUserAction(action_type=action_type, reference=reference)
