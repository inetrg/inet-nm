"""
    Dummy conftest.py for inet_nm.

    If you don't know what this is for, just leave it empty.
    Read more about conftest.py under:
    - https://docs.pytest.org/en/stable/fixture.html
    - https://docs.pytest.org/en/stable/writing_plugins.html
"""

import pytest


def pytest_addoption(parser):
    parser.addoption("--cli-readme-mock", default=None)


@pytest.fixture()
def cli_readme_mock(request):
    return request.config.getoption("--cli-readme-mock")
