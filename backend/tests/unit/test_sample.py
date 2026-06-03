"""Sample unit test proving the unit layer is collected and runs (no I/O)."""


def test_unit_layer_runs() -> None:
    """Assert a trivial pure expression to confirm unit tests execute.

    Placeholder until real pure-logic units exist (e.g. ``Money`` in P0-MOD-05);
    it only proves the ``tests/unit`` layer is wired up and runs without I/O.
    """
    assert sum([1, 2, 3]) == 6
