"""Smoke test: the harness package imports and exposes its version."""

import harness


def test_package_imports_with_version() -> None:
    # arrange / act
    version = harness.__version__

    # assert
    assert version == "0.1.0"
