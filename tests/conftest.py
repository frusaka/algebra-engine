import processing
import pytest


@pytest.fixture
def processor():
    return processing.Interpreter.instance()
