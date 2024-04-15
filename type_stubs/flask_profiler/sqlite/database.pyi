import sqlite3

from _typeshed import Incomplete
from flask_profiler.entities import measurement_archive as interface

from .migrations import Migrations as Migrations
from .select_query import RecordResult as RecordResult

LOGGER: Incomplete

class Row(sqlite3.Row): ...

class Sqlite:
    sqlite_file: Incomplete
    connection: Incomplete
    cursor: Incomplete
    def __init__(self, sqlite_file: str) -> None: ...
    def create_database(self) -> None: ...
    def record_measurement(self, measurement: interface.Measurement) -> int: ...
    def get_records(self) -> RecordResult: ...
    def close_connection(self) -> None: ...
