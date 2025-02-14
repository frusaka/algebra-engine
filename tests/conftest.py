import processing
import pytest


@pytest.fixture
def processor():
    return processing.Interpreter()


@pytest.fixture
def AST():
    return processing.AST
