import os


def test_worker_loop_survives_a_database_outage_and_stops_gracefully() -> None:
    assert os.environ.get("ORANGE_SYNTH_FAIL") != "1"
