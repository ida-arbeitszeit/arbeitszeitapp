import enum


@enum.unique
class UserAction(enum.Enum):
    answer_invite = 1
    answer_cooperation_request = 2
