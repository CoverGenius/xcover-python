import pytest
from xcover import XCover


@pytest.fixture(scope="session")
def vcr_config():
    return {"filter_headers": ["authorization"]}


@pytest.fixture()
def client():
    yield XCover()
