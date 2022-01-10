from .datetime_service import FakeDatetimeService


class FakeTokenService:
    def generate_token(self, input: str) -> str:
        timestamp = FakeDatetimeService().now().timestamp()
        return f"token_{timestamp}_{input}"

    def confirm_token(self, token: str, max_age_in_sec: int) -> str:
        prefix, timestamp, text = tuple(token.split("_", 2))
        now = FakeDatetimeService().now().timestamp()
        time_passed = now - float(timestamp)
        if (prefix == "token") and (time_passed < max_age_in_sec):
            return text
        else:
            raise Exception
