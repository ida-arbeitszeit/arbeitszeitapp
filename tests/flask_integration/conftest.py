import warnings

from pytest import fixture


@fixture(autouse=True)
def install_warning_filters():
    warnings.filterwarnings(
        "ignore",
        message=r"Dialect sqlite\+pysqlite does \*not\* support Decimal objects natively, and SQLAlchemy must convert from floating point - rounding errors and other issues may occur",
    )
    yield
    warnings.resetwarnings()
