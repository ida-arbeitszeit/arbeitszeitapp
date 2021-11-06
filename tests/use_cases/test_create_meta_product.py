from uuid import uuid4

from arbeitszeit.use_cases import CreateMetaProduct, CreateMetaProductRequest
from tests.data_generators import CompanyGenerator
from tests.use_cases.repositories import MetaProductRepository

from .dependency_injection import injection_test


@injection_test
def test_creation_unsuccessfull_when_coordinator_does_not_exist(
    create_product: CreateMetaProduct,
):
    request = CreateMetaProductRequest(
        coordinator_id=uuid4(), name="test name", definition="some info"
    )
    response = create_product(request)
    assert response is None


@injection_test
def test_creation_is_successfull(
    create_product: CreateMetaProduct,
    company_generator: CompanyGenerator,
):
    coordinator = company_generator.create_company()
    request = CreateMetaProductRequest(
        coordinator_id=coordinator.id, name="test name", definition="some info"
    )
    response = create_product(request)
    assert response


@injection_test
def test_creation_creates_a_meta_product_in_repository(
    create_product: CreateMetaProduct,
    company_generator: CompanyGenerator,
    meta_product_repository: MetaProductRepository,
):
    coordinator = company_generator.create_company()
    request = CreateMetaProductRequest(
        coordinator_id=coordinator.id, name="test name", definition="some info"
    )
    create_product(request)
    assert len(meta_product_repository) == 1
