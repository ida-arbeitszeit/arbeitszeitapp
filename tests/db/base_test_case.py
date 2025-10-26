from pathlib import Path
from typing import Any
from unittest import TestCase

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session, SessionTransaction, scoped_session, sessionmaker

from arbeitszeit.injector import Injector
from arbeitszeit_db.db import Base, Database
from arbeitszeit_db.repositories import DatabaseGatewayImpl
from tests import data_generators
from tests.datetime_service import FakeDatetimeService
from tests.db.dependency_injection import (
    DatabaseModule,
    provide_test_database_uri,
)
from tests.dependency_injection import TestingModule
from tests.lazy_property import _lazy_property
from tests.markers import database_required
from tests.www.datetime_formatter import FakeTimezoneConfiguration


@database_required
class TestCaseWithResettedDatabase(TestCase):
    _is_db_resetted = False

    def setUp(self):
        super().setUp()
        self.dependencies = [DatabaseModule()]
        self.injector = Injector(self.dependencies)
        self.db = self.injector.get(Database)
        self.reset_test_db_once_per_testrun()

    def reset_test_db_once_per_testrun(self) -> None:
        if not DatabaseTestCase._is_db_resetted:
            reset_test_db()
            DatabaseTestCase._is_db_resetted = True


class DatabaseTestCase(TestCaseWithResettedDatabase):
    def setUp(self) -> None:
        super().setUp()
        self._lazy_property_cache: dict[str, Any] = dict()
        self.dependencies.extend([TestingModule()])
        self.injector = Injector(self.dependencies)
        self.db = self.injector.get(Database)

        # Set up connection-level transaction for test isolation
        self.connection = self.db.engine.connect()
        self.transaction = self.connection.begin()

        # expire_on_commit=False prevents objects from expiring after flush
        session_factory = sessionmaker(bind=self.connection, expire_on_commit=False)
        self.test_session = scoped_session(session_factory)

        # This allows code that calls commit() to work properly in tests
        @event.listens_for(self.test_session, "after_transaction_end")
        def restart_savepoint(
            session: Session, transaction: SessionTransaction
        ) -> None:
            if transaction.nested and (
                not transaction._parent or not transaction._parent.nested
            ):
                session.begin_nested()

        self.test_session.begin_nested()
        self.db._session = self.test_session

    def tearDown(self) -> None:
        self._lazy_property_cache = dict()
        self.test_session.remove()
        self.transaction.rollback()
        self.connection.close()
        super().tearDown()

    accountant_generator = _lazy_property(data_generators.AccountantGenerator)
    company_generator = _lazy_property(data_generators.CompanyGenerator)
    consumption_generator = _lazy_property(data_generators.ConsumptionGenerator)
    cooperation_generator = _lazy_property(data_generators.CooperationGenerator)
    coordination_tenure_generator = _lazy_property(
        data_generators.CoordinationTenureGenerator
    )
    coordination_transfer_request_generator = _lazy_property(
        data_generators.CoordinationTransferRequestGenerator
    )
    database_gateway = _lazy_property(DatabaseGatewayImpl)
    datetime_service = _lazy_property(FakeDatetimeService)
    email_generator = _lazy_property(data_generators.EmailGenerator)
    member_generator = _lazy_property(data_generators.MemberGenerator)
    plan_generator = _lazy_property(data_generators.PlanGenerator)
    registered_hours_worked_generator = _lazy_property(
        data_generators.RegisteredHoursWorkedGenerator
    )
    timezone_configuration = _lazy_property(FakeTimezoneConfiguration)
    transfer_generator = _lazy_property(data_generators.TransferGenerator)
    worker_affiliation_generator = _lazy_property(
        data_generators.WorkerAffiliationGenerator
    )


def reset_test_db() -> None:
    engine = create_engine(provide_test_database_uri())
    dialect = engine.dialect.name
    if dialect == "postgresql":
        with engine.begin() as conn:
            conn.execute(text("DROP SCHEMA public CASCADE"))
            conn.execute(text("CREATE SCHEMA public"))
    elif dialect == "sqlite":
        path_string = engine.url.database
        assert path_string, "Expected a file path for SQLite database"
        path = Path(path_string)
        if path.exists():
            path.unlink()
    Base.metadata.create_all(bind=engine)
