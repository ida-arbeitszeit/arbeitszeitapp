from uuid import uuid4

from arbeitszeit_flask.database.repositories import DatabaseGatewayImpl
from tests.data_generators import CompanyGenerator, MemberGenerator

from ..flask import FlaskTestCase


class CooperationResultTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.db_gateway = self.injector.get(DatabaseGatewayImpl)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.member_generator = self.injector.get(MemberGenerator)

    def test_that_there_are_no_invites_in_database_by_default(self) -> None:
        assert not self.db_gateway.get_company_work_invites()

    def test_that_there_is_at_least_on_invite_in_db_after_creating_one(self) -> None:
        company = self.company_generator.create_company()
        member = self.member_generator.create_member()
        self.db_gateway.create_company_work_invite(company=company, member=member)
        assert self.db_gateway.get_company_work_invites()

    def test_that_created_invite_has_specified_member_as_its_attribute(self) -> None:
        member = self.member_generator.create_member()
        invite = self.db_gateway.create_company_work_invite(
            company=self.company_generator.create_company(), member=member
        )
        assert invite.member == member

    def test_that_created_invite_has_specified_company_as_its_attribute(self) -> None:
        company = self.company_generator.create_company()
        invite = self.db_gateway.create_company_work_invite(
            company=company, member=self.member_generator.create_member()
        )
        assert invite.company == company

    def test_that_invite_returned_by_create_method_and_querying_are_equal(self) -> None:
        invite_from_create = self.db_gateway.create_company_work_invite(
            company=self.company_generator.create_company(),
            member=self.member_generator.create_member(),
        )
        invite_from_query = self.db_gateway.get_company_work_invites().first()
        assert invite_from_create == invite_from_query

    def test_that_invites_can_be_filtered_by_their_id(self) -> None:
        invite = self.db_gateway.create_company_work_invite(
            company=self.company_generator.create_company(),
            member=self.member_generator.create_member(),
        )
        assert self.db_gateway.get_company_work_invites().with_id(invite.id)
        assert not self.db_gateway.get_company_work_invites().with_id(uuid4())

    def test_that_invites_can_be_filtered_by_issuing_company(self) -> None:
        issuer = self.company_generator.create_company()
        other_company = self.company_generator.create_company()
        self.db_gateway.create_company_work_invite(
            company=issuer,
            member=self.member_generator.create_member(),
        )
        assert self.db_gateway.get_company_work_invites().issued_by(issuer)
        assert not self.db_gateway.get_company_work_invites().issued_by(other_company)

    def test_invites_can_be_filtered_by_addressed_member(self) -> None:
        member = self.member_generator.create_member()
        other_member = self.member_generator.create_member()
        self.db_gateway.create_company_work_invite(
            member=member,
            company=self.company_generator.create_company(),
        )
        assert self.db_gateway.get_company_work_invites().addressing(member)
        assert not self.db_gateway.get_company_work_invites().addressing(other_member)

    def test_that_after_deleting_all_invites_future_queried_yield_no_results(
        self,
    ) -> None:
        self.db_gateway.create_company_work_invite(
            company=self.company_generator.create_company(),
            member=self.member_generator.create_member(),
        )
        self.db_gateway.get_company_work_invites().delete()
        assert not self.db_gateway.get_company_work_invites()

    def test_deleting_invites_in_filtered_query_leaves_other_invites_in_db(
        self,
    ) -> None:
        other_invite = self.db_gateway.create_company_work_invite(
            company=self.company_generator.create_company(),
            member=self.member_generator.create_member(),
        )
        invite_to_delete = self.db_gateway.create_company_work_invite(
            company=self.company_generator.create_company(),
            member=self.member_generator.create_member(),
        )
        self.db_gateway.get_company_work_invites().with_id(invite_to_delete.id).delete()
        assert self.db_gateway.get_company_work_invites().with_id(other_invite.id)
