from dataclasses import dataclass

from arbeitszeit.use_cases.create_offer import CreateOfferResponse


@dataclass
class CreateOfferViewModel:
    name: str
    description: str


class CreateOfferPresenter:
    def present(self, use_case_response: CreateOfferResponse) -> CreateOfferViewModel:
        return CreateOfferViewModel(
            name=use_case_response.name,
            description=use_case_response.description,
        )
