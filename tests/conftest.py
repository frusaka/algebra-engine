from processing import Interpreter
import pytest


@pytest.fixture
def processor():
    return Interpreter()
