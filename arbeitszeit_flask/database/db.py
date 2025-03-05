from typing import Optional

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, scoped_session, sessionmaker


class Database:
    _instance: Optional["Database"] = None
    _engine: Optional[Engine] = None
    _session: Optional[scoped_session] = None
    _uri: Optional[str] = None

    def __new__(cls) -> "Database":
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance

    def configure(self, uri: str) -> None:
        if self._uri == uri:
            # URI is already set to the same value
            pass
        elif self._uri is None:
            self._uri = uri
        else:
            raise ValueError("Database URI is already set to a different value.")

    @property
    def engine(self) -> Engine:
        if self._engine is None:
            if self._uri is None:
                raise ValueError("Database URI is not set.")
            self._engine = create_engine(self._uri)
        return self._engine

    @property
    def session(self) -> scoped_session:
        if self._session is None:
            engine = self.engine
            session_factory = sessionmaker(
                autocommit=False, autoflush=False, bind=engine
            )
            self._session = scoped_session(session_factory)
        return self._session


class Base(DeclarativeBase):
    pass
