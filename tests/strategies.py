from hypothesis import strategies

from arbeitszeit.user_action import UserAction


@strategies.composite
def user_actions(draw):
    return draw(strategies.sampled_from(UserAction))
