"""Pytest conftest"""
import pytest


def pytest_addoption(parser):
    """Pass in the --update from command arguments"""
    parser.addoption(
        "--update", action="store_true", help="Update the expected output"
    )


@pytest.fixture
def update_flag(request):
    """pytest fixture to get the --update flag from command line"""
    return request.config.option.update
