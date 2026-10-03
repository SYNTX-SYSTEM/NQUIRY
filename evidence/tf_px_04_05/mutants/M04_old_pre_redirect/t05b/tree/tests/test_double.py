import pytest
from pkg.mod import double


@pytest.mark.parametrize("x", range(8))
def test_double(x: int) -> None:
    assert double(x) == x + x
