from __future__ import annotations

import pytest

pytestmark = pytest.mark.skip(reason="Integration test requires running Postgres and external services")


def test_placeholder():
    assert True
