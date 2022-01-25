import warnings

from pytest import fixture


@fixture(autouse=True)
def install_warning_filters():
    warnings.filterwarnings(
        "ignore",
        message=r"Dialect sqlite\+pysqlite does \*not\* support Decimal objects natively, and SQLAlchemy must convert from floating point - rounding errors and other issues may occur",
    )
    warnings.filterwarnings(
        "ignore",
        message=r"The 'autoescape' extension is deprecated and will be removed in Jinja 3.1",
    )
    warnings.filterwarnings(
        "ignore",
        message=r"The 'with' extension is deprecated and will be removed in Jinja 3.1",
    )
    yield
    warnings.resetwarnings()
