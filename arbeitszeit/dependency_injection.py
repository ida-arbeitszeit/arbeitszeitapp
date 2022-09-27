from injector import Module, provider

from arbeitszeit.actors import GiroOffice
from arbeitszeit.giro_office import GiroOfficeImpl


class ArbeitszeitModule(Module):
    @provider
    def provide_giro_office(self, instance: GiroOfficeImpl) -> GiroOffice:
        return instance
