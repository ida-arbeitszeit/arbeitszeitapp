from datetime import datetime
from typing import Protocol

class Clock(Protocol):
    def utc_now(self) -> datetime: ...

class SystemClock:
    def utc_now(self) -> datetime: ...
