from inspect import signature

import pytest

from pluggie import validate

def func1(a, b, c=4, d=5):
    pass


def func2(a, c=3, d=2):
    pass


def func3(a, b, d=2):
    pass


@pytest.mark.parametrize("func", (func2, func3))
def test_missing_args_raises(func):
    with pytest.raises(validate.SignatureError):
        validate.signature_args(signature(func1), signature(func))
