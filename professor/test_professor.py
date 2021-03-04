import os
import pytest

@pytest.fixture
def test_professor(route):
    '''Professor route require login'''
    rv = route('/professor')
    assert 1 == 1 