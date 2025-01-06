from processing import Interpreter
import pytest


@pytest.fixture
def interpreter():
    return Interpreter()
