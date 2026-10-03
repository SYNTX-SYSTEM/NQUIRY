import time

import pytest


@pytest.mark.parametrize("i", range(400))
def test_slow(i: int) -> None:
    time.sleep(0.03)
