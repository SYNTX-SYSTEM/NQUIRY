import os

import pytest


@pytest.mark.parametrize("i", range(8))
def test_other(i: int) -> None:
    assert os.environ.get("ORANGE_SYNTH_FAIL") != "1"
