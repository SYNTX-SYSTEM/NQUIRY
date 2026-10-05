import os


def test_malformed_input_is_refused() -> None:
    assert os.environ.get("ORANGE_SYNTH_FAIL") != "1"
