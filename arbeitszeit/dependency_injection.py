from injector import Module, provider

from arbeitszeit.actors import GiroOffice, MemberRepository
from arbeitszeit.giro_office import GiroOfficeImpl
from arbeitszeit.member import MemberRepositoryImpl


class ArbeitszeitModule(Module):
    @provider
    def provide_giro_office(self, instance: GiroOfficeImpl) -> GiroOffice:
        return instance

    @provider
    def provide_member_repository(
        self, instance: MemberRepositoryImpl
    ) -> MemberRepository:
        return instance
